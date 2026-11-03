"""Validate a test matrix CSV so every row is one clean, readable experiment."""
import csv

REQUIRED = [
    "test_id", "channel", "funnel_stage", "variable", "hypothesis", "variant_a", "variant_b",
    "kept_constant", "primary_metric", "early_read_metric", "planned_weeks",
    "utm_content_a", "utm_content_b",
]
MULTI_VARIABLE_HINTS = (" and ", " + ", ",", "&", " plus ")


def validate_row(row, line):
    problems = []
    for col in REQUIRED:
        if not (row.get(col) or "").strip():
            problems.append(f"line {line}: '{col}' is empty")
    var = (row.get("variable") or "").lower()
    if any(h in var for h in MULTI_VARIABLE_HINTS):
        problems.append(f"line {line}: 'variable' looks like more than one thing ({row['variable']!r}); test one at a time")
    a, b = (row.get("variant_a") or "").strip(), (row.get("variant_b") or "").strip()
    if a and a == b:
        problems.append(f"line {line}: variants A and B are identical")
    ca, cb = (row.get("utm_content_a") or "").strip(), (row.get("utm_content_b") or "").strip()
    if ca and ca == cb:
        problems.append(f"line {line}: utm_content values must differ so results can be told apart")
    if (row.get("primary_metric") or "").strip().lower() == (row.get("early_read_metric") or "").strip().lower() and row.get("primary_metric"):
        problems.append(f"line {line}: primary metric and early-read metric are the same; early read is direction only, the primary metric decides")
    return problems


def validate_file(path):
    problems = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            return [f"missing columns: {', '.join(missing)}"]
        ids = set()
        for i, row in enumerate(reader, start=2):
            problems += validate_row(row, i)
            tid = (row.get("test_id") or "").strip()
            if tid in ids:
                problems.append(f"line {i}: duplicate test_id {tid}")
            ids.add(tid)
    return problems
