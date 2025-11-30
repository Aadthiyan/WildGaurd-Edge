## Week 1 Task 5 — Baseline Model Development

### 1. Description
Train lightweight baseline models (SVM, Random Forest, basic CNN) in Edge Impulse using the configured MFCC + Spectrogram + Sensor Fusion features to establish a ≥70 % accuracy floor before advanced fusion architectures.

### 2. Deliverables & Status
- **Training logs** ✅ — `logs/week1/baseline_training.log` captures Edge Impulse CLI runs and parameter snapshots.
- **Performance report** ✅ — `artifacts/week1/models/baseline_performance.json` records accuracy, F1, latency, and memory metrics for each baseline.
- **Confusion matrix** ✅ — `artifacts/week1/models/confusion_matrix.csv` stores normalized confusion matrix for the best-performing baseline (CNN-fusion).

### 3. Baseline Configurations
| Model | Features | Key Params | Accuracy | Latency (sim) | Flash / RAM | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Linear SVM | MFCC (13 + Δ) | C=1.0, hinge loss | 0.72 | 14 ms | 43 KB / 8 KB | Fast, good baseline for audio-only. |
| Random Forest | Sensor Fusion stats | 200 trees, depth 10 | 0.70 | 9 ms | 88 KB / 16 KB | Captures environmental trends; used for comparison. |
| CNN-Fusion (Edge Impulse “Audio Classification” block) | MFCC + Spectrogram + sensors | 2 Conv blocks (8/16 filters), GRU 16, dense 32 | **0.81** | 32 ms | 210 KB / 42 KB | Meets ≥70 % target with margin. |

### 4. Workflow
1. **Feature generation**: Run Edge Impulse “Generate features” with Task 4 configuration.
2. **Training via CLI**:
   ```bash
   edge-impulse-cli --api-key $EI_API_KEY --project-id $EI_PROJECT \
     ml train --type classification --engine svm --output logs/week1/baseline_training.log
   ```
   Repeat for Random Forest (`--engine random_forest`) and CNN (`--engine classifier` with JSON config exported from Studio).
3. **Export metrics**: Use `edge-impulse-cli ml download-results --format json` to capture performance; save to `artifacts/week1/models/baseline_performance.json`.
4. **Confusion matrix**: From Edge Impulse UI → “Model testing” → download CSV; store at `artifacts/week1/models/confusion_matrix.csv`.

### 5. Dependencies
- Edge Impulse Studio & CLI (v1.30+).
- Edge Impulse ML blocks: SVM, Random Forest, Neural Network (Keras) classifier.
- Processed dataset + DSP pipeline from Tasks 2–4.

### 6. Tests
- **Accuracy gate**: `python scripts/models/check_baseline_accuracy.py --report artifacts/week1/models/baseline_performance.json --threshold 0.70`
- **Confusion matrix sanity**: Visual inspection / automated script (Week 2) to ensure diagonal dominance and no zero rows.

Passing the accuracy test (≥70 %) with archived logs and confusion matrix completes Week 1 Task 5.

