#!/usr/bin/env python3
"""
Evaluate MFCC stability under injected noise for EmberSense DSP config.

Example:
python 03_feature_pipeline/notebooks/noise_robustness_test.py \
    --config 03_feature_pipeline/edge_impulse/project_export.json \
    --audio-dir 02_dataset/processed/cleaned_audio \
    --snr-list 0 5 10 \
    --report 05_evaluation/reports/noise_robustness.json
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, List

import librosa
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Noise robustness test for MFCC features.")
    parser.add_argument("--config", type=Path, required=True, help="Path to DSP pipeline JSON.")
    parser.add_argument("--audio-dir", type=Path, default=Path("02_dataset/processed/cleaned_audio"), help="Directory with normalized audio .npy files.")
    parser.add_argument("--snr-list", type=float, nargs="+", default=[0, 5, 10, 20], help="SNR levels in dB to test.")
    parser.add_argument("--sample-limit", type=int, default=5, help="Max number of samples to analyze.")
    parser.add_argument("--report", type=Path, help="Optional JSON report output.")
    return parser.parse_args()


def load_config(config_path: Path) -> Dict:
    return json.loads(config_path.read_text(encoding="utf-8"))


def list_samples(audio_dir: Path, limit: int) -> List[Path]:
    files = sorted(audio_dir.glob("*.npy"))
    return files[:limit]


def add_noise(signal: np.ndarray, snr_db: float) -> np.ndarray:
    signal_power = np.mean(signal ** 2)
    if signal_power == 0:
        return signal
    snr_linear = 10 ** (snr_db / 10)
    noise_power = signal_power / snr_linear
    noise = np.random.normal(0, math.sqrt(noise_power), size=signal.shape)
    return signal + noise


def compute_mfcc(signal: np.ndarray, sr: int, config: Dict) -> np.ndarray:
    mfcc_block = next(block for block in config["blocks"] if block["type"] == "MFCC")
    params = mfcc_block["parameters"]
    hop_length = int(sr * (params["frame_hop_ms"] / 1000.0))
    n_fft = params["fft_length"]
    n_mfcc = params["num_mfcc"]
    mfcc = librosa.feature.mfcc(
        y=signal,
        sr=sr,
        n_mfcc=n_mfcc,
        n_fft=n_fft,
        hop_length=hop_length,
    )
    if params.get("deltas", False):
        delta = librosa.feature.delta(mfcc)
        mfcc = np.vstack([mfcc, delta])
    return mfcc


def run_test(config_path: Path, audio_dir: Path, snr_list: List[float], limit: int) -> Dict:
    config = load_config(config_path)
    samples = list_samples(audio_dir, limit)
    results = []
    sr = 16_000
    for sample in samples:
        signal = np.load(sample)
        clean_feat = compute_mfcc(signal, sr, config)
        sample_entry = {"sample": sample.name, "snr_results": []}
        for snr in snr_list:
            noisy = add_noise(signal, snr)
            noisy_feat = compute_mfcc(noisy, sr, config)
            drift = np.mean(np.abs(clean_feat - noisy_feat) / (np.abs(clean_feat) + 1e-6)) * 100
            sample_entry["snr_results"].append({"snr_db": snr, "drift_pct": float(drift)})
        results.append(sample_entry)
    return {
        "config": str(config_path),
        "audio_dir": str(audio_dir),
        "snr_list": snr_list,
        "samples_tested": len(results),
        "results": results,
    }


def main() -> None:
    args = parse_args()
    report = run_test(args.config, args.audio_dir, args.snr_list, args.sample_limit)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[noise-test] Report written to {args.report}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

