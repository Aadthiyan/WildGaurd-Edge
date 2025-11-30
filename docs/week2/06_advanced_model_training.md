# Task 6 – Advanced Model Training & Research Iteration

## Description
Develop deeper CNNs, sensor-fusion-based models, anomaly detection, and improved DSP configs to push beyond baseline performance toward the ≥85% accuracy target.

## Deliverables

### 1. Experiment Logs ✅
- **Location**: `04_models/advanced/experiments/`
- **Format**: JSON metadata + training logs
- **Contents**: 
  - Experiment ID, timestamps, status
  - Model configuration
  - Training hyperparameters
  - Final metrics (accuracy, latency, memory)

### 2. Model Versioning ✅
- **Location**: `04_models/advanced/versions/`
- **Structure**: Each version in separate directory with:
  - `version_metadata.json` - Version info, config, results
  - `model.h5` or `model.eim` - Model artifacts
  - Performance metrics

### 3. Comparative Report ✅
- **Location**: `05_evaluation/reports/comparative_report.md`
- **Contents**:
  - Side-by-side comparison of all models
  - Accuracy, latency, memory metrics
  - Target achievement status
  - Recommendations

## Dependencies
- **Edge Impulse Studio**: Primary training platform
- **PyTorch/TensorFlow**: Via BYOM (Bring Your Own Model) for custom architectures
- **Processed dataset**: From Week 1 (`02_dataset/processed/`)
- **Feature pipeline**: From Week 1 (`03_feature_pipeline/`)

## Model Variants

### v2.0 - Deep CNN-Fusion
- Enhanced CNN with attention mechanisms
- Multi-scale feature extraction
- Target: ≥85% accuracy, <50ms latency, <300KB memory

### v2.1 - GRU-Temporal Fusion
- Bidirectional GRU for temporal modeling
- Better sensor sequence understanding
- Target: Improved temporal pattern recognition

### v2.2 - Anomaly Detector
- Autoencoder-based anomaly detection
- Unsupervised pre-training + supervised fine-tuning
- Target: Lower false positive rate (<5%)

### v3.0 - Optimized DSP Config
- Improved MFCC/spectrogram parameters
- Enhanced feature discriminability
- Target: Better feature quality scores

## Usage

### Training a Model
```bash
python 04_models/advanced/train_advanced.py \
    --config 04_models/advanced/configs/cnn_fusion_v2.json \
    --experiment-name exp_001 \
    --version v2.0 \
    --method edge_impulse \
    --edge-impulse-project-id <PROJECT_ID>
```

### Tracking Experiments
```bash
python 04_models/advanced/experiment_tracker.py \
    --experiment-dir 04_models/advanced/experiments/exp_001 \
    --metrics accuracy=0.87 latency_ms=42 memory_kb=285
```

### Comparing Models
```bash
python 04_models/advanced/compare_models.py \
    --baseline 04_models/baseline/baseline_performance.json \
    --advanced 04_models/advanced/versions/v2.0/version_metadata.json \
    --output 05_evaluation/reports/comparative_report.md
```

## Tests

### Accuracy Comparison
- Compare all models against baseline (≥70%)
- Target: Advanced models ≥85%
- Statistical significance testing

### Memory Comparison
- Flash + RAM usage for each model
- Target: <300KB total
- Edge Impulse profiler reports

### Latency Comparison
- Inference time in Edge Impulse simulator
- Target: <50ms end-to-end
- MCU: Cortex-M4F @ 80MHz

### Test Command
```bash
python 04_models/advanced/compare_models.py \
    --baseline 04_models/baseline/baseline_performance.json \
    --advanced 04_models/advanced/versions/*/version_metadata.json \
    --output 05_evaluation/reports/comparative_report.md \
    --csv 05_evaluation/reports/model_comparison.csv
```

## Status
- ✅ Experiment framework setup
- ✅ Model training scripts
- ✅ Versioning system
- ✅ Comparative analysis tools
- ⏳ Model training (pending Edge Impulse API key)
- ⏳ Performance evaluation

