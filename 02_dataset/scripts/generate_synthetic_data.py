#!/usr/bin/env python3
"""
Generate synthetic dataset for testing EmberSense pipeline.

This creates placeholder data so you can test the pipeline without
downloading large datasets.

Usage:
    python 02_dataset/scripts/generate_synthetic_data.py \
        --audio-samples 100 \
        --sensor-segments 50 \
        --output-dir 02_dataset/raw
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf


def generate_synthetic_audio(
    output_dir: Path,
    num_samples: int,
    sample_rate: int = 16000,
    duration: float = 10.0
) -> None:
    """Generate synthetic audio files for testing."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[synthetic] Generating {num_samples} audio samples...")
    
    for i in range(num_samples):
        # Generate random audio (white noise + some frequency components)
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Mix of frequencies to simulate different sounds
        if i % 2 == 0:
            # "Fire-like" - lower frequencies with crackling
            signal = np.sin(2 * np.pi * 200 * t) * 0.3
            signal += np.sin(2 * np.pi * 500 * t) * 0.2
            signal += np.random.normal(0, 0.1, len(t))  # Crackling noise
            label = "fire"
        else:
            # "Rain-like" - higher frequencies, more noise
            signal = np.sin(2 * np.pi * 1000 * t) * 0.2
            signal += np.random.normal(0, 0.15, len(t))
            label = "rain"
        
        # Normalize
        signal = signal / np.max(np.abs(signal)) * 0.8
        
        # Save
        filename = f"synthetic_{label}_{i:04d}.wav"
        filepath = output_dir / filename
        sf.write(filepath, signal, sample_rate)
    
    print(f"[synthetic] Audio samples saved to {output_dir}")


def generate_synthetic_sensor_data(
    output_dir: Path,
    num_segments: int
) -> None:
    """Generate synthetic sensor data for testing."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[synthetic] Generating {num_segments} sensor segments...")
    
    for i in range(num_segments):
        # Generate 30-minute time series at 1 Hz
        timestamps = pd.date_range(
            start=f"2019-{i%12+1:02d}-01 00:00:00",
            periods=1800,  # 30 minutes * 60 seconds
            freq="1S"
        )
        
        # Simulate sensor readings
        if i % 2 == 0:
            # "Pre-fire" conditions - temperature rising, humidity dropping
            temp = 25 + np.linspace(0, 10, 1800) + np.random.normal(0, 1, 1800)
            humidity = 60 - np.linspace(0, 20, 1800) + np.random.normal(0, 2, 1800)
            voc = 100 + np.linspace(0, 200, 1800) + np.random.normal(0, 10, 1800)
            pressure = 1013 + np.random.normal(0, 2, 1800)
            label = "pre_fire_alert"
        else:
            # "Nominal" conditions - stable
            temp = 20 + np.random.normal(0, 2, 1800)
            humidity = 50 + np.random.normal(0, 5, 1800)
            voc = 50 + np.random.normal(0, 5, 1800)
            pressure = 1013 + np.random.normal(0, 1, 1800)
            label = "nominal"
        
        # Create DataFrame
        df = pd.DataFrame({
            "timestamp": timestamps,
            "temperature_c": temp,
            "relative_humidity_pct": humidity,
            "voc_ppb": voc,
            "barometric_pressure_hpa": pressure,
        })
        df.set_index("timestamp", inplace=True)
        
        # Save as Parquet
        filename = f"synthetic_sensor_{label}_{i:04d}.parquet"
        filepath = output_dir / filename
        df.to_parquet(filepath)
    
    print(f"[synthetic] Sensor segments saved to {output_dir}")


def create_annotations(output_dir: Path) -> None:
    """Create annotation files for synthetic data."""
    audio_dir = output_dir / "audio_fire"
    sensor_dir = output_dir / "sensor_fire"
    
    # Audio annotations
    audio_files = sorted(audio_dir.glob("*.wav"))
    audio_annotations = []
    
    for i, filepath in enumerate(audio_files):
        label = "fire" if "fire" in filepath.name else "rain"
        audio_annotations.append({
            "event_id": f"SYNTH{i:04d}",
            "file_path": str(filepath.relative_to(output_dir.parent.parent)),
            "start_s": 0.0,
            "end_s": 10.0,
            "label": label,
            "confidence": 1.0,
            "source": "synthetic",
            "annotator": "synthetic_generator",
            "notes": "Synthetic test data",
        })
    
    # Sensor annotations
    sensor_files = sorted(sensor_dir.glob("*.parquet"))
    sensor_annotations = []
    
    for i, filepath in enumerate(sensor_files):
        label = "pre_fire_alert" if "pre_fire" in filepath.name else "nominal"
        df = pd.read_parquet(filepath)
        sensor_annotations.append({
            "segment_id": f"SSYNTH{i:04d}",
            "file_path": str(filepath.relative_to(output_dir.parent.parent)),
            "start_iso": df.index[0].isoformat(),
            "end_iso": df.index[-1].isoformat(),
            "label": label,
            "source": "synthetic",
            "annotator": "synthetic_generator",
            "notes": "Synthetic test data",
        })
    
    # Save annotations
    processed_dir = output_dir.parent / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    audio_df = pd.DataFrame(audio_annotations)
    audio_df.to_csv(processed_dir / "annotations.csv", index=False)
    
    sensor_df = pd.DataFrame(sensor_annotations)
    sensor_df.to_csv(processed_dir / "sensor_segment_annotations.csv", index=False)
    
    print(f"[synthetic] Annotations saved to {processed_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic test data.")
    parser.add_argument(
        "--audio-samples",
        type=int,
        default=100,
        help="Number of audio samples to generate",
    )
    parser.add_argument(
        "--sensor-segments",
        type=int,
        default=50,
        help="Number of sensor segments to generate",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("02_dataset/raw"),
        help="Output directory",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    print("=" * 60)
    print("Generating Synthetic Test Data")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This generates synthetic data for testing only!")
    print("   For real training, download actual datasets.")
    print()
    
    # Generate audio
    audio_dir = args.output_dir / "audio_fire"
    generate_synthetic_audio(audio_dir, args.audio_samples)
    
    # Generate sensor data
    sensor_dir = args.output_dir / "sensor_fire"
    generate_synthetic_sensor_data(sensor_dir, args.sensor_segments)
    
    # Create annotations
    create_annotations(args.output_dir)
    
    print()
    print("=" * 60)
    print("✅ Synthetic data generation complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Review generated files in:", args.output_dir)
    print("  2. Test preprocessing pipeline")
    print("  3. For real training, download actual datasets:")
    print("     python 02_dataset/scripts/dataset_fetch.py --source all")


if __name__ == "__main__":
    try:
        import soundfile as sf
    except ImportError:
        print("ERROR: soundfile not installed. Install with:")
        print("  pip install soundfile")
        exit(1)
    
    main()

