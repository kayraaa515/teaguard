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
if "lat" not in st.session_state:
    st.session_state.lat = None
if "lon" not in st.session_state:
    st.session_state.lon = None

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

        # Auto GPS via browser
        st.markdown("### 📍 Automatic Location")
        
        loc_data = st.query_params.get("lat", None)
        
        # HTML to get GPS automatically
        gps_html = """
        <div style="text-align:center; padding: 10px;">
            <button onclick="getLocation()" style="
                background-color: #4CAF50;
                color: white;
                padding: 15px 30px;
                font-size: 18px;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                width: 100%;
            ">
                📍 Meri Location Lo
            </button>
            <p id="status" style="margin-top:10px; font-size:16px; color:gray;">Button dabao — location automatic milegi!</p>
            <input type="text" id="lat_val" style="display:none">
            <input type="text" id="lon_val" style="display:none">
        </div>

        <script>
        function getLocation() {
            document.getElementById('status').innerHTML = '⏳ Location dhundh raha hoon...';
            document.getElementById('status').style.color = 'orange';
            
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        var lat = position.coords.latitude.toFixed(6);
                        var lon = position.coords.longitude.toFixed(6);
                        document.getElementById('status').innerHTML = 
                            '✅ Location mili! Lat: ' + lat + ', Lon: ' + lon;
                        document.getElementById('status').style.color = 'green';
                        document.getElementById('lat_val').value = lat;
                        document.getElementById('lon_val').value = lon;
                        
                        // Send to Streamlit
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: lat + ',' + lon
                        }, '*');
                    },
                    function(error) {
                        document.getElementById('status').innerHTML = 
                            '❌ Location nahi mili — phone mein location ON karo!';
                        document.getElementById('status').style.color = 'red';
                    },
                    {enableHighAccuracy: true, timeout: 10000}
                );
            } else {
                document.getElementById('status').innerHTML = '❌ Browser GPS support nahi karta!';
            }
        }
        </script>
        """
        
        from streamlit.components.v1 import html
        html(gps_html, height=150)

        # Manual fallback
        st.markdown("**Ya manually daalo (Google Maps se):**")
        col1, col2 = st.columns(2)
        with col1:
            manual_lat = st.number_input("Latitude:", value=0.0, format="%.6f", key="mlat")
        with col2:
            manual_lon = st.number_input("Longitude:", value=0.0, format="%.6f", key="mlon")

        st.markdown("### 📸 Camera se Photo Lo")
        st.warning("Sirf camera se photo lo — gallery se nahi chalega!")
        camera_photo = st.camera_input("Photo lo")

        if camera_photo and worker and manual_lat != 0.0:
            img = Image.open(camera_photo)
            st.image(img, width=300)

            lat = manual_lat
            lon = manual_lon

            # Face detection
            arr = np.array(img.convert("RGB"))
            gray = cv2.cvtColor(
                cv2.cvtColor(arr, cv2.COLOR_RGB2BGR),
                cv2.COLOR_BGR2GRAY
            )
            fc = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            faces = fc.detectMultiScale(gray, 1.1, 5)
            face_found = len(faces) > 0

            # Fake detection
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            is_fake = blur_score < 30

            # Division check
            division = None
            for name, b in st.session_state.divisions.items():
                if (b["lat_min"] <= lat <= b["lat_max"] and
                        b["lon_min"] <= lon <= b["lon_max"]):
                    division = name

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Time**")
                now = datetime.datetime.now()
                st.success(now.strftime('%d %b %Y, %I:%M %p'))
            with c2:
                st.markdown("**Face**")
                if is_fake:
                    st.error("Fake photo!")
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
                st.success("✅ VERIFIED!")
                status = "Verified"
            elif is_fake:
                st.error("❌ FAILED — Fake photo!")
                status = "Failed-Fake"
            else:
                st.error("❌ FAILED!")
                status = "Failed"

            if lat and lon:
                m = folium.Map(location=[lat, lon], zoom_start=14)
                folium.Marker(
                    [lat, lon],
                    icon=folium.Icon(
                        color="green" if status == "Verified" else "red"
                    )
                ).add_to(m)
                for n, b in st.session_state.divisions.items():
                    folium.Rectangle(
                        [[b["lat_min"], b["lon_min"]],
                         [b["lat_max"], b["lon_max"]]],
                        color="blue", fill=True, fill_opacity=0.15
                    ).add_to(m)
                st_folium(m, width=700, height=350)

            record = {
                "Worker": worker,
                "Time": now.strftime('%d %b %Y, %I:%M %p'),
                "Lat": lat,
                "Lon": lon,
                "Division": division or "Outside",
                "Face": "Found" if face_found else "Not Found",
                "Fake": "Yes" if is_fake else "No",
                "Status": status
            }
            st.session_state.history.append(record)
            save_json(HISTORY_FILE, st.session_state.history)
            st.info("Record save ho gaya!")

with tab3:
    st.subheader("Manager Dashboard")
    if not st.session_state.history:
        st.info("Koi record nahi abhi")
    else:
        df = pd.DataFrame(st.session_state.history)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", len(df))
        c2.metric("Verified", len(df[df["Status"] == "Verified"]))
        c3.metric("Failed", len(df[df["Status"] != "Verified"]))
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "CSV Download",
            df.to_csv(index=False),
            "report.csv",
            "text/csv"
        )
        if st.button("History Clear"):
            st.session_state.history = []
            save_json(HISTORY_FILE, [])
            st.rerun()
