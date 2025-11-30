## EmberSense Success Metrics

### 1. Success Metrics
- **Accuracy**: ≥ 85 % macro F1 and event-level accuracy on held-out validation segments.
- **Latency**: < 50 ms inference time in Edge Impulse simulator for target MCU class (Cortex-M4F @ 80 MHz).
- **Memory footprint**: < 300 KB total (Flash + RAM) for the deployed model bundle.
- **Data integrity**: 100 % traceable preprocessing lineage; zero label leakage across train/val/test.

### 2. Baseline Model Targets
- **Minimum accuracy**: ≥ 70 % for baseline models (SVM, Random Forest, basic CNN)
- **Target accuracy**: ≥ 85 % for advanced fusion models
- **False positive rate**: < 5 % on negative class (rain, wind, fauna)
- **False negative rate**: < 10 % on fire-positive events

### 3. Performance Benchmarks
- **Training time**: < 2 hours for baseline models on Edge Impulse
- **Feature extraction**: < 10 ms per 10-second audio clip
- **Model size**: < 300 KB Flash, < 50 KB RAM
- **Inference latency**: < 50 ms end-to-end (feature extraction + model inference)

### 4. Evaluation Criteria
- **Reproducibility**: All experiments must be reproducible with fixed seeds (seed=42)
- **Documentation**: Complete logs, configs, and artifacts for every model version
- **Compliance**: All datasets must have verified licenses and attribution
- **Testing**: Automated tests for accuracy gates, label consistency, and feature quality

### 5. Tests — Peer-Review Checklist
1. **Traceability**: Does every dataset entry map to a license source and preprocessing log?
2. **Metric coverage**: Are accuracy, latency, memory targets explicitly tied to evaluation scripts and Edge Impulse profiles?
3. **Assumption validation**: Are sensing/operational assumptions documented and justified via references?
4. **Reproducibility**: Can another engineer recreate the dataset splits and DSP features from the documented pipeline without external knowledge?
5. **Risk review**: Are false-positive/false-negative impacts discussed, with mitigation strategies (e.g., multi-frame voting)?

Completion of this checklist by an independent reviewer constitutes acceptance for Week 1, Task 1.

