# Advanced Model Training & Research Iteration

This directory contains advanced model architectures, training experiments, and versioning for EmberSense.

## Structure
- `experiments/` - Individual experiment logs and results
- `versions/` - Versioned model artifacts and metadata
- `logs/` - Training logs and experiment tracking
- `configs/` - Model configuration files
- `checkpoints/` - Model checkpoints during training

## Model Variants

### v2.0 - Deep CNN-Fusion
- Enhanced CNN architecture with attention
- Multi-scale feature extraction
- Target: ≥85% accuracy

### v2.1 - GRU-Temporal Fusion
- Temporal modeling for sensor sequences
- Bidirectional GRU layers
- Target: Better temporal pattern recognition

### v2.2 - Anomaly Detector
- Unsupervised anomaly detection
- Early warning system
- Target: Lower false positive rate

### v3.0 - Optimized DSP Config
- Improved MFCC parameters
- Enhanced spectrogram features
- Target: Better feature discriminability

## Usage

### Training a new model
```bash
python 04_models/advanced/train_advanced.py \
    --config 04_models/advanced/configs/cnn_fusion_v2.json \
    --experiment-name exp_001 \
    --version v2.0
```

### Comparing models
```bash
python 04_models/advanced/compare_models.py \
    --baseline 04_models/baseline/baseline_performance.json \
    --advanced 04_models/advanced/versions/v2.0/performance.json \
    --output 05_evaluation/reports/comparative_report.md
```

