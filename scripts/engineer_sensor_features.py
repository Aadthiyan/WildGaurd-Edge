import pandas as pd
import numpy as np
from pathlib import Path
import json

print('=' * 80)
print('PHASE 4: FEATURE ENGINEERING FROM SENSOR DATA')
print('=' * 80)

# Load sensor data
sensor_df = pd.read_csv('02_dataset/raw/sensor_fire/sensor_data.csv')
print(f'\n✅ Loaded {len(sensor_df)} sensor records')
print(f'   Date range: {sensor_df["date"].min()} to {sensor_df["date"].max()}')
print(f'   Locations: {sensor_df["location"].unique().tolist()}')

# Calculate fire-risk indicators
sensor_df['date'] = pd.to_datetime(sensor_df['date'])
sensor_df = sensor_df.sort_values('date')

sensor_features = {}

for location in sensor_df['location'].unique():
    loc_data = sensor_df[sensor_df['location'] == location].copy()
    
    # Rolling statistics (7-day windows)
    loc_data['temp_mean'] = loc_data['T2M'].rolling(7, min_periods=1).mean()
    loc_data['temp_std'] = loc_data['T2M'].rolling(7, min_periods=1).std()
    loc_data['temp_spike'] = loc_data['T2M'].diff().abs()
    
    loc_data['humidity_mean'] = loc_data['RH2M'].rolling(7, min_periods=1).mean()
    loc_data['humidity_min'] = loc_data['RH2M'].rolling(7, min_periods=1).min()
    loc_data['humidity_drop'] = loc_data['RH2M'].diff().abs()
    
    loc_data['pressure_std'] = loc_data['PS'].rolling(7, min_periods=1).std()
    loc_data['pressure_anomaly'] = (loc_data['PS'] - loc_data['PS'].rolling(7, min_periods=1).mean()).abs()
    
    # Composite risk score
    loc_data['fire_risk_score'] = (
        (100 - loc_data['humidity_min']) * 0.4 +
        (loc_data['temp_mean'] / 30 * 100) * 0.3 +
        (loc_data['pressure_std'] * 10) * 0.2 +
        (loc_data['temp_spike'] * 5) * 0.1
    ).clip(0, 100)
    
    sensor_features[location] = {
        'avg_temp': float(loc_data['T2M'].mean()),
        'avg_humidity': float(loc_data['RH2M'].mean()),
        'avg_fire_risk_score': float(loc_data['fire_risk_score'].mean()),
        'high_risk_days': int((loc_data['fire_risk_score'] > 70).sum()),
        'total_days': len(loc_data)
    }
    
    print(f'\n📊 {location}:')
    print(f'   Avg Temp: {loc_data["T2M"].mean():.1f}°C')
    print(f'   Avg Humidity: {loc_data["RH2M"].mean():.1f}%')
    print(f'   Fire Risk Score: {loc_data["fire_risk_score"].mean():.1f}/100')
    print(f'   High Risk Days: {(loc_data["fire_risk_score"] > 70).sum()}')
    
    # Save engineered features
    Path('03_feature_pipeline/sensor_features/').mkdir(parents=True, exist_ok=True)
    loc_data.to_csv(f'03_feature_pipeline/sensor_features/{location}_engineered.csv', index=False)

# Save summary
with open('03_feature_pipeline/sensor_features/summary.json', 'w') as f:
    json.dump(sensor_features, f, indent=2)

print('\n' + '=' * 80)
print('✅ SENSOR FEATURE ENGINEERING COMPLETE')
print('=' * 80)
print('\n📂 Features saved to: 03_feature_pipeline/sensor_features/')
print('\n🎯 Ready for CNN-Fusion and GRU-Temporal training!')
print('\nNext: Training advanced models (CNN-Fusion + GRU)...')
