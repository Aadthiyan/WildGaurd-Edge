# Dataset Summary

See `02_dataset/processed/dataset_summary.json` for detailed statistics.

## Overview
- **Audio events**: Fire-positive and negative (rain, wind, fauna) samples
- **Sensor segments**: Environmental traces (temperature, humidity, VOC, pressure)
- **Splits**: Train/Val/Test with seed=42 for reproducibility

## Collection Status
- AudioSet wildfire subset: Expected 1200 items
- UrbanSound8K negatives: Expected 8732 items  
- NASA/NOAA sensors: Expected 520 segments

## Preprocessing
- Audio: 16kHz mono, 10s fixed duration, LUFS normalized
- Sensors: 1Hz cadence, z-score normalized, 30s windows

