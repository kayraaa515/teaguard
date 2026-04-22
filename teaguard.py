import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import folium
from streamlit_folium import st_folium
import datetime
import pandas as pd
import cv2
import numpy as np
import json
import os

st.set_page_config(page_title="TeaGuard", page_icon="🌿", layout="wide")
st.title("🌿 TeaGuard - Field Verification System")

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
    st.subheader("Field Location Set Karo")
    st.info("Ek baar set karo — hamesha save rahega!")
    div_name = st.text_input("Division naam:")
    col1, col2 = st.columns(2)
    with col1:
        clat = st.number_input("Latitude:", value=31.50, format="%.6f")
    with col2:
        clon = st.number_input("Longitude:", value=74.85, format="%.6f")
    radius = st.slider("Size (km):", 0.1, 5.0, 0.5, 0.1)
    if st.button("Save Division"):
        if div_name:
            offset = radius / 111
            st.session_state.divisions[div_name] = {
                "lat_min": round(clat - offset, 6),
                "lat_max": round(clat + offset, 6),
                "lon_min": round(clon - offset, 6),
                "lon_max": round(clon + offset, 6),
            }
            save_json(DIVISIONS_FILE, st.session_state.divisions)
            st.success(f"{div_name} save ho gaya!")
    if st.session_state.divisions:
        st.subheader("Saved Divisions:")
        for name, b in st.session_state.divisions.items():
            st.write(f"**{name}** — {b['lat_min']} to {b['lat_max']}")

with tab1:
    st.subheader("Worker Photo Verify")
    if not st.session_state.divisions:
        st.warning("Pehle Division Setup mein location set karo!")
    else:
        worker = st.text_input("Worker naam:")
        
        st.markdown("### 📍 Apni location paste karo")
        st.info("Phone mein Google Maps kholo → apni location pe tap karo → coordinates copy karo → yahan paste karo")
        col1, col2 = st.columns(2)
        with col1:
            manual_lat = st.number_input("Latitude:", value=0.0, format="%.6f")
        with col2:
            manual_lon = st.number_input("Longitude:", value=0.0, format="%.6f")

        st.markdown("### 📸 Abhi Camera se Photo Lo")
        st.warning("Sirf camera se li photo accept hogi — gallery se nahi!")
        camera_photo = st.camera_input("Camera se photo lo")

        if camera_photo and worker and manual_lat != 0.0:
            img = Image.open(camera_photo)
            st.image(img, width=300)

            # Face detection
            arr = np.array(img.convert("RGB"))
            gray = cv2.cvtColor(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
            fc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = fc.detectMultiScale(gray, 1.1, 5)
            face_found = len(faces) > 0

            # Fake photo detection — blur check
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            is_fake = blur_score < 30

            # Division check
            lat = manual_lat
            lon = manual_lon
            division = None
            for name, b in st.session_state.divisions.items():
                if b["lat_min"] <= lat <= b["lat_max"] and b["lon_min"] <= lon <= b["lon_max"]:
                    division = name

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Time**")
                now = datetime.datetime.now()
                st.success(now.strftime('%d %b %Y, %I:%M %p'))
            with c2:
                st.markdown("**Face Check**")
                if is_fake:
                    st.error("Fake photo — screen se li lag rahi hai!")
                elif face_found:
                    st.success("Face mila!")
                else:
                    st.error("Face nahi mila!")
            with c3:
                st.markdown("**Location**")
                if division:
                    st.success(f"{division}")
                else:
                    st.error("Division se bahar!")

            st.markdown("---")
            if face_found and division and not is_fake:
                st.success("✅ VERIFIED — Worker sahi jagah tha!")
                status = "Verified"
            elif is_fake:
                st.error("❌ FAILED — Fake photo detect hui!")
                status = "Failed - Fake"
            else:
                st.error("❌ FAILED!")
                status = "Failed"

            # Map
            m = folium.Map(location=[lat, lon], zoom_start=14)
            folium.Marker(
