#!/usr/bin/env python3
"""
Generate feature quality diagnostics for a single sample.

Outputs include:
- Spectral centroid / bandwidth stats
- Energy distribution across MFCCs
- Sensor statistical ranges (if available)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

import librosa
import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Feature quality inspection tool.")
    parser.add_argument("--sample", type=str, required=True, help="Sample ID (e.g., EVT0001).")
    parser.add_argument("--audio-dir", type=Path, default=Path("data/processed/audio"), help="Directory with audio .npy.")
    parser.add_argument("--sensor-dir", type=Path, default=Path("data/processed/sensors"), help="Directory with sensor parquet.")
    parser.add_argument("--config", type=Path, required=True, help="DSP pipeline JSON.")
    parser.add_argument("--out", type=Path, help="Optional JSON output.")
    return parser.parse_args()


def load_audio(sample_id: str, audio_dir: Path) -> np.ndarray:
    path = audio_dir / f"{sample_id}.npy"
    if not path.exists():
        raise FileNotFoundError(f"Audio sample missing: {path}")
    return np.load(path)


def load_sensor(sample_id: str, sensor_dir: Path) -> pd.DataFrame | None:
    path = sensor_dir / f"{sample_id}.parquet"
    if not path.exists():
        return None
    return pd.read_parquet(path)


def audio_metrics(signal: np.ndarray, sr: int = 16_000) -> Dict:
    centroid = librosa.feature.spectral_centroid(y=signal, sr=sr)
    bandwidth = librosa.feature.spectral_bandwidth(y=signal, sr=sr)
    rms = librosa.feature.rms(y=signal)
    return {
        "spectral_centroid_hz_mean": float(centroid.mean()),
        "spectral_bandwidth_hz_mean": float(bandwidth.mean()),
        "rms_dbfs": float(librosa.amplitude_to_db(rms, ref=1.0).mean()),
    }


def mfcc_energy(signal: np.ndarray, sr: int = 16_000, n_mfcc: int = 13) -> Dict:
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=n_mfcc)
    energy = mfcc.mean(axis=1)
    return {f"mfcc_{i+1}_mean": float(val) for i, val in enumerate(energy)}


def sensor_metrics(df: pd.DataFrame) -> Dict:
    stats = {}
    for column in df.columns:
        stats[column] = {
            "mean": float(df[column].mean()),
            "min": float(df[column].min()),
            "max": float(df[column].max()),
            "std": float(df[column].std()),
        }
    return stats


def run_report(sample_id: str, audio_dir: Path, sensor_dir: Path, config_path: Path) -> Dict:
    audio = load_audio(sample_id, audio_dir)
    audio_stats = audio_metrics(audio)
    mfcc_stats = mfcc_energy(audio)
    sensor_df = load_sensor(sample_id, sensor_dir)
    report = {
        "sample": sample_id,
        "config": str(config_path),
        "audio_metrics": audio_stats,
        "mfcc_energy": mfcc_stats,
        "sensor_metrics": sensor_metrics(sensor_df) if sensor_df is not None else None,
    }
    return report


def main() -> None:
    args = parse_args()
    report = run_report(args.sample, args.audio_dir, args.sensor_dir, args.config)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[feature-quality] Report written to {args.out}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

