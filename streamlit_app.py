import streamlit as st
import os
import json
import numpy as np
import librosa
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import time

# Configuration
CONFIG = {
    'sr': 16000,
    'n_mfcc': 13,
}

EI_MODEL_SERVER = 'http://127.0.0.1:5001'
TEMP_DIR = 'temp_uploads'
os.makedirs(TEMP_DIR, exist_ok=True)

def start_node_server():
    """Start the Node.js model server if it's not running."""
    # Check if already running
    try:
        requests.get(f'{EI_MODEL_SERVER}/api/health', timeout=1)
        return True
    except:
        pass

    try:
        node_dir = Path("node")
        if not node_dir.exists():
            print("Node directory not found")
            return False

        # Install dependencies if needed
        if not (node_dir / "node_modules").exists():
            with st.spinner("Installing model server dependencies..."):
                subprocess.run(["npm", "install"], cwd=node_dir, check=True, shell=True)

        # Start server with logging
        log_file = open("node_server.log", "w")
        process = subprocess.Popen(
            ["node", "server.js"], 
            cwd=node_dir, 
            shell=True,
            stdout=log_file,
            stderr=subprocess.STDOUT
        )
        
        # Wait for startup (up to 15 seconds)
        progress_text = "Starting AI Model Server..."
        my_bar = st.progress(0, text=progress_text)
        
        for i in range(15):
            try:
                requests.get(f'{EI_MODEL_SERVER}/api/health', timeout=1)
                my_bar.empty()
                return True
            except:
                time.sleep(1)
                my_bar.progress((i + 1) / 15, text=progress_text)
        
        my_bar.empty()
        print("Timeout waiting for node server")
        return False
    except Exception as e:
        print(f"Failed to start node server: {e}")
        return False

# Page Config
st.set_page_config(
    page_title="WildGaurd-Edge",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Server
if 'server_started' not in st.session_state:
    st.session_state.server_started = start_node_server()

# Debug: Show Node Logs
with st.sidebar.expander("🛠️ Debug Info"):
    if os.path.exists("node/node_server.log"):
        with open("node/node_server.log", "r") as f:
            st.text_area("Node Server Logs", f.read(), height=200)
    else:
        st.info("No server logs found.")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    </style>
    """, unsafe_allow_html=True)

def load_model_metrics():
    try:
        with open('04_models/baseline/baseline_performance.json', 'r') as f:
            return json.load(f)
    except:
        return None

def extract_features_for_ei_model(audio_path):
    """Extract features exactly as Edge Impulse expects them."""
    try:
        y, sr = librosa.load(audio_path, sr=CONFIG['sr'])
        
        # Extract MFCC (13 coefficients)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=CONFIG['n_mfcc'])
        mfcc_mean = np.mean(mfcc, axis=1)
        
        # Extract Mel-Frequency Energy
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64)
        mel_energy = np.mean(mel_spec, axis=1)
        
        # Combine features
        combined_features = np.concatenate([
            mfcc_mean,
            mel_energy[:8]
        ])
        
        return combined_features.tolist(), True
    except Exception as e:
        st.error(f"Feature extraction error: {e}")
        return None, False

def predict_fire_fallback(features):
    """Improved fallback Python-based prediction if Node server is down."""
    if features is None:
        return None, None
    
    try:
        features = np.array(features)
        
        # Calculate comprehensive statistics
        mfcc_mean = np.mean(features)
        mfcc_std = np.std(features)
        mfcc_max = np.max(features)
        mfcc_min = np.min(features)
        
        # Frequency band analysis
        low = np.mean(np.abs(features[0:3]))      # Low frequencies
        mid = np.mean(np.abs(features[3:7]))      # Mid frequencies  
        high = np.mean(np.abs(features[7:10]))    # High frequencies
        ultra_high = np.mean(np.abs(features[10:]))  # Ultra high frequencies
        
        # Total energy
        total_energy = np.sum(np.abs(features))
        energy_variance = np.var(features)
        
        # Fire detection score (0-1)
        fire_score = 0.0
        
        # 1. High energy content (fire is loud) - 20%
        if total_energy > 2.0:
            fire_score += 0.20
        elif total_energy > 1.0:
            fire_score += 0.10
            
        # 2. High variance (fire crackles and pops) - 25%
        if mfcc_std > 1.0:
            fire_score += 0.25
        elif mfcc_std > 0.6:
            fire_score += 0.15
            
        # 3. Broadband energy (fire has wide frequency range) - 20%
        freq_spread = mfcc_max - mfcc_min
        if freq_spread > 2.0:
            fire_score += 0.20
        elif freq_spread > 1.2:
            fire_score += 0.10
            
        # 4. High frequency content (crackling sounds) - 20%
        high_freq_ratio = (high + ultra_high) / (low + mid + 0.001)
        if high_freq_ratio > 0.8:
            fire_score += 0.20
        elif high_freq_ratio > 0.5:
            fire_score += 0.10
            
        # 5. Energy variance (non-stationary signal) - 15%
        if energy_variance > 1.0:
            fire_score += 0.15
        elif energy_variance > 0.5:
            fire_score += 0.08
            
        # Normalize confidence
        confidence = min(max(fire_score, 0.0), 1.0)
        
        # Apply threshold
        prediction = 1 if confidence > 0.5 else 0
        
        return prediction, confidence
        
    except Exception as e:
        print(f"Fallback prediction error: {e}")
        return None, None

def predict_with_ei_server(features):
    """Call Node.js server for prediction."""
    try:
        response = requests.post(
            f'{EI_MODEL_SERVER}/api/predict',
            json={'features': features},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'success':
                return (
                    result['prediction'],
                    result['confidence'],
                    result['prediction_text'],
                    'Edge Impulse (98.92% accuracy)'
                )
        else:
            print(f"Server returned status code: {response.status_code}")
    except requests.exceptions.Timeout:
        print("Node.js server timeout - server may be slow or unresponsive")
    except requests.exceptions.ConnectionError:
        print("Node.js server connection error - server may not be running")
    except Exception as e:
        print(f"Error calling Edge Impulse server: {e}")
    
    # Fallback
    pred, conf = predict_fire_fallback(features)
    pred_text = 'FIRE DETECTED 🔥' if pred == 1 else 'NO FIRE ✅'
    return pred, conf, pred_text, 'Fallback (Python - Improved)'

# Sidebar
with st.sidebar:
    st.title("🔥 WildGaurd-Edge")
    st.markdown("---")
    
    # Server Status
    st.subheader("System Status")
    try:
        resp = requests.get(f'{EI_MODEL_SERVER}/api/health', timeout=1)
        if resp.status_code == 200:
            st.success("✅ Model Server Online")
        else:
            st.warning("⚠️ Model Server Offline")
            if st.button("Try Restarting Server"):
                st.session_state.server_started = start_node_server()
                st.rerun()
    except:
        st.error("❌ Model Server Unreachable")
        st.caption("Using Python fallback (lower accuracy)")
        if st.button("Try Restarting Server"):
            st.session_state.server_started = start_node_server()
            st.rerun()

    st.markdown("---")
    st.info("This interface allows you to test the fire detection model with audio files.")

# Main Content
st.title("Wildfire Detection Dashboard")
st.markdown("Real-time audio analysis for early fire detection.")

# Metrics
metrics = load_model_metrics()
if metrics:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Accuracy", f"{metrics.get('validation_metrics', {}).get('accuracy', 0)*100:.1f}%")
    with col2:
        st.metric("Recall", f"{metrics.get('fire_detection_analysis', {}).get('recall_fire', 0)*100:.1f}%")
    with col3:
        st.metric("Latency", f"{metrics.get('on_device_performance', {}).get('inferencing_time_ms', 0)}ms")
    with col4:
        st.metric("Model Size", f"{metrics.get('on_device_performance', {}).get('flash_usage_mb', 0)}MB")

# Test Audio File Section
st.header("🎙️ Test Audio File")

uploaded_file = st.file_uploader("Upload WAV, MP3, or OGG file", type=['wav', 'mp3', 'ogg'])

if uploaded_file:
    # Save temp file
    temp_path = os.path.join(TEMP_DIR, uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Audio Player
    st.audio(uploaded_file)
    
    if st.button("Analyze Audio", key="analyze_btn"):
        with st.spinner("Extracting features and analyzing..."):
            # Extract features
            features, success = extract_features_for_ei_model(temp_path)
            
            if success:
                # Predict
                pred, conf, text, source = predict_with_ei_server(features)
                
                # Display Result
                st.markdown("### Analysis Results")
                
                res_col1, res_col2 = st.columns([2, 1])
                
                with res_col1:
                    if pred == 1:
                        st.markdown(f"""
                            <div class="error-box">
                                <h2>🔥 FIRE DETECTED</h2>
                                <p>Confidence: {conf*100:.1f}%</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="success-box">
                                <h2>✅ NO FIRE DETECTED</h2>
                                <p>Confidence: {(1-conf)*100:.1f}% (Safe)</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                with res_col2:
                    st.caption("Inference Source")
                    st.info(source)
                    
                    st.caption("Feature Stats")
                    st.text(f"Mean Energy: {np.mean(features):.4f}")
                    st.text(f"Variance: {np.var(features):.4f}")
            
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)

# Footer
st.markdown("---")
st.caption("WildGaurd-Edge | Streamlit Dashboard | v1.0")
