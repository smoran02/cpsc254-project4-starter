"""Pre-flight check for project4 submission. Run before you submit.

Verifies:
- required files are present
- schema.py exposes JobPosting
- extract.py exposes extract(text) with the expected signature
- eval.py has the --inputs/--labels CLI
- iterations.md has at least 3 labeled versions

Usage:
    python check_submission.py          # soft mode: treats missing output artifacts as notes
    python check_submission.py --final  # strict mode: fails if any deliverable is missing
"""

from __future__ import annotations

import argparse
import inspect
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SOURCE_FILES = [
    "extract.py",
    "eval.py",
    "schema.py",
    "requirements.txt",
]

OUTPUT_FILES = [
    "iterations.md",
    "writeup.md",
    "results.csv",
    "AI_DISCLOSURE.md",
]

OUTPUT_HINTS = {
    "results.csv": "run `python eval.py --inputs data/train.jsonl --labels data/train_labels.jsonl` to generate it",
    "iterations.md": "log your prompt/schema iterations here (≥3 required at submission time)",
    "writeup.md": "250–300 word error analysis referencing results.csv (required at submission time)",
    "AI_DISCLOSURE.md": "required at submission time: fill out the template and remove the TEMPLATE sentinel line (-10 pts if missing or unfilled)",
}

AI_DISCLOSURE_SENTINEL = "TEMPLATE: edit before submitting"


def _extract_import_hint() -> str:
    """Produce a targeted rename hint if extract.py defines e.g. extract_job_posting."""
    try:
        import extract as extract_mod
    except Exception as e:
        return f"cannot import extract.py: {e}"

    candidates = [
        n
        for n in dir(extract_mod)
        if "extract" in n.lower()
        and not n.startswith("_")
        and callable(getattr(extract_mod, n, None))
    ]
    if candidates:
        return (
            f"extract.py has no function named `extract`. Found instead: {candidates}. "
            "The grader and the final project both import `extract` by that exact name; rename it back."
        )
    return "extract.py is missing a function named `extract`. The grader and the final project import it by that exact name."


def check(final: bool = False) -> None:
    errors: list[str] = []
    notes: list[str] = []

    for name in SOURCE_FILES:
        if not (ROOT / name).exists():
            errors.append(f"missing file: {name}")

    for name in OUTPUT_FILES:
        if not (ROOT / name).exists():
            msg = f"{name} missing: {OUTPUT_HINTS[name]}"
            if final:
                errors.append(msg)
            else:
                notes.append(msg)

    sys.path.insert(0, str(ROOT))

    try:
        from schema import JobPosting  # noqa: F401
    except Exception as e:
        errors.append(f"cannot import JobPosting from schema.py: {e}")

    try:
        from extract import extract

        sig = inspect.signature(extract)
        params = list(sig.parameters.values())
        if len(params) != 1:
            errors.append(
                f"extract() must take exactly 1 argument; got {len(params)}"
            )
    except NotImplementedError:
        errors.append("extract() is still a stub (raises NotImplementedError)")
    except ImportError:
        errors.append(_extract_import_hint())
    except Exception as e:
        errors.append(f"cannot import extract from extract.py: {e}")

    r = subprocess.run(
        [sys.executable, str(ROOT / "eval.py"), "--help"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if r.returncode != 0 or "--inputs" not in r.stdout or "--labels" not in r.stdout:
        errors.append("eval.py must accept --inputs and --labels CLI args")

    disclosure = ROOT / "AI_DISCLOSURE.md"
    if final and disclosure.exists():
        if AI_DISCLOSURE_SENTINEL in disclosure.read_text():
            errors.append(
                "AI_DISCLOSURE.md still contains the template sentinel line "
                f"('{AI_DISCLOSURE_SENTINEL}'). Fill out the template and remove that line. "
                "Missing or unfilled disclosure is a -10 point penalty."
            )

    it = ROOT / "iterations.md"
    if it.exists():
        # Tolerate markdown decoration around the version label: **v1:**, _v1_:,
        # ### v1:, etc. Require a digit somewhere after the label so a student
        # who writes only "v1:" with no score doesn't silently satisfy the rubric.
        text = it.read_text()
        labeled = re.findall(r"(?mi)^[\s*_#]*\s*v\d+[\s*_]*:.*", text)
        scored = [line for line in labeled if re.search(r"\d", line.split(":", 1)[1])]
        if len(scored) < 3:
            errors.append(
                f"iterations.md has {len(scored)} version labels with a score; "
                f"need at least 3 (found {len(labeled)} total; each must include a numeric score, e.g. 'v1: ... 62.5%')"
            )

    if errors:
        header = "PRE-FLIGHT FAILED:" if final else "PRE-FLIGHT FAILED (pre-final):"
        print(header)
        for e in errors:
            print(f"  - {e}")
        if notes:
            print("\nAlso missing (not failures yet, required before final submission):")
            for nt in notes:
                print(f"  - {nt}")
        sys.exit(1)

    print("Pre-flight check passed." if final else "Pre-flight check passed (pre-final mode).")
    if notes:
        print("\nBefore submission, also complete:")
        for nt in notes:
            print(f"  - {nt}")
        print("\nRun `python check_submission.py --final` to verify.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--final",
        action="store_true",
        help="Strict mode: fail if any deliverable (results.csv, iterations.md, writeup.md) is missing. Use right before submission.",
    )
    args = parser.parse_args()
    check(final=args.final)
