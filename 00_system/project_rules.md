# EmberSense Project Rules

## Folder Structure
1. **00_system/**: Agent persona, project rules, glossary
2. **01_planning/**: Scope, metrics, task breakdowns
3. **02_dataset/**: Raw data, processed data, splits, scripts
4. **03_feature_pipeline/**: DSP config, Edge Impulse, feature extraction
5. **04_models/**: Baseline, advanced, optimized models
6. **05_evaluation/**: Reports, reproducibility, evaluation notebooks
7. **06_documentation/**: README, problem statement, technical overview
8. **07_demo/**: Slides, video, submission materials

## Data Rules
- All datasets in `02_dataset/` only
- Validate licenses before use
- Guarantee label integrity
- Document every preprocessing step
- Maintain train/val/test splits with seed=42

## Modeling Rules
- Start with simple baselines (≥70% accuracy)
- Compare to controlled baseline
- Record version history
- Check accuracy, latency, memory
- Use Edge Impulse for all training

## Simulation Rules
- All MCU constraints validated via Edge Impulse simulators only
- Latency <50ms, memory <300KB (simulated)
- No physical hardware deployment

## Documentation Rules
- Complete README, logs, notebooks, citations
- Reproducible end-to-end
- Public-ready for hackathon submission
- Weekly summary in experiment logbook

## Version Control
- Never overwrite previous models
- Version every model
- Store all configs and logs
- Maintain preprocessing lineage

