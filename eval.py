"""
Evaluation harness for ``extract()``.

Usage:
    python eval.py --inputs data/train.jsonl --labels data/train_labels.jsonl

Prints a summary block (the grader parses it) and writes ``results.csv``
with columns: ``id, field, predicted, expected, score, correct``. ``score`` is
the raw float from ``score_field``; ``correct`` is ``score == 1.0``.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from extract import extract
from schema import JobPosting


STRING_FIELDS = ("title", "company", "location")
ENUM_FIELDS = ("is_remote", "experience_level", "salary_currency")
NUMERIC_FIELDS = ("salary_min", "salary_max", "years_experience_min")
LIST_FIELDS = ("required_skills",)
ALL_FIELDS = STRING_FIELDS + ENUM_FIELDS + NUMERIC_FIELDS + LIST_FIELDS

NUMERIC_TOLERANCE = 0.10  # +/- 10%


def score_field(field: str, predicted: Any, expected: Any) -> float:
    """Return a score in [0, 1] for a single field.

    Scoring rules (must match the assignment brief exactly; hidden unit tests
    check these):

    - ``title``, ``company``, ``location``: normalized exact match
      (lowercase + strip). Returns 1.0 or 0.0.
    - ``is_remote``, ``experience_level``, ``salary_currency``: strict equality.
    - ``salary_min``, ``salary_max``, ``years_experience_min``: nullable numeric.
      null vs null = 1.0; null vs value (either direction) = 0.0;
      otherwise 1.0 if ``|pred - exp| <= 0.10 * |exp|``.
    - ``required_skills``: F1 on the set of items, lowercased + stripped.
      empty vs empty = 1.0; empty vs nonempty = 0.0.
    """
    # TODO (assignment): implement each branch.
    raise NotImplementedError


def load_jsonl(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def run(inputs_path: str, labels_path: str, out_csv: str = "results.csv") -> None:
    inputs = load_jsonl(inputs_path)
    labels_by_id = {row["id"]: row["label"] for row in load_jsonl(labels_path)}

    per_field: dict[str, list[float]] = {f: [] for f in ALL_FIELDS}
    full_record_correct = 0
    valid_count = 0
    error_count = 0
    n = len(inputs)

    rows_out: list[list[Any]] = []

    for row in inputs:
        rid = row["id"]
        expected = labels_by_id[rid]

        try:
            pred = extract(row["text"])
            valid_count += 1
            pred_dict = pred.model_dump()
        except ValidationError:
            pred_dict = {f: None for f in ALL_FIELDS}
        except Exception as e:
            print(f"[warn] {rid}: extract() raised {type(e).__name__}: {e}")
            error_count += 1
            pred_dict = {f: None for f in ALL_FIELDS}

        all_correct = True
        for field in ALL_FIELDS:
            s = score_field(field, pred_dict.get(field), expected.get(field))
            per_field[field].append(s)
            correct = s == 1.0
            if not correct:
                all_correct = False
            rows_out.append([rid, field, pred_dict.get(field), expected.get(field), s, correct])
        if all_correct:
            full_record_correct += 1

    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "field", "predicted", "expected", "score", "correct"])
        writer.writerows(rows_out)

    def pct(xs: list[float]) -> float:
        return 100.0 * sum(xs) / len(xs) if xs else 0.0

    scored_count = n - error_count
    schema_rate = 100.0 * valid_count / scored_count if scored_count else 0.0
    full_acc = 100.0 * full_record_correct / n if n else 0.0
    avg_per_field = sum(pct(per_field[f]) for f in ALL_FIELDS) / len(ALL_FIELDS)
    # Overall = weighted blend of avg-per-field (rewards partial correctness)
    # and full-record (rewards getting entire postings right). Grader tiers
    # against this number, not against full-record alone.
    overall_score = 0.6 * avg_per_field + 0.4 * full_acc

    # --- GRADER-PARSED SUMMARY: format must match exactly. ---
    print(f"Schema validation rate: {schema_rate:.1f}%")
    print(f"  (scored {valid_count}/{scored_count}; {error_count} API errors excluded from denominator)")
    print(f"Overall score:          {overall_score:.1f}%")
    print(f"  (0.6 * avg-per-field + 0.4 * full-record; this is the graded number)")
    print(f"Full-record accuracy:   {full_acc:.1f}%")
    print(f"Avg per-field accuracy: {avg_per_field:.1f}%")
    print()
    print("Per-field accuracy:")
    print(f"  title:                {pct(per_field['title']):.1f}%")
    print(f"  company:              {pct(per_field['company']):.1f}%")
    print(f"  location:             {pct(per_field['location']):.1f}%")
    print(f"  is_remote:            {pct(per_field['is_remote']):.1f}%")
    print(f"  experience_level:     {pct(per_field['experience_level']):.1f}%")
    print(f"  salary_min:           {pct(per_field['salary_min']):.1f}%")
    print(f"  salary_max:           {pct(per_field['salary_max']):.1f}%")
    print(f"  salary_currency:      {pct(per_field['salary_currency']):.1f}%")
    print(f"  required_skills (F1): {pct(per_field['required_skills']):.1f}%")
    print(f"  years_experience_min: {pct(per_field['years_experience_min']):.1f}%")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", required=True, help="Path to inputs jsonl")
    parser.add_argument("--labels", required=True, help="Path to labels jsonl")
    parser.add_argument("--out", default="results.csv", help="Path to write per-field CSV")
    args = parser.parse_args()
    run(args.inputs, args.labels, args.out)


if __name__ == "__main__":
    main()
