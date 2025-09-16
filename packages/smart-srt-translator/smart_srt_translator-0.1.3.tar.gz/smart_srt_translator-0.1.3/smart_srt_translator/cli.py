from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .api import translate_srt_file
from .env import load_env_vars
from . import __version__
from .models import TranslateOptions
from .providers import DummyTranslator

try:
    from .providers.openai_provider import OpenAITranslator  # optional
except Exception:  # pragma: no cover
    OpenAITranslator = None  # type: ignore


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    # Auto-load .env style files for OPENAI_* if available
    load_env_vars()
    parser = argparse.ArgumentParser(
        prog="srt-translate",
        description="Smart SRT translation",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Environment:\n"
            "- Loads OPENAI_API_KEY/OPENAI_MODEL from .env (repo root or VidScalerSubtitleAdder/.env).\n\n"
            "Recommended defaults:\n"
            "- wrap width: 40\n"
            "- review: on (ascii 0.6, stop 0.15)\n"
            "- strict review: on (2 passes)\n"
            "- smoothing: on\n"
            "- balancing: on (ratio 1.8)\n\n"
            "Examples:\n"
            "- Basic smart: srt-translate translate input.srt en de\n"
            "- Tuning: srt-translate translate input.srt en de --wrap-width 38 --balance-ratio 1.7\n"
        ),
    )
    # Version (works without subcommand)
    parser.add_argument("--version", action="version", version=f"srt-translate {__version__}")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_trans = sub.add_parser(
        "translate",
        help="Translate an SRT file",
        formatter_class=argparse.RawTextHelpFormatter,
        description=(
            "Translate SRT using smart pipeline (OpenAI by default).\n\n"
            "Recommended defaults:\n"
            "- wrap width: 40\n- review: on (ascii 0.6, stop 0.15)\n"
            "- strict review: on (2 passes)\n- smoothing: on\n- balancing: on (ratio 1.8)\n"
        ),
    )
    p_trans.add_argument("input", help="Path to input .srt file")
    p_trans.add_argument("src", help="Source language code or 'auto'")
    p_trans.add_argument("tgt", help="Target language code")
    p_trans.add_argument("--provider", choices=["dummy", "openai"], default="openai")
    p_trans.add_argument("--mode", choices=["basic", "smart"], default="smart", help="Translation mode")
    p_trans.add_argument("--probe", choices=["off", "ask", "auto"], default="off")
    p_trans.add_argument("--audio", help="Optional audio/video source for probe", default=None)
    p_trans.add_argument("--out", help="Explicit output path", default=None)
    # Language-aware preset
    p_trans.add_argument(
        "--lang-preset",
        choices=["auto", "off"],
        default="auto",
        help="Apply language-aware defaults (auto: DE-friendly settings)",
    )
    # Smart-mode tuning
    p_trans.add_argument("--wrap-width", type=int, default=40, help="Line wrap width per segment (default 40)")
    p_trans.add_argument("--no-review", action="store_true", help="Disable English-remnant review pass")
    p_trans.add_argument("--review-ascii", type=float, default=0.6, help="ASCII ratio threshold for review (default 0.6)")
    p_trans.add_argument("--review-stop", type=float, default=0.15, help="English stopword ratio threshold for review (default 0.15)")
    strict_grp = p_trans.add_mutually_exclusive_group()
    strict_grp.add_argument("--strict-review", dest="strict_review", action="store_true", help="Enable strict review (default)")
    strict_grp.add_argument("--no-strict-review", dest="strict_review", action="store_false", help="Disable strict review")
    p_trans.set_defaults(strict_review=True)
    p_trans.add_argument("--strict-passes", type=int, default=2, help="Max strict review passes per group (default 2)")
    p_trans.add_argument("--no-smooth", action="store_true", help="Disable cross-segment wrap smoothing")
    p_trans.add_argument("--no-balance", action="store_true", help="Disable length balancing (default on)")
    p_trans.add_argument("--balance-ratio", type=float, default=1.8, help="Balance trigger ratio (longer/shorter; default 1.8)")
    p_trans.add_argument("--preserve-timing", action="store_true", help="Translate per-segment without cross-boundary reflow (wrap>=100, no balancing)")
    # Timing expansion prototype
    p_trans.add_argument("--expand-timing", action="store_true", help="Expand segment durations for readability based on reading speed")
    p_trans.add_argument("--expansion-factor", type=float, default=1.3, help="Multiply original durations (e.g., DE≈1.3)")
    p_trans.add_argument("--min-seg-dur", type=float, default=2.0, help="Minimum seconds per segment")
    p_trans.add_argument("--reading-wpm", type=int, default=200, help="Reading speed in words per minute")
    p_trans.add_argument("--min-gap-ms", type=int, default=120, help="Minimum gap between segments in milliseconds")

    p_fin = sub.add_parser("finalize", help="Apply resolutions to a translated SRT")
    p_fin.add_argument("translated", help="Path to already translated .srt file")
    p_fin.add_argument("--resolutions", required=True, help="Path to resolutions.json")
    p_fin.add_argument(
        "--requests",
        help="Path to the corresponding requests.json (optional if resolutions include segment_id)",
        default=None,
    )
    p_fin.add_argument("--out", help="Explicit output path (defaults to *_final.srt)")

    args = parser.parse_args(argv)

    if args.cmd == "translate":
        provider = DummyTranslator()
        if args.provider == "openai":
            if OpenAITranslator is None:
                parser.error("OpenAI provider unavailable. Install with [openai] extra.")
            provider = OpenAITranslator()  # type: ignore
        if args.mode == "smart":
            from .smart_pipeline import translate_srt_smart
            review = not args.no_review
            review_ascii = args.review_ascii
            review_stop = args.review_stop
            # Language-aware preset overlay (non-destructive): only applies for smart mode
            preserve_timing = args.preserve_timing
            wrap_width = args.wrap_width
            expand_timing = args.expand_timing
            expansion_factor = args.expansion_factor
            min_seg_dur = args.min_seg_dur
            reading_wpm = args.reading_wpm
            min_gap_ms = args.min_gap_ms

            if getattr(args, 'lang_preset', 'off') == 'auto' and (args.tgt.lower().startswith('de')):
                if not preserve_timing:
                    preserve_timing = True
                if wrap_width < 100:
                    wrap_width = 100
                if not expand_timing:
                    expand_timing = True
                    if expansion_factor < 1.3:
                        expansion_factor = 1.3
                    if min_seg_dur < 2.0:
                        min_seg_dur = 2.0
                    if reading_wpm < 200:
                        reading_wpm = 200
                    if min_gap_ms < 120:
                        min_gap_ms = 120

            outp = translate_srt_smart(
                args.input,
                src_lang=None if args.src.lower() == "auto" else args.src or "en",
                tgt_lang=args.tgt,
                provider=provider,
                keep_timing=True,
                wrap_width=wrap_width,
                review=review,
                review_ascii_threshold=review_ascii,
                review_stop_threshold=review_stop,
                strict_review=args.strict_review,
                strict_max_passes=args.strict_passes,
                smooth=(not args.no_smooth),
                balance=(not args.no_balance),
                balance_ratio=args.balance_ratio,
                preserve_timing=preserve_timing,
                expand_timing=expand_timing,
                expansion_factor=expansion_factor,
                min_segment_duration=min_seg_dur,
                reading_speed_wpm=reading_wpm,
                min_gap_ms=min_gap_ms,
                output_path=args.out,
            )
            print(f"Written: {outp}")
            return 0
        else:
            opts = TranslateOptions(
                provider=provider,
                src_lang=None if args.src.lower() == "auto" else args.src,
                tgt_lang=args.tgt,
                probe_mode=args.probe,
                audio_source=args.audio,
                output_path=args.out,
            )
            res = translate_srt_file(args.input, opts.src_lang, opts.tgt_lang, opts)
            print(f"Written: {res.output_path}")
            if res.pending_requests:
                req_path = Path(res.output_path).with_suffix(".requests.json")
                print(f"Audio probe requests written: {req_path}")
            return 0

    if args.cmd == "finalize":
        from .io_json import read_resolutions_json, read_requests_json
        from .api import apply_resolutions_to_srt

        resolutions = read_resolutions_json(args.resolutions)
        req_map = None
        if args.requests:
            requests = read_requests_json(args.requests)
            req_map = {r.request_id: r.segment_id for r in requests}
        outp = apply_resolutions_to_srt(args.translated, resolutions, req_map, args.out)
        print(f"Written: {outp}")
        return 0

    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

