# EmberSense Problem Statement

## Wildfire Detection Challenge

Wildfires cause catastrophic damage when not detected early. Current detection methods rely on:
- Satellite imagery (too slow, ~30-60 min delay)
- Human observation (not scalable, limited coverage)
- Fixed camera systems (high power, limited range)

## Early Warning Indicators

Research shows that acoustic and environmental signals precede visible flames by minutes:
- **Acoustic**: Branch crackle, combustion pops, ignition sounds
- **Environmental**: Temperature spikes, humidity drops, VOC sensor spikes

## Solution: EmberSense

EmberSense is a multi-modal wildfire detection system that:
- Fuses acoustic and environmental sensor data
- Runs on low-power MCUs (<300KB memory)
- Provides <50ms inference latency
- Achieves ≥85% accuracy on early fire detection

## Target Deployment

- Remote forest monitoring stations
- Solar-powered, battery-backed
- LoRa uplink for alerts
- On-device inference (no cloud dependency)

See `01_planning/scope_definition.md` for detailed scope and assumptions.

