#!/usr/bin/env python3
"""
Validate EmberSense raw dataset folders against the manifest.

Usage:
    python scripts/validators/validate_dataset_completeness.py \
        --manifest metadata/dataset_manifest.json \
        --report artifacts/week1/dataset_completeness.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple


def count_files(directory: Path) -> int:
    if not directory.exists():
        return 0
    return sum(
        1
        for path in directory.rglob("*")
        if path.is_file() and path.name != ".gitkeep"
    )


def validate_source(source: Dict, root: Path) -> Dict:
    target_dir = root / source["target_dir"]
    file_count = count_files(target_dir)
    expected = source.get("expected_items", 0)
    status = "pass" if (file_count >= expected and expected > 0) else "pending"
    issues: List[str] = []

    if not target_dir.exists():
        issues.append(f"Missing directory: {target_dir}")
    if expected > 0 and file_count < expected:
        issues.append(
            f"File shortfall: expected {expected}, found {file_count}"
        )
    if expected == 0:
        issues.append("Expected item count not defined in manifest.")

    return {
        "source_id": source["id"],
        "target_dir": str(target_dir),
        "expected_items": expected,
        "observed_items": file_count,
        "status": status if not issues else "attention",
        "issues": issues,
    }


def run_validation(manifest_path: Path, project_root: Path) -> Dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sources = manifest.get("sources", [])
    results = [validate_source(src, project_root) for src in sources]

    return {
        "validated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "manifest_version": manifest.get("version"),
        "results": results,
    }


def write_report(report: Dict, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate dataset completeness against manifest."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Path to dataset_manifest.json",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Project root (default: current directory)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional path to save JSON report",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_validation(args.manifest, args.project_root)
    if args.report:
        write_report(report, args.report)
        print(f"[validator] Report written to {args.report}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

