Smart SRT Translator
====================

A lightweight, extensible Python package for translating SRT subtitle files, with optional audio probe support and pluggable providers (OpenAI, etc.).

Features
--------
- Smart SRT in/out: preserves timing and structure.
- Provider abstraction: start with a no-op Dummy, optionally use OpenAI.
- Optional audio probe flow: generate JSON requests for uncertain segments.
- CLI `srt-translate` for quick usage; programmatic API for embedding.

Quick Start
-----------
- Install (PyPI): `python -m pip install "smart-srt-translator[openai]"` (zsh/PowerShell: Extras in Anführungszeichen setzen)
- Create venv (choose one, depending on your setup):
  - Windows: `py -m venv .venv` or `python -m venv .venv`
  - macOS/Linux: `python3 -m venv .venv` (or `python -m venv .venv`)
  - Activate:
    - PowerShell: `.venv\Scripts\Activate.ps1`
    - CMD: `.venv\Scripts\activate.bat`
    - bash/zsh: `source .venv/bin/activate`
- Install (local): `python -m pip install -e ".[openai]"` (omit `[openai]` to skip OpenAI extra; zsh/PowerShell: Extras quoten)
- Translate (CLI):
  - Smart (default): `srt-translate translate Sample/firstdayinnewhospital.srt en de`
  - Provider is `openai` by default; mode `smart` by default.
  - The CLI auto-loads `.env` with `OPENAI_API_KEY` and optional `OPENAI_MODEL`.
  - Note: Inside the venv prefer `python -m pip ...` (on Unix you may use `python3 -m pip ...`).

Quick Start (DE)
----------------
- Minimal: `srt-translate translate <input.srt> en de` (language-aware preset applies for DE).
- Timing-critical (burn-in/live): `srt-translate translate <input.srt> en de --preserve-timing --wrap-width 120`
- Improve readability (long clips): `srt-translate translate <input.srt> en de --expand-timing --expansion-factor 1.3 --min-seg-dur 2.0`
- Both (recommended for DE video): `srt-translate translate <input.srt> en de --preserve-timing --wrap-width 120 --expand-timing`

Preserve Timing Mode
--------------------
- For timing-critical SRT where segments must never exchange words across boundaries:
  - Use `--preserve-timing` to translate per-segment with a higher wrap width (>=100), no balancing, and no cross-boundary reflow.
  - Example: `srt-translate translate input.srt en de --preserve-timing`
  - Tip: Combine with a larger `--wrap-width 120` if needed.

Timing Expansion (Prototype)
----------------------------
- Expands segment durations to improve readability (longer target texts like DE):
  - `--expand-timing --expansion-factor 1.3 --min-seg-dur 2.0 --reading-wpm 200 --min-gap-ms 120`
  - Works with both smart and preserve-timing modes; keeps segment order, shifts subsequent segments forward.
  - Recommended for DE: `--preserve-timing --expand-timing --wrap-width 120 --expansion-factor 1.3`
  - Basic per-segment: `srt-translate translate Sample/firstdayinnewhospital.srt auto de --provider dummy --mode basic`

Recommended Defaults
--------------------
- Wrap width: 40 (`--wrap-width 40`)
- Review: on, thresholds ASCII=0.6, STOP=0.15 (override with `--no-review`, `--review-*`)
- Strict review: on with 2 passes (disable via `--no-strict-review`)
- Smoothing: on (disable via `--no-smooth`)
- Balancing: on, ratio=1.8 (disable via `--no-balance`, tune with `--balance-ratio`)

Minimal Usage
-------------
`srt-translate translate Sample/firstdayinnewhospital.srt en de`

Programmatic API
----------------
```
from smart_srt_translator import translate_srt_file, translate_srt_smart, TranslateOptions

res = translate_srt_file(
    "Sample/firstdayinnewhospital.srt",
    src_lang=None,  # auto
    tgt_lang="de",
    options=TranslateOptions(probe_mode="off")
)
print(res.output_path)

# or Smart mode (uses recommended defaults)
out = translate_srt_smart(
    "Sample/firstdayinnewhospital.srt",
    src_lang="en",
    tgt_lang="de",
    # wrap_width=40,
    # review=True,
    # review_ascii_threshold=0.6,
    # review_stop_threshold=0.15,
    # strict_review=True,
    # strict_max_passes=2,
    # smooth=True,
    # balance=True,
    # balance_ratio=1.8,
)
print(out)
```

Audio Probe Flow (Concept)
--------------------------
- `--probe ask`: creates `<output>.requests.json` with segment time windows needing audio review.
- Provide `resolutions.json` later (same IDs) to finalize improved translations (planned `finalize`).
- `--probe auto`: will require a transcriber provider and audio source (roadmap).

Configuration
-------------
- OpenAI provider needs `OPENAI_API_KEY` and optional `OPENAI_MODEL`.
- The CLI auto-loads `.env` from the repo root if present.

Status
------
- MVP scaffold ready. OpenAI provider implemented at a minimal prompt level.
- Finalization flow and advanced sentence-grouping/caching from the app are planned to be ported.

License
-------
MIT

Further Docs
------------
- Parameter reference: see PARAMS.md for a concise overview of modes, flags, defaults, and recipes.
 - Readability guide: see READABILITY.md for DE presets and timing expansion tips.
