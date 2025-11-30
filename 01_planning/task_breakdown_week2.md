# Week 2 Task Breakdown

## Task 6: Advanced Model Training & Research Iteration

### Description
Develop deeper CNNs, sensor-fusion-based models, anomaly detection, and improved DSP configs to push beyond baseline performance toward the ≥85% accuracy target.

### Deliverables
- **Experiment logs**: Detailed logs of all training runs, hyperparameters, and results
- **Model versioning**: Systematic versioning of all model variants with metadata
- **Comparative report**: Side-by-side comparison of all models (baseline + advanced) across accuracy, memory, and latency metrics

### Dependencies
- Edge Impulse Studio (primary training platform)
- PyTorch/TensorFlow via BYOM (Bring Your Own Model) for custom architectures
- Processed dataset from Week 1
- Feature pipeline from Week 1

### Models to Develop
1. **Deep CNN-Fusion v2**: Enhanced CNN with more layers, attention mechanisms
2. **GRU-Temporal Fusion**: Temporal modeling for sensor sequences
3. **Anomaly Detector**: Unsupervised/semi-supervised anomaly detection for early warning
4. **Improved DSP Configs**: Optimized MFCC/spectrogram parameters based on feature analysis

### Tests
- Compare accuracy (target ≥85%)
- Compare memory footprint (target <300KB)
- Compare latency (target <50ms)
- Statistical significance testing between model variants

### Status
- [ ] Experiment framework setup
- [ ] Model training scripts
- [ ] Versioning system
- [ ] Comparative analysis
