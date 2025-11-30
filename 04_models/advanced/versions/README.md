# Model Versions

This directory contains versioned model artifacts and metadata.

## Versioning Scheme
- **v2.0+**: Advanced models (Week 2)
- **v1.0**: Baseline models (Week 1)

## Directory Structure
Each version directory contains:
- `version_metadata.json` - Version info, config, results
- `model.h5` or `model.eim` - Model artifacts (if available)
- `performance.json` - Performance metrics

## Current Versions

### v2.0 - Deep CNN-Fusion
- Status: Pending training
- Target: ≥85% accuracy, <50ms latency, <300KB memory

### v2.1 - GRU-Temporal Fusion
- Status: Pending training
- Target: Better temporal pattern recognition

### v2.2 - Anomaly Detector
- Status: Pending training
- Target: Lower false positive rate

