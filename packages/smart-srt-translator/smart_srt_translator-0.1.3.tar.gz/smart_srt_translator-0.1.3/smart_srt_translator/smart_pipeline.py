from __future__ import annotations

import os
import re
import json
import hashlib
import textwrap
from typing import List, Optional, Tuple
from pathlib import Path

from .srt_utils import parse_srt, format_srt
from .models import Segment
from .providers.base import TranslatorProvider
from .providers.dummy_provider import DummyTranslator


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _split_into_sentence_groups(texts: List[str], max_chars: int = 320) -> List[Tuple[int, int, str]]:
    groups: List[Tuple[int, int, str]] = []
    cur_start = 0
    cur_text: List[str] = []
    for i, t in enumerate(texts):
        t = _normalize_whitespace(t)
        if not t:
            # treat empty as boundary but include as its own group
            if cur_text:
                groups.append((cur_start, i - 1, _normalize_whitespace(" ".join(cur_text))))
                cur_text = []
            groups.append((i, i, ""))
            cur_start = i + 1
            continue
        cur_text.append(t)
        merged = " ".join(cur_text)
        if re.search(r"[\.!?][\)\]\"]?$", merged) or len(merged) >= max_chars:
            groups.append((cur_start, i, _normalize_whitespace(merged)))
            cur_start = i + 1
            cur_text = []
    if cur_text:
        groups.append((cur_start, len(texts) - 1, _normalize_whitespace(" ".join(cur_text))))
    return groups


def _wrap_two_lines(text: str, width: int = 42, min_tail_chars: int = 4) -> str:
    lines = textwrap.wrap(text, width=width)
    if len(lines) <= 1:
        return text
    if len(lines) == 2:
        # If the tail is too short (e.g., one short word), prefer single line
        if len(lines[-1].strip()) < min_tail_chars:
            return " ".join(lines)
        return "\n".join(lines)
    # If more than two lines, compress gently: join last lines
    first = lines[0]
    second = " ".join(lines[1:])
    if len(lines[-1].strip()) < min_tail_chars:
        # Try rebalance by slightly increasing width (best-effort)
        widened = textwrap.wrap(text, width=min(width + 5, 80))
        if len(widened) == 2 and len(widened[-1].strip()) >= min_tail_chars:
            return "\n".join(widened)
    return f"{first}\n{second}"


def _postprocess(text: str, tgt_lang: str) -> str:
    if tgt_lang.lower().startswith("de"):
        text = re.sub(r"\s+,", ",", text)
        text = re.sub(r"\s+\.", ".", text)
        text = re.sub(r"\s+(!|\?|:|;)", r"\1", text)
        text = re.sub(r"\s+\)\s*", ") ", text)
        text = re.sub(r"\s+\(", " (", text)
    return text.strip()


_EN_STOPS = {
    "the","a","an","and","or","but","so","to","of","in","on","for","with","as","is","are",
    "was","were","be","being","been","it","its","this","that","these","those","at","by","from",
    "you","your","yours","he","she","they","we","i","me","my","mine","his","her","their","our",
    "do","does","did","have","has","had","will","would","can","could","should","shall","may","might",
    "not","no","yes","only","just","there","here","what","why","how","when","where","which","who",
}


def _needs_review(text: str, tgt_lang: str, ascii_threshold: float, stop_threshold: float) -> bool:
    if not text:
        return False
    if tgt_lang.lower().startswith("de"):
        # Heuristic: too many pure ASCII words and English stopwords
        tokens = re.findall(r"[A-Za-z]{2,}", text)
        if not tokens:
            return False
        ascii_ratio = sum(1 for t in tokens if re.fullmatch(r"[A-Za-z]+", t)) / max(1, len(tokens))
        stop_ratio = sum(1 for t in tokens if t.lower() in _EN_STOPS) / max(1, len(tokens))
        return ascii_ratio > ascii_threshold and stop_ratio > stop_threshold
    return False


_MOVE_TAIL_TOKENS = {
    # German short/common tokens that are awkward as trailing singletons
    "und", "oder", "aber", "ich", "du", "er", "sie", "es", "wir", "ihr",
    "die", "der", "das", "den", "dem", "des", "ein", "eine", "einer", "einem", "eines",
    "zu", "mit", "auf", "für", "an", "im", "am", "vom", "beim", "als", "so", "dass", "weil",
}

_END_PUNCT = {".", "!", "?", "…"}


def _time_to_seconds(tc: str) -> float:
    try:
        hh, mm, ss_ms = tc.split(":")
        ss, ms = ss_ms.split(",")
        return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000.0
    except Exception:
        return 0.0


def _seconds_to_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        s += 1
        ms -= 1000
    if s >= 60:
        m += 1
        s -= 60
    if m >= 60:
        h += 1
        m -= 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _smooth_across_segments(segments: List[Segment], wrap_width: int, balance: bool = True, balance_ratio: float = 2.0) -> List[Segment]:
    out = [Segment(s.index, s.start, s.end, s.text) for s in segments]
    for i in range(len(out) - 1):
        cur = out[i]
        nxt = out[i + 1]
        # Do not push tokens into zero-length next segments
        if nxt.start == nxt.end:
            continue
        cur_words = cur.text.split()
        nxt_words = nxt.text.split()
        if not cur_words:
            continue
        # Protection: avoid moves across very short segments (duration or tiny token count)
        cur_dur_ms = int((_time_to_seconds(cur.end) - _time_to_seconds(cur.start)) * 1000)
        nxt_dur_ms = int((_time_to_seconds(nxt.end) - _time_to_seconds(nxt.start)) * 1000)
        PROTECT_MIN_DURATION_MS = 600
        PROTECT_MIN_TOKENS = 3
        WIDOW_MIN_TOKENS = 2
        cur_protected = (cur_dur_ms < PROTECT_MIN_DURATION_MS) or (len(cur_words) <= PROTECT_MIN_TOKENS)
        nxt_protected = (nxt_dur_ms < PROTECT_MIN_DURATION_MS) or (len(nxt_words) <= PROTECT_MIN_TOKENS)

        # Sticky punctuation: if next starts with a token ending in .!? and current does not end with punctuation, pull it back
        if nxt_words and (not cur_protected) and (not nxt_protected):
            head_tok = nxt_words[0]
            if head_tok and head_tok[-1] in _END_PUNCT and (not cur.text or cur.text[-1] not in _END_PUNCT):
                cur_words.append(head_tok)
                nxt_words = nxt_words[1:]
                cur.text = _wrap_two_lines(" ".join(cur_words), width=wrap_width)
                nxt.text = _wrap_two_lines(" ".join(nxt_words), width=wrap_width)
                cur_words = cur.text.split()
                nxt_words = nxt.text.split()

        # Do not move further if current ends with punctuation (sentence boundary)
        if cur.text and not cur.text[-1].isalnum():
            continue
        # Move a dangling short tail token
        if (not cur_protected) and (not nxt_protected) and len(cur_words) >= 3 and cur_words[-1].lower() in _MOVE_TAIL_TOKENS:
            token = cur_words.pop()
            nxt_words.insert(0, token)
            cur.text = _wrap_two_lines(" ".join(cur_words), width=wrap_width)
            nxt.text = _wrap_two_lines(" ".join(nxt_words), width=wrap_width)

        # Widow/orphan control: avoid too-short heads in next segment
        cur_words = cur.text.split()
        nxt_words = nxt.text.split()
        if (not cur_protected) and (not nxt_protected) and 0 < len(nxt_words) < WIDOW_MIN_TOKENS:
            tail = cur_words[-1] if cur_words else ""
            if tail and tail[-1].isalnum():
                cur_words = cur_words[:-1]
                nxt_words = [tail] + nxt_words
                cur.text = _wrap_two_lines(" ".join(cur_words), width=wrap_width)
                nxt.text = _wrap_two_lines(" ".join(nxt_words), width=wrap_width)

        # Optional simple length balancing: if one side is much shorter than the other, move a word
        if balance and nxt_words and (not cur_protected) and (not nxt_protected):
            # Recompute after potential move above
            cur_len = len(cur.text.strip())
            nxt_len = len(nxt.text.strip())
            if cur_len > 0 and nxt_len > 0:
                if cur_len * balance_ratio < nxt_len:
                    # Move one leading token from next to end of current, unless next starts with punctuation
                    head = nxt_words[0]
                    if head and head[0].isalnum():
                        cur_words = cur.text.split()
                        cur_words.append(head)
                        nxt_words = nxt_words[1:]
                        cur.text = _wrap_two_lines(" ".join(cur_words), width=wrap_width)
                        nxt.text = _wrap_two_lines(" ".join(nxt_words), width=wrap_width)
                elif nxt_len * balance_ratio < cur_len and len(cur_words) > 1:
                    # Move one trailing token from current to front of next
                    tail = cur_words[-1]
                    if tail and tail[-1].isalnum():
                        nxt_words = [tail] + nxt_words
                        cur_words = cur_words[:-1]
                        cur.text = _wrap_two_lines(" ".join(cur_words), width=wrap_width)
                        nxt.text = _wrap_two_lines(" ".join(nxt_words), width=wrap_width)
    return out


class JsonCache:
    def __init__(self, path: str):
        self.path = path
        self._data = {}  # type: ignore
        if os.path.exists(path):
            try:
                self._data = json.load(open(path, "r", encoding="utf-8"))
            except Exception:
                self._data = {}

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)


def _cache_key(provider: str, model: str, src: str, tgt: str, text: str) -> str:
    h = hashlib.sha256()
    h.update((provider + "\0" + model + "\0" + src + "\0" + tgt + "\0" + text).encode("utf-8"))
    return h.hexdigest()


def _distribute_translation_over_segments(segments: List[Segment], translated_full: str, wrap_width: int = 42) -> List[Segment]:
    """Distribute translated text over segments while preserving timing.

    - Excludes zero-length or empty-source segments from allocation (they remain empty).
    - Allocates targets proportional to source text length.
    - Distributes any leftover words round-robin across eligible segments (not just the last).
    """
    translated_full = _normalize_whitespace(translated_full)
    words = translated_full.split()

    # Determine eligible segments (non-empty, non zero-length)
    eligible_idx: List[int] = [
        i for i, s in enumerate(segments) if s.text.strip() and not (s.start == s.end)
    ]
    out: List[Segment] = [
        Segment(index=s.index, start=s.start, end=s.end, text="") for s in segments
    ]
    if not eligible_idx:
        return out

    src_total = sum(len(segments[i].text) for i in eligible_idx) or 1
    tgt_total = len(translated_full)
    # Initial char targets per eligible segment
    targets = [max(1, round(tgt_total * len(segments[i].text) / src_total)) for i in eligible_idx]
    diff = tgt_total - sum(targets)
    j = 0
    while diff != 0 and eligible_idx:
        step = 1 if diff > 0 else -1
        targets[j % len(targets)] += step
        diff -= step
        j += 1

    # Fill each eligible segment up to its target length using whole words
    widx = 0
    for pos, seg_i in enumerate(eligible_idx):
        cur_target = targets[pos]
        taken: List[str] = []
        cur_len = 0
        while widx < len(words) and (cur_len + len(words[widx]) + (1 if taken else 0)) <= cur_target:
            w = words[widx]
            taken.append(w)
            cur_len += len(w) + (1 if cur_len > 0 else 0)
            widx += 1
        out[seg_i] = Segment(
            index=segments[seg_i].index,
            start=segments[seg_i].start,
            end=segments[seg_i].end,
            text=_wrap_two_lines(" ".join(taken).strip(), width=wrap_width),
        )

    # Distribute any leftover words round-robin across eligible segments
    if widx < len(words):
        rr = 0
        cur_texts = [out[i].text for i in eligible_idx]
        while widx < len(words):
            seg_pos = eligible_idx[rr % len(eligible_idx)]
            cur = (cur_texts[rr % len(eligible_idx)] + " " + words[widx]).strip()
            cur = _wrap_two_lines(cur, width=wrap_width)
            cur_texts[rr % len(eligible_idx)] = cur
            out[seg_pos] = Segment(index=out[seg_pos].index, start=out[seg_pos].start, end=out[seg_pos].end, text=cur)
            widx += 1
            rr += 1
    return out


def translate_srt_smart(
    input_path: str,
    src_lang: str = "en",
    tgt_lang: str = "de",
    provider: Optional[TranslatorProvider] = None,
    keep_timing: bool = True,
    cache_path: Optional[str] = None,
    wrap_width: int = 40,
    review: bool = True,
    review_ascii_threshold: float = 0.6,
    review_stop_threshold: float = 0.15,
    strict_review: bool = True,
    strict_max_passes: int = 2,
    smooth: bool = True,
    balance: bool = True,
    balance_ratio: float = 1.8,
    preserve_timing: bool = False,
    # Timing expansion prototype
    expand_timing: bool = False,
    expansion_factor: float = 1.3,
    min_segment_duration: float = 2.0,
    reading_speed_wpm: int = 200,
    min_gap_ms: int = 120,
    output_path: Optional[str] = None,
) -> str:
    p = Path(input_path)
    segments = parse_srt(p.read_text(encoding="utf-8"))
    if not segments:
        raise ValueError("No valid SRT entries found.")

    texts = [s.text for s in segments]
    provider = provider or DummyTranslator()
    # Derive a provider/model identity string for caching
    prov_name = provider.__class__.__name__
    model = getattr(provider, "model", "-")
    cache = JsonCache(cache_path or os.fspath(p.with_name("smart_translation_cache.json")))

    if preserve_timing:
        # Strict per-segment translation; never move text across segments
        eff_wrap = max(wrap_width, 100)
        # Batch translate all segments
        initial = provider.translate_texts(texts, src_lang, tgt_lang)
        # Optional review per segment
        final_texts: List[str] = []
        for t in initial:
            tt = _postprocess(t, tgt_lang)
            if review and _needs_review(tt, tgt_lang, review_ascii_threshold, review_stop_threshold):
                tt2 = provider.translate_texts([tt], None, tgt_lang)[0]
                tt = _postprocess(tt2, tgt_lang)
            if strict_review and review and _needs_review(tt, tgt_lang, review_ascii_threshold, review_stop_threshold):
                passes = 0
                while passes < max(1, strict_max_passes) and _needs_review(tt, tgt_lang, review_ascii_threshold, review_stop_threshold):
                    tt2 = provider.translate_texts([tt], None, tgt_lang)[0]
                    tt = _postprocess(tt2, tgt_lang)
                    passes += 1
            final_texts.append(tt)
        out_segments: List[Segment] = []
        for seg, t in zip(segments, final_texts):
            # Preserve empties and zero-length segments
            if not seg.text.strip() or seg.start == seg.end:
                out_segments.append(Segment(index=seg.index, start=seg.start, end=seg.end, text=""))
            else:
                out_segments.append(Segment(index=seg.index, start=seg.start, end=seg.end, text=_wrap_two_lines(t, width=eff_wrap)))
    else:
        # Smart grouping + distribution path
        groups = _split_into_sentence_groups(texts)
        group_texts = [g[2] for g in groups]

        translated_groups: List[str] = []
        for t in group_texts:
            key = _cache_key(prov_name, str(model), src_lang or "auto", tgt_lang, t)
            cached = cache.get(key)
            if cached is not None:
                translated_groups.append(cached)
                continue
            out = provider.translate_texts([t], src_lang, tgt_lang)[0]
            out = _postprocess(out, tgt_lang)
            cache.set(key, out)
            translated_groups.append(out)

        translated_full = _normalize_whitespace(" ".join(translated_groups))

        # Review pass on groups
        if review:
            for gi, g in enumerate(translated_groups):
                if _needs_review(g, tgt_lang, review_ascii_threshold, review_stop_threshold):
                    key2 = _cache_key(prov_name + "#review", str(model), src_lang or "auto", tgt_lang, g)
                    cached2 = cache.get(key2)
                    if cached2 is not None:
                        translated_groups[gi] = cached2
                    else:
                        out2 = provider.translate_texts([g], None, tgt_lang)[0]
                        out2 = _postprocess(out2, tgt_lang)
                        cache.set(key2, out2)
                        translated_groups[gi] = out2

        # Strict review on groups
        if strict_review and review:
            for gi in range(len(translated_groups)):
                passes = 0
                while passes < max(1, strict_max_passes) and _needs_review(
                    translated_groups[gi], tgt_lang, review_ascii_threshold, review_stop_threshold
                ):
                    g = translated_groups[gi]
                    keyS = _cache_key(prov_name + f"#strict{passes+1}", str(model), src_lang or "auto", tgt_lang, g)
                    cachedS = cache.get(keyS)
                    if cachedS is not None:
                        translated_groups[gi] = cachedS
                    else:
                        outS = provider.translate_texts([g], None, tgt_lang)[0]
                        outS = _postprocess(outS, tgt_lang)
                        cache.set(keyS, outS)
                        translated_groups[gi] = outS
                    passes += 1

        translated_full = _normalize_whitespace(" ".join(translated_groups))

        if keep_timing:
            out_segments = _distribute_translation_over_segments(segments, translated_full, wrap_width=wrap_width)
            if smooth:
                out_segments = _smooth_across_segments(out_segments, wrap_width=wrap_width, balance=balance, balance_ratio=balance_ratio)
        else:
            out_segments = segments[:]
            for (start_i, end_i, _), t in zip(groups, translated_groups):
                for i in range(start_i, end_i + 1):
                    out_segments[i] = Segment(
                        index=out_segments[i].index, start=out_segments[i].start, end=out_segments[i].end, text=_wrap_two_lines(t, width=wrap_width)
                    )

    # Optional timing expansion for readability
    if expand_timing:
        out_segments = _expand_segment_timings(
            out_segments,
            original_segments=segments,
            expansion_factor=expansion_factor,
            min_segment_duration=min_segment_duration,
            reading_speed_wpm=reading_speed_wpm,
            min_gap_ms=min_gap_ms,
        )

    out_path = (
        output_path
        if output_path
        else os.fspath(p.with_name(p.stem + f"_translated_smart_{tgt_lang}" + p.suffix))
    )
    Path(out_path).write_text(format_srt(out_segments), encoding="utf-8")
    return out_path


def _expand_segment_timings(
    translated_segments: List[Segment],
    original_segments: List[Segment],
    *,
    expansion_factor: float,
    min_segment_duration: float,
    reading_speed_wpm: int,
    min_gap_ms: int,
) -> List[Segment]:
    """Prototype: expand segment durations based on reading speed and expansion factor.

    - Keeps the order of segments; shifts subsequent segments forward as needed.
    - Ensures a minimal gap between segments.
    - Leaves empty or zero-length segments unchanged.
    """
    out: List[Segment] = []
    prev_end = None
    min_gap_s = max(0.0, min_gap_ms / 1000.0)
    words_per_sec = max(1e-6, reading_speed_wpm / 60.0)

    for seg_t, seg_o in zip(translated_segments, original_segments):
        text = seg_t.text or ""
        if not text.strip() or seg_o.start == seg_o.end:
            # Preserve empty or zero-length
            start_s = _time_to_seconds(seg_o.start)
            end_s = _time_to_seconds(seg_o.end)
            if prev_end is not None:
                start_s = max(start_s, prev_end + min_gap_s)
                end_s = max(end_s, start_s)
            out.append(Segment(index=seg_t.index, start=_seconds_to_time(start_s), end=_seconds_to_time(end_s), text=seg_t.text))
            prev_end = end_s
            continue

        orig_start = _time_to_seconds(seg_o.start)
        orig_end = _time_to_seconds(seg_o.end)
        orig_dur = max(0.0, orig_end - orig_start)
        # Desired duration based on reading speed (approx by word count)
        word_count = len(re.findall(r"\w+", text))
        wpm_dur = word_count / words_per_sec
        target = max(orig_dur * max(1.0, expansion_factor), wpm_dur, min_segment_duration)

        start_s = orig_start if prev_end is None else max(orig_start, prev_end + min_gap_s)
        end_s = start_s + target
        out.append(Segment(index=seg_t.index, start=_seconds_to_time(start_s), end=_seconds_to_time(end_s), text=seg_t.text))
        prev_end = end_s

    return out
