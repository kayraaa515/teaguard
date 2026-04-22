import streamlit as st
from PIL import Image
import folium
from streamlit_folium import st_folium
import datetime
import pandas as pd
import cv2
import numpy as np
import json
import os
from streamlit.components.v1 import html

st.set_page_config(page_title="TeaGuard", page_icon="🌿", layout="wide")

# ---- Cool CSS ----
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * { font-family: 'Poppins', sans-serif; }
    
    .main { background: #0a0a0a; }
    
    .stApp {
        background: linear-gradient(135deg, #0d1b0f 0%, #1a2e1c 50%, #0d1b0f 100%);
        color: white;
    }
    
    h1, h2, h3 { color: #4ade80 !important; }
    
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 5px;
        gap: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #9ca3af;
        border-radius: 10px;
        font-weight: 600;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #16a34a, #15803d) !important;
        color: white !important;
    }
    
    .stTextInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(74,222,128,0.3) !important;
        border-radius: 10px !important;
        color: white !important;
        padding: 12px !important;
    }
    
    .stTextInput input:focus {
        border-color: #4ade80 !important;
        box-shadow: 0 0 0 2px rgba(74,222,128,0.2) !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #16a34a, #15803d) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        width: 100% !important;
        transition: all 0.3s !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(22,163,74,0.4) !important;
    }
    
    .stMetric {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(74,222,128,0.2) !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    
    .stMetric label { color: #9ca3af !important; }
    .stMetric [data-testid="metric-container"] { color: #4ade80 !important; }
    
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        border: none !important;
    }
    
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    .stSlider [data-baseweb="slider"] {
        color: #4ade80 !important;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---- Hero Header ----
st.markdown("""
<div style="
    text-align: center;
    padding: 40px 20px;
    background: linear-gradient(135deg, rgba(22,163,74,0.15), rgba(21,128,61,0.1));
    border-radius: 20px;
    border: 1px solid rgba(74,222,128,0.2);
    margin-bottom: 30px;
">
    <div style="font-size: 60px; margin-bottom: 10px;">🌿</div>
    <h1 style="font-size: 42px; font-weight: 700; color: #4ade80; margin: 0;">TeaGuard</h1>
    <p style="color: #9ca3af; font-size: 18px; margin-top: 10px;">
        AI-Powered Field Verification System
    </p>
    <div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px; flex-wrap: wrap;">
        <span style="background: rgba(74,222,128,0.1); border: 1px solid rgba(74,222,128,0.3); 
                     padding: 6px 16px; border-radius: 20px; color: #4ade80; font-size: 14px;">
            📍 GPS Verify
        </span>
        <span style="background: rgba(74,222,128,0.1); border: 1px solid rgba(74,222,128,0.3); 
                     padding: 6px 16px; border-radius: 20px; color: #4ade80; font-size: 14px;">
            👤 Face Detection
        </span>
        <span style="background: rgba(74,222,128,0.1); border: 1px solid rgba(74,222,128,0.3); 
                     padding: 6px 16px; border-radius: 20px; color: #4ade80; font-size: 14px;">
            🛡️ Fake Photo Alert
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

DIVISIONS_FILE = "divisions.json"
HISTORY_FILE = "history.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {} if file == DIVISIONS_FILE else []

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

if "divisions" not in st.session_state:
    st.session_state.divisions = load_json(DIVISIONS_FILE)
if "history" not in st.session_state:
    st.session_state.history = load_json(HISTORY_FILE)

tab1, tab2, tab3 = st.tabs(["📸 Photo Verify", "🗺️ Division Setup", "📊 Dashboard"])

with tab2:
    st.markdown("### 🗺️ Field Location Set Karo")
    st.info("Ek baar set karo — hamesha save rahega!")

    div_name = st.text_input("Division naam (jaise: Block A, Field 1):")
    col1, col2 = st.columns(2)
    with col1:
        clat = st.number_input("Center Latitude:", value=31.50, format="%.6f")
    with col2:
        clon = st.number_input("Center Longitude:", value=74.85, format="%.6f")
    radius = st.slider("Field size (km):", 0.1, 5.0, 0.5, 0.1)

    if st.button("💾 Division Save Karo"):
        if div_name:
            offset = radius / 111
            st.session_state.divisions[div_name] = {
                "lat_min": round(clat - offset, 6),
                "lat_max": round(clat + offset, 6),
                "lon_min": round(clon - offset, 6),
                "lon_max": round(clon + offset, 6),
            }
            save_json(DIVISIONS_FILE, st.session_state.divisions)
            st.success(f"✅ '{div_name}' permanently save ho gaya!")

    if st.session_state.divisions:
        st.markdown("### Saved Divisions:")
        for name, b in st.session_state.divisions.items():
            st.markdown(f"""
            <div style="background: rgba(74,222,128,0.08); border: 1px solid rgba(74,222,128,0.2);
                        border-radius: 10px; padding: 12px 16px; margin: 8px 0;">
                <b style="color: #4ade80;">📍 {name}</b><br>
                <span style="color: #9ca3af; font-size: 13px;">
                    Lat: {b['lat_min']} → {b['lat_max']} | 
                    Lon: {b['lon_min']} → {b['lon_max']}
                </span>
            </div>
            """, unsafe_allow_html=True)

with tab1:
    st.markdown("### 📸 Worker Verification")

    if not st.session_state.divisions:
        st.warning("⚠️ Pehle Division Setup mein apni field ki location set karo!")
    else:
        worker = st.text_input("👤 Worker ka naam:")

        st.markdown("### 📍 Automatic Location")
        gps_html = """
        <div style="padding: 10px 0;">
            <button onclick="getLocation()" style="
                background: linear-gradient(135deg, #16a34a, #15803d);
                color: white; padding: 15px 30px; font-size: 18px;
                border: none; border-radius: 12px; cursor: pointer;
                width: 100%; font-family: Poppins, sans-serif;
                font-weight: 600; letter-spacing: 0.5px;
                box-shadow: 0 4px 15px rgba(22,163,74,0.3);
            ">
                📍 Meri Location Automatic Lo
            </button>
            <div id="status" style="margin-top: 12px; font-size: 15px; 
                color: #9ca3af; text-align: center; font-family: Poppins, sans-serif;">
                Button dabao — location automatic milegi!
            </div>
        </div>
        <script>
        function getLocation() {
            document.getElementById('status').innerHTML = '⏳ Location dhundh raha hoon...';
            document.getElementById('status').style.color = 'orange';
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        var lat = pos.coords.latitude.toFixed(6);
                        var lon = pos.coords.longitude.toFixed(6);
                        document.getElementById('status').innerHTML = 
                            '✅ Location mili! Lat: ' + lat + ' | Lon: ' + lon;
                        document.getElementById('status').style.color = '#4ade80';
                    },
                    function(err) {
                        document.getElementById('status').innerHTML = 
                            '❌ Location nahi mili — phone mein location ON karo!';
                        document.getElementById('status').style.color = 'red';
                    },
                    {enableHighAccuracy: true, timeout: 10000}
                );
            }
        }
        </script>
        """
        html(gps_html, height=120)

        st.markdown("**Ya manually daalo:**")
        col1, col2 = st.columns(2)
        with col1:
            manual_lat = st.number_input("Latitude:", value=0.0, format="%.6f", key="mlat")
        with col2:
            manual_lon = st.number_input("Longitude:", value=0.0, format="%.6f", key="mlon")

        st.markdown("### 📸 Abhi Camera se Photo Lo")
        st.warning("⚠️ Sirf camera se photo accept hogi!")
        camera_photo = st.camera_input("📷 Camera se photo lo")

        if camera_photo and worker and manual_lat != 0.0:
            img = Image.open(camera_photo)

            arr = np.array(img.convert("RGB"))
            gray = cv2.cvtColor(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
            fc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = fc.detectMultiScale(gray, 1.1, 5)
            face_found = len(faces) > 0
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            is_fake = blur_score < 30

            lat = manual_lat
            lon = manual_lon
            division = None
            for name, b in st.session_state.divisions.items():
                if b["lat_min"] <= lat <= b["lat_max"] and b["lon_min"] <= lon <= b["lon_max"]:
                    division = name

            now = datetime.datetime.now()

            st.markdown("---")
            st.markdown("### Verification Results")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div style="background: rgba(74,222,128,0.1); border: 1px solid rgba(74,222,128,0.3);
                            border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 30px;">⏰</div>
                    <div style="color: #4ade80; font-weight: 600; margin: 8px 0;">Time</div>
                    <div style="color: white; font-size: 13px;">{now.strftime('%d %b %Y')}</div>
                    <div style="color: #4ade80; font-weight: 600;">{now.strftime('%I:%M %p')}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                face_color = "#4ade80" if face_found and not is_fake else "#ef4444"
                face_icon = "✅" if face_found and not is_fake else "❌"
                face_text = "Face Mila!" if face_found and not is_fake else ("Fake Photo!" if is_fake else "Face Nahi Mila!")
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border: 1px solid {face_color}40;
                            border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 30px;">{face_icon}</div>
                    <div style="color: {face_color}; font-weight: 600; margin: 8px 0;">Face Check</div>
                    <div style="color: white; font-size: 13px;">{face_text}</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                loc_color = "#4ade80" if division else "#ef4444"
                loc_icon = "✅" if division else "❌"
                loc_text = division if division else "Division Se Bahar!"
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border: 1px solid {loc_color}40;
                            border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 30px;">{loc_icon}</div>
                    <div style="color: {loc_color}; font-weight: 600; margin: 8px 0;">Location</div>
                    <div style="color: white; font-size: 13px;">{loc_text}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if face_found and division and not is_fake:
                status = "Verified"
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(22,163,74,0.2), rgba(21,128,61,0.1));
                            border: 2px solid #4ade80; border-radius: 15px; padding: 25px; text-align: center;">
                    <div style="font-size: 50px;">✅</div>
                    <div style="color: #4ade80; font-size: 24px; font-weight: 700;">VERIFIED!</div>
                    <div style="color: #9ca3af; margin-top: 8px;">Worker sahi jagah tha — photo authentic hai</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                status = "Failed-Fake" if is_fake else "Failed"
                reason = "Fake photo detect hui!" if is_fake else "Verification fail hua!"
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(185,28,28,0.1));
                            border: 2px solid #ef4444; border-radius: 15px; padding: 25px; text-align: center;">
                    <div style="font-size: 50px;">❌</div>
                    <div style="color: #ef4444; font-size: 24px; font-weight: 700;">FAILED!</div>
                    <div style="color: #9ca3af; margin-top: 8px;">{reason}</div>
                </div>
                """, unsafe_allow_html=True)

            if lat and lon:
                st.markdown("<br>", unsafe_allow_html=True)
                m = folium.Map(location=[lat, lon], zoom_start=14)
                folium.Marker(
                    [lat, lon],
                    icon=folium.Icon(color="green" if status == "Verified" else "red")
                ).add_to(m)
                for n, b in st.session_state.divisions.items():
                    folium.Rectangle(
                        [[b["lat_min"], b["lon_min"]], [b["lat_max"], b["lon_max"]]],
                        color="#4ade80", fill=True, fill_opacity=0.15
                    ).add_to(m)
                st_folium(m, width=700, height=350)

            record = {
                "Worker": worker,
                "Time": now.strftime('%d %b %Y, %I:%M %p'),
                "Lat": lat, "Lon": lon,
                "Division": division or "Outside",
                "Face": "Found" if face_found else "Not Found",
                "Fake": "Yes" if is_fake else "No",
                "Status": status
            }
            st.session_state.history.append(record)
            save_json(HISTORY_FILE, st.session_state.history)
            st.success("✅ Record save ho gaya!")

with tab3:
    st.markdown("### 📊 Manager Dashboard")
    if not st.session_state.history:
        st.info("Koi record nahi abhi — pehle photo verify karo")
    else:
        df = pd.DataFrame(st.session_state.history)
        c1, c2, c3 = st.columns(3)
        c1.metric("📊 Total", len(df))
        c2.metric("✅ Verified", len(df[df["Status"] == "Verified"]))
        c3.metric("❌ Failed", len(df[df["Status"] != "Verified"]))
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "📥 CSV Download Karo",
            df.to_csv(index=False),
            "teaguard_report.csv",
            "text/csv"
        )
        if st.button("🗑️ History Clear"):
            st.session_state.history = []
            save_json(HISTORY_FILE, [])
            st.rerun()
