#!/usr/bin/env python3
"""
Verify baseline models meet minimum accuracy threshold.

Usage:
python 04_models/check_baseline_accuracy.py \
    --report 04_models/baseline/baseline_performance.json \
    --threshold 0.70
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check baseline accuracy threshold.")
    parser.add_argument(
        "--report",
        type=Path,
        required=True,
        help="Path to baseline_performance.json",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.70,
        help="Minimum acceptable accuracy.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = json.loads(args.report.read_text(encoding="utf-8"))
    models = data.get("models", [])
    failing = [
        (model["name"], model["accuracy"])
        for model in models
        if model.get("accuracy", 0.0) < args.threshold
    ]
    if failing:
        print("[baseline-check] FAIL")
        for name, acc in failing:
            print(f" - {name}: {acc:.2%} < {args.threshold:.0%}")
        raise SystemExit(1)
    print("[baseline-check] PASS")
    for model in models:
        print(f" - {model['name']}: {model['accuracy']:.2%}")


if __name__ == "__main__":
    main()

