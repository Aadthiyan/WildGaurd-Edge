#!/usr/bin/env python3
"""
Ensure annotation files meet EmberSense schema expectations.

Validations:
- Required columns present.
- start/end ordering and duration bounds.
- Labels belong to allowed taxonomy derived from manifest.
- No overlapping duplicates for same file/time span (audio).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

MANIFEST_PATH_DEFAULT = Path("02_dataset/raw/metadata_raw.json")
LABEL_FILES = {
    "audio": Path("02_dataset/processed/annotations.csv"),
    "sensor": Path("02_dataset/processed/sensor_segment_annotations.csv"),
}

REQUIRED_COLUMNS = {
    "audio": ["event_id", "file_path", "start_s", "end_s", "label"],
    "sensor": ["segment_id", "file_path", "start_iso", "end_iso", "label"],
}


def load_allowed_labels(manifest_path: Path) -> Dict[str, List[str]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    audio_labels = []
    for source in manifest.get("sources", []):
        if source.get("modality") == "audio":
            audio_labels.extend(source.get("labels", []))
    return {
        "audio": sorted(set(audio_labels + ["rain", "wind", "vehicle", "nominal"])),
        "sensor": ["pre_fire_alert", "nominal"],
    }


def validate_audio(df: pd.DataFrame, allowed: List[str]) -> List[str]:
    issues: List[str] = []
    for col in REQUIRED_COLUMNS["audio"]:
        if col not in df.columns:
            issues.append(f"Missing column '{col}' in audio annotations.")
    if issues:
        return issues
    invalid_labels = sorted(set(df["label"]) - set(allowed))
    if invalid_labels:
        issues.append(f"Audio labels outside taxonomy: {invalid_labels}")
    invalid_duration = df[df["end_s"] <= df["start_s"]]
    if not invalid_duration.empty:
        issues.append(
            f"{len(invalid_duration)} audio events have non-positive duration."
        )
    duplicates = (
        df.groupby(["file_path", "start_s", "end_s", "label"])
        .size()
        .reset_index(name="count")
    )
    duplicates = duplicates[duplicates["count"] > 1]
    if not duplicates.empty:
        issues.append("Duplicate audio annotations detected.")
    return issues


def validate_sensor(df: pd.DataFrame, allowed: List[str]) -> List[str]:
    issues: List[str] = []
    for col in REQUIRED_COLUMNS["sensor"]:
        if col not in df.columns:
            issues.append(f"Missing column '{col}' in sensor annotations.")
    if issues:
        return issues
    invalid_labels = sorted(set(df["label"]) - set(allowed))
    if invalid_labels:
        issues.append(f"Sensor labels outside taxonomy: {invalid_labels}")
    if (df["start_iso"] >= df["end_iso"]).any():
        issues.append("Sensor segments with start >= end timestamps detected.")
    return issues


def run_checks(manifest_path: Path) -> Dict:
    allowed = load_allowed_labels(manifest_path)
    results = []
    for modality, csv_path in LABEL_FILES.items():
        if not csv_path.exists():
            results.append(
                {
                    "modality": modality,
                    "status": "missing",
                    "issues": [f"Label file not found: {csv_path}"],
                }
            )
            continue
        df = pd.read_csv(csv_path)
        validator = validate_audio if modality == "audio" else validate_sensor
        issues = validator(df, allowed[modality])
        results.append(
            {
                "modality": modality,
                "status": "pass" if not issues else "attention",
                "issues": issues,
                "records": len(df),
            }
        )
    return {
        "checked_at": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "results": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate EmberSense annotation files.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_PATH_DEFAULT,
        help="Path to metadata_raw.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional JSON output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_checks(args.manifest)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[label-check] Report written to {args.report}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

