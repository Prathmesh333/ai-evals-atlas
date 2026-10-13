"""Evaluate stored predictions with strict input validation and paired uncertainty."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent


def wilson(successes, total, z=1.959963984540054):
    if not isinstance(total, int) or not isinstance(successes, int) or not 0 <= successes <= total or total < 1:
        raise ValueError("Require integer counts with 0 <= successes <= total and total > 0")
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return max(0, center - radius), min(1, center + radius)


def load_cases(path):
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not cases:
        raise ValueError("Dataset is empty")
    seen = set()
    for case in cases:
        if not all(isinstance(case.get(k), str) and case[k] for k in ("id", "input", "expected", "slice")):
            raise ValueError("Each case requires nonempty id, input, expected, and slice strings")
        if case["id"] in seen:
            raise ValueError("Duplicate case ID: " + case["id"])
        seen.add(case["id"])
    return cases


def normalize(value):
    # Appropriate only for these constrained teaching answers.
    return " ".join(value.casefold().split())


def score(cases, predictions):
    if not isinstance(predictions, dict):
        raise ValueError("Predictions must map case IDs to answer strings")
    extra = set(predictions) - {case["id"] for case in cases}
    if extra:
        raise ValueError("Unknown prediction IDs: " + ", ".join(sorted(extra)))
    if any(not isinstance(value, str) for value in predictions.values()):
        raise ValueError("Every prediction must be a string")
    rows = []
    for case in cases:
        actual = predictions.get(case["id"])
        rows.append({**case, "actual": actual, "pass": actual is not None and normalize(actual) == normalize(case["expected"]),
                     "status": "missing" if actual is None else "scored"})
    return rows


def aggregate(rows):
    passed = sum(row["pass"] for row in rows)
    return {"cases": len(rows), "passed": passed, "accuracy": passed / len(rows),
            "wilson_95": wilson(passed, len(rows)), "missing": sum(row["status"] == "missing" for row in rows)}


def paired_bootstrap(a, b, iterations=5000, seed=42):
    if len(a) != len(b) or not a:
        raise ValueError("Paired samples must have equal nonzero length")
    differences = [int(y) - int(x) for x, y in zip(a, b)]
    rng = random.Random(seed)
    samples = sorted(sum(rng.choices(differences, k=len(differences))) / len(differences) for _ in range(iterations))
    return {"candidate_minus_baseline": sum(differences) / len(differences),
            "percentile_bootstrap_95": [samples[int(iterations * .025)], samples[int(iterations * .975)]],
            "resampling_unit": "case", "iterations": iterations, "seed": seed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=HERE / "data" / "cases.jsonl")
    parser.add_argument("--baseline", type=Path, default=HERE / "data" / "baseline.json")
    parser.add_argument("--candidate", type=Path, default=HERE / "data" / "candidate.json")
    parser.add_argument("--output", type=Path, default=HERE / "runs" / "evaluation.json")
    args = parser.parse_args()
    try:
        cases = load_cases(args.cases)
        baseline = score(cases, json.loads(args.baseline.read_text(encoding="utf-8")))
        candidate = score(cases, json.loads(args.candidate.read_text(encoding="utf-8")))
    except (ValueError, OSError) as error:
        parser.error(str(error))
    slices = defaultdict(list)
    for row in candidate:
        slices[row["slice"]].append(row)
    report = {"description": "Synthetic stored predictions, not measurements of real AI models",
        "protocol": "casefold + whitespace normalization; missing answer counts as failure",
        "sha256": {name: hashlib.sha256(getattr(args, name).read_bytes()).hexdigest() for name in ("cases", "baseline", "candidate")},
        "baseline": aggregate(baseline), "candidate": aggregate(candidate),
        "comparison": paired_bootstrap([r["pass"] for r in baseline], [r["pass"] for r in candidate]),
        "candidate_slices": {name: aggregate(rows) for name, rows in slices.items()},
        "baseline_cases": baseline, "candidate_cases": candidate}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if not k.endswith("_cases")}, indent=2))


if __name__ == "__main__":
    main()
