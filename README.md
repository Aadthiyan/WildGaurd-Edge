# EmberSense — Multi-Modal Wildfire Detection System

EmberSense is an MCU-friendly, multi-modal wildfire detection system that uses acoustic signals and environmental sensor data to identify early wildfire signatures. The project uses only simulated MCU environments (no physical hardware) and is built using Edge Impulse Studio, classical DSP libraries, and lightweight ML models.

## Project Structure

```
emberguard-agent/
├── 00_system/          # Agent persona, project rules, glossary
├── 01_planning/        # Scope, metrics, task breakdowns
├── 02_dataset/         # Raw data, processed data, splits, scripts
├── 03_feature_pipeline/ # DSP config, Edge Impulse, feature extraction
├── 04_models/          # Baseline, advanced, optimized models
├── 05_evaluation/      # Reports, reproducibility, evaluation notebooks
├── 06_documentation/   # README, problem statement, technical overview
└── 07_demo/            # Slides, video, submission materials
```

## Quick Start

1. **Dataset Preparation**: See `02_dataset/scripts/` for preprocessing scripts
2. **Feature Extraction**: Configure Edge Impulse using `03_feature_pipeline/edge_impulse/project_export.json`
3. **Model Training**: Use Edge Impulse Studio or CLI to train models (see `04_models/`)
4. **Evaluation**: Run evaluation scripts in `05_evaluation/`

## Success Metrics

- **Accuracy**: ≥ 85% macro F1 and event-level accuracy
- **Latency**: < 50ms inference time (simulated)
- **Memory**: < 300KB total (Flash + RAM)
- **Baseline**: ≥ 70% accuracy for baseline models

## Documentation

- **Problem Statement**: `06_documentation/problem_statement.md`
- **Technical Overview**: `06_documentation/technical_overview.md`
- **Experiment Logbook**: `06_documentation/experiment_logbook.md`
- **Citations**: `06_documentation/citations.md`

## License

All datasets used in this project are properly licensed:
- AudioSet: CC BY 4.0
- UrbanSound8K: CC BY 4.0
- NASA/NOAA: Public Domain

See `02_dataset/licensing/dataset_licenses.md` for details.

## Status

✅ Week 1 Complete: Dataset pipeline, DSP configuration, baseline models (SVM 72%, RF 70%, CNN-Fusion 81%)

## Contact

For questions or contributions, please refer to the project documentation in `06_documentation/`.

