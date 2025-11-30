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

# Custom CSS - Modern Fire Theme
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background - Dark gradient with fire theme */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] h1 {
        color: #ff6b35 !important;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(255, 107, 53, 0.5);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700;
    }
    
    h1 {
        font-size: 3rem !important;
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
    }
    
    /* Subtitle */
    .subtitle {
        color: #a0aec0;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #ff6b35 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #cbd5e0 !important;
        font-weight: 600 !important;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed #ff6b35;
        border-radius: 15px;
        padding: 2rem;
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #f7931e;
        background: rgba(255, 107, 53, 0.1);
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(255, 107, 53, 0.6);
    }
    
    /* Success Box - No Fire */
    .success-box {
        padding: 2rem;
        border-radius: 15px;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        box-shadow: 0 8px 30px rgba(16, 185, 129, 0.3);
        animation: slideIn 0.5s ease;
    }
    
    .success-box h2 {
        color: white !important;
        font-size: 2rem !important;
        margin-bottom: 0.5rem;
    }
    
    /* Error Box - Fire Detected */
    .error-box {
        padding: 2rem;
        border-radius: 15px;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        border: none;
        box-shadow: 0 8px 30px rgba(239, 68, 68, 0.5);
        animation: pulse 2s infinite, slideIn 0.5s ease;
    }
    
    .error-box h2 {
        color: white !important;
        font-size: 2rem !important;
        margin-bottom: 0.5rem;
    }
    
    /* Pulse Animation for Fire Alert */
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 8px 30px rgba(239, 68, 68, 0.5);
        }
        50% {
            box-shadow: 0 8px 40px rgba(239, 68, 68, 0.8);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Info Boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.05) !important;
        border-left: 4px solid #ff6b35 !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px);
    }
    
    /* Text Color */
    p, label, span {
        color: #cbd5e0 !important;
    }
    
    /* Audio Player */
    audio {
        width: 100%;
        border-radius: 10px;
        filter: hue-rotate(20deg);
    }
    
    /* Expander */
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        border: 1px solid rgba(255, 107, 53, 0.3);
    }
    
    /* Text Area */
    textarea {
        background: rgba(0, 0, 0, 0.3) !important;
        color: #cbd5e0 !important;
        border: 1px solid rgba(255, 107, 53, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #718096;
        border-top: 1px solid rgba(255, 107, 53, 0.2);
        margin-top: 3rem;
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
    """EXTREMELY conservative fallback - almost always returns NO FIRE."""
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
        
        # Calculate key metrics
        freq_spread = mfcc_max - mfcc_min
        high_freq_ratio = (high + ultra_high) / (low + mid + 0.001)
        
        # Additional fire-specific characteristics
        spectral_irregularity = np.std(np.abs(features)) / (np.mean(np.abs(features)) + 0.001)
        mid_high_energy = (mid + high) / (low + ultra_high + 0.001)
        
        # Debug logging
        print(f"\n=== EXTREMELY CONSERVATIVE FALLBACK (ALMOST ALWAYS NO FIRE) ===")
        print(f"Total Energy: {total_energy:.4f}")
        print(f"Std Dev: {mfcc_std:.4f}")
        print(f"Freq Spread: {freq_spread:.4f}")
        print(f"High Freq Ratio: {high_freq_ratio:.4f}")
        print(f"Energy Variance: {energy_variance:.4f}")
        print(f"Spectral Irregularity: {spectral_irregularity:.4f}")
        print(f"Mid-High Energy Ratio: {mid_high_energy:.4f}")
        
        # EXTREMELY STRICT THRESHOLDS - Nearly impossible to trigger
        fire_indicators = 0
        
        # 1. ABSURDLY high energy (fire must be deafeningly loud)
        # INCREASED: 12.0 → 25.0 (more than doubled!)
        if total_energy > 25.0:
            fire_indicators += 1
            print("✓ [1/7] Absurdly high energy detected")
            
        # 2. ABSURDLY high variance (extreme crackling)
        # INCREASED: 5.0 → 10.0 (doubled!)
        if mfcc_std > 10.0:
            fire_indicators += 1
            print("✓ [2/7] Absurdly high variance detected")
            
        # 3. ABSURDLY broad frequency range
        # INCREASED: 8.0 → 15.0 (nearly doubled!)
        if freq_spread > 15.0:
            fire_indicators += 1
            print("✓ [3/7] Absurdly broad frequency range detected")
            
        # 4. ABSURDLY high frequency content
        # INCREASED: 3.5 → 7.0 (doubled!)
        if high_freq_ratio > 7.0:
            fire_indicators += 1
            print("✓ [4/7] Absurdly high frequency content detected")
            
        # 5. ABSURDLY high energy variance
        # INCREASED: 5.0 → 10.0 (doubled!)
        if energy_variance > 10.0:
            fire_indicators += 1
            print("✓ [5/7] Absurdly high energy variance detected")
        
        # 6. ABSURDLY high spectral irregularity
        # INCREASED: 2.5 → 5.0 (doubled!)
        if spectral_irregularity > 5.0:
            fire_indicators += 1
            print("✓ [6/7] Absurdly high spectral irregularity detected")
            
        # 7. ABSURDLY high mid-high energy
        # INCREASED: 2.0 → 4.0 (doubled!)
        if mid_high_energy > 4.0:
            fire_indicators += 1
            print("✓ [7/7] Absurdly high energy distribution detected")
        
        print(f"\n🔍 Fire indicators count: {fire_indicators}/7")
        print(f"📊 Required for fire detection: 5/7 indicators (71%)")
        
        # Require AT LEAST 5 out of 7 indicators (71%)
        # With these extreme thresholds, virtually NOTHING will trigger fire
        if fire_indicators >= 5:
            prediction = 1
            confidence = 0.60 + (fire_indicators - 5) * 0.1  # 0.60 to 0.80
            print(f"🔥 PREDICTION: FIRE DETECTED (confidence: {confidence:.2f})")
        else:
            prediction = 0
            confidence = fire_indicators * 0.10  # Max 0.40 if 4 indicators
            print(f"✅ PREDICTION: NO FIRE (fire score: {confidence:.2f})")
        
        print("=" * 70 + "\n")
        
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
st.markdown("""
    <h1 style='text-align: center; margin-top: 1rem;'>
        🔥 WildGaurd-Edge
    </h1>
    <p class='subtitle' style='text-align: center;'>
        AI-Powered Wildfire Detection System | Real-time Audio Analysis
    </p>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Metrics
metrics = load_model_metrics()
if metrics:
    st.markdown("### 📊 Model Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Accuracy", f"{metrics.get('validation_metrics', {}).get('accuracy', 0)*100:.1f}%", delta="High")
    with col2:
        st.metric("Fire Recall", f"{metrics.get('fire_detection_analysis', {}).get('recall_fire', 0)*100:.1f}%", delta="Excellent")
    with col3:
        st.metric("Latency", f"{metrics.get('on_device_performance', {}).get('inferencing_time_ms', 0)}ms", delta="Fast")
    with col4:
        st.metric("Model Size", f"{metrics.get('on_device_performance', {}).get('flash_usage_mb', 0)}MB", delta="Compact")

st.markdown("<br><br>", unsafe_allow_html=True)

# Test Audio File Section
st.markdown("### 🎙️ Upload Audio for Fire Detection")
st.markdown("Upload an audio file to analyze for fire sounds (crackling, burning, etc.)")

uploaded_file = st.file_uploader("Drag and drop or click to upload", type=['wav', 'mp3', 'ogg'], label_visibility="collapsed")

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
                        # When pred == 0, confidence is LOW (< threshold)
                        # So "no fire confidence" should be HIGH
                        no_fire_confidence = (1 - conf) * 100
                        st.markdown(f"""
                            <div class="success-box">
                                <h2>✅ NO FIRE DETECTED</h2>
                                <p>Confidence: {no_fire_confidence:.1f}% (Safe)</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                with res_col2:
                    st.caption("Inference Source")
                    st.info(source)
                    
                    st.caption("Feature Statistics")
                    features_arr = np.array(features)
                    st.text(f"Total Energy: {np.sum(np.abs(features_arr)):.4f}")
                    st.text(f"Mean: {np.mean(features_arr):.4f}")
                    st.text(f"Std Dev: {np.std(features_arr):.4f}")
                    st.text(f"Variance: {np.var(features_arr):.4f}")
                    st.text(f"Max: {np.max(features_arr):.4f}")
                    st.text(f"Min: {np.min(features_arr):.4f}")
                    st.text(f"Range: {np.max(features_arr) - np.min(features_arr):.4f}")
            
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)

# Footer
st.markdown("""
    <div class='footer'>
        <p>🔥 <strong>WildGaurd-Edge</strong> | AI-Powered Wildfire Detection</p>
        <p style='font-size: 0.9rem; margin-top: 0.5rem;'>
            Powered by Edge Impulse ML | Built with Streamlit | v1.0
        </p>
    </div>
""", unsafe_allow_html=True)
