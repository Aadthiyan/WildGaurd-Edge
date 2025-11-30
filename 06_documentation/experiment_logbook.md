# EmberSense Experiment Logbook

## Week 1 Progress

### Task 1: Use Case, Scope & Metrics ✅
- **Date**: 2025-11-17
- **Status**: Complete
- **Deliverables**: 
  - Scope definition: `01_planning/scope_definition.md`
  - Metrics definition: `01_planning/metrics_definition.md`
- **Notes**: Established problem statement, objectives, success metrics (≥85% accuracy, <50ms latency, <300KB memory), and scope assumptions.

### Task 2: Dataset Research, Collection & Licensing ✅
- **Date**: 2025-11-17
- **Status**: Complete
- **Deliverables**:
  - Raw dataset structure: `02_dataset/raw/`
  - Licensing documentation: `02_dataset/licensing/dataset_licenses.md`
  - Dataset manifest: `02_dataset/raw/metadata_raw.json`
- **Notes**: Configured AudioSet, UrbanSound8K, and NASA/NOAA data sources with license verification.

### Task 3: Dataset Annotation, Preprocessing & Documentation ✅
- **Date**: 2025-11-17
- **Status**: Complete
- **Deliverables**:
  - Annotation schemas: `02_dataset/processed/annotations.csv`
  - Preprocessing notebook: `02_dataset/scripts/embersense_preprocessing.ipynb`
  - Dataset summary: `02_dataset/processed/dataset_summary.json`
- **Notes**: Created preprocessing pipeline for audio normalization (16kHz, 10s) and sensor feature extraction.

### Task 4: DSP & Feature Extraction Pipeline ✅
- **Date**: 2025-11-17
- **Status**: Complete
- **Deliverables**:
  - Edge Impulse config: `03_feature_pipeline/edge_impulse/project_export.json`
  - Feature previews: `03_feature_pipeline/edge_impulse/feature_previews/`
- **Notes**: Configured MFCC (13 + Δ), log-Mel spectrogram (64 bins), and sensor fusion (mean/std/min/max/slope) blocks.

### Task 5: Baseline Model Development ✅
- **Date**: 2025-11-17
- **Status**: Complete
- **Deliverables**:
  - Training logs: `04_models/logs/baseline_training.log`
  - Performance report: `04_models/baseline/baseline_performance.json`
  - Confusion matrix: `04_models/baseline/confusion_matrix.csv`
- **Notes**: Trained SVM (72%), Random Forest (70%), and CNN-Fusion (81%) baselines. All meet ≥70% accuracy target.

## Next Steps (Week 2)
- Advanced model development (CNN+GRU fusion)
- Model optimization (quantization, pruning)
- Evaluation and benchmarking

