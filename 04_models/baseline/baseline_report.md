# Baseline Model Performance Report

## Summary
Three baseline models were trained in Edge Impulse to establish a ≥70% accuracy floor:

| Model | Features | Accuracy | F1 Macro | Latency | Flash | RAM |
|-------|----------|----------|----------|---------|-------|-----|
| Linear SVM | MFCC | 72% | 70% | 14.2 ms | 43 KB | 8 KB |
| Random Forest | Sensor Fusion | 70% | 68% | 9.1 ms | 88 KB | 16 KB |
| CNN-Fusion | MFCC+Spec+Sensor | **83%** | **81%** | 32.4 ms | 210 KB | 42 KB |

## Best Model
**CNN-Fusion (cnn_fusion_v1)** achieves 83% accuracy and meets all baseline targets.

See `baseline_performance.json` for detailed metrics and `confusion_matrix.csv` for class-wise performance.

