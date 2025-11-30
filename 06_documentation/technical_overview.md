# EmberSense Technical Overview

## Architecture

### 1. Data Pipeline
- **Raw Data**: AudioSet (fire), UrbanSound8K (negatives), NASA/NOAA (sensors)
- **Preprocessing**: Audio normalization (16kHz, 10s), sensor interpolation (1Hz)
- **Splits**: Stratified train/val/test with seed=42

### 2. Feature Extraction (Edge Impulse)
- **MFCC**: 13 coefficients + deltas (32ms frames)
- **Spectrogram**: 64ms windows, log magnitude
- **Sensor Fusion**: Mean/std/min/max/slope per 30s window

### 3. Models
- **Baseline**: SVM (72%), Random Forest (70%), CNN-Fusion (83%)
- **Advanced**: CNN+GRU fusion (target ≥85%)
- **Optimized**: Quantized INT8, pruned variants

### 4. Deployment
- **Target MCU**: Cortex-M4F @ 80MHz
- **Constraints**: <50ms latency, <300KB memory
- **Simulation**: Edge Impulse MCU profiler

## Technology Stack
- **DSP**: librosa, scipy
- **ML**: Edge Impulse Studio, TensorFlow Lite
- **Data**: pandas, numpy, pyarrow
- **Validation**: Custom Python scripts

See `03_feature_pipeline/` and `04_models/` for implementation details.

