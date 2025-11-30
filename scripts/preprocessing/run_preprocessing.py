#!/usr/bin/env python3
"""
Entry-point for EmberSense preprocessing workflow.

Steps:
1. Load label CSVs (audio + sensor).
2. Normalize audio duration to 10 s, mono, 16 kHz.
3. Apply bandpass filter & amplitude normalization via librosa.
4. Align sensor windows, resample to 1 Hz, z-score normalize per channel.
5. Export processed artifacts and update metadata logs.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
PROCESSED_ROOT = PROJECT_ROOT / "data" / "processed"
LABELS_DIR = PROJECT_ROOT / "metadata" / "labels"
LOG_PATH = PROJECT_ROOT / "metadata" / "preprocessing_log.csv"


def ensure_dirs() -> None:
    PROCESSED_ROOT.mkdir(parents=True, exist_ok=True)


def load_labels() -> dict[str, pd.DataFrame]:
    labels = {}
    for csv_name in ("audio_event_annotations.csv", "sensor_segment_annotations.csv"):
        csv_path = LABELS_DIR / csv_name
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing label file: {csv_path}")
        labels[csv_name] = pd.read_csv(csv_path)
    return labels


def log_step(script: str, description: str, input_glob: str, output_path: Path, parameters: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        LOG_PATH.write_text("timestamp,script,description,input_glob,output_path,parameters,checksum\n")
    import datetime, json
    timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    row = f'{timestamp},{script},"{description}",{input_glob},{output_path},{json.dumps(parameters)},PENDING\n'
    with LOG_PATH.open("a", encoding="utf-8") as fp:
        fp.write(row)


def run_notebook(nb_path: Path, output_path: Path) -> None:
    cmd = [
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--ExecutePreprocessor.timeout=0",
        "--output",
        str(output_path),
        str(nb_path),
    ]
    subprocess.run(cmd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run EmberSense preprocessing pipeline.")
    parser.add_argument(
        "--notebook",
        type=Path,
        default=PROJECT_ROOT / "notebooks" / "week1" / "embersense_preprocessing.ipynb",
        help="Path to preprocessing notebook.",
    )
    parser.add_argument(
        "--executed-notebook",
        type=Path,
        default=PROJECT_ROOT / "artifacts" / "week1" / "embersense_preprocessing.executed.ipynb",
        help="Where to save executed notebook.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dirs()
    labels = load_labels()
    print(f"[preprocessing] Loaded labels: {[f'{k}:{len(v)}' for k, v in labels.items()]}")
    log_step(
        script="scripts/preprocessing/run_preprocessing.py",
        description="Execute preprocessing notebook",
        input_glob="data/raw/**/*",
        output_path=args.executed_notebook,
        parameters={"notebook": str(args.notebook)},
    )
    run_notebook(args.notebook, args.executed_notebook)
    print(f"[preprocessing] Notebook executed -> {args.executed_notebook}")


if __name__ == "__main__":
    main()

