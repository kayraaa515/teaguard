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
        photo = st.file_uploader("Photo upload karo", type=["jpg","jpeg","png"])
        
        if photo and worker:
            img = Image.open(photo)
            st.image(img, width=300)
            
            # EXIF
            exif = {}
            try:
                info = img._getexif()
                if info:
                    for tag, val in info.items():
                        exif[TAGS.get(tag, tag)] = val
            except:
                pass
            
            # GPS
            lat, lon = None, None
            if "GPSInfo" in exif:
                try:
                    g = {GPSTAGS.get(k,k): v for k,v in exif["GPSInfo"].items()}
                    la = g["GPSLatitude"]
                    lo = g["GPSLongitude"]
                    lat = float(la[0]) + float(la[1])/60 + float(la[2])/3600
                    lon = float(lo[0]) + float(lo[1])/60 + float(lo[2])/3600
                    lat = round(lat, 6)
                    lon = round(lon, 6)
                except:
                    pass
            
            # Time
            ptime = None
            ts = exif.get("DateTimeOriginal")
            if ts:
                try:
                    ptime = datetime.datetime.strptime(ts, "%Y:%m:%d %H:%M:%S")
                except:
                    pass
            
            # Face
            arr = np.array(img.convert("RGB"))
            gray = cv2.cvtColor(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
            fc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = fc.detectMultiScale(gray, 1.1, 5)
            face_found = len(faces) > 0
            
            # Division check
            division = None
            if lat and lon:
                for name, b in st.session_state.divisions.items():
                    if b["lat_min"] <= lat <= b["lat_max"] and b["lon_min"] <= lon <= b["lon_max"]:
                        division = name
            
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Time**")
                if ptime:
                    st.success(ptime.strftime('%d %b %Y, %I:%M %p'))
                else:
                    st.warning("Nahi mila")
            with c2:
                st.markdown("**Face**")
                if face_found:
                    st.success("Face mila!")
                else:
                    st.error("Face nahi mila!")
            with c3:
                st.markdown("**Location**")
                if lat and division:
                    st.success(f"{division}")
                elif lat:
                    st.error("Division se bahar!")
                else:
                    st.error("GPS nahi mila")
            
            st.markdown("---")
            status = "Verified" if (face_found and division) else "Failed"
            if status == "Verified":
                st.success("VERIFIED!")
            else:
                st.error("FAILED!")
            
            if lat and lon:
                m = folium.Map(location=[lat, lon], zoom_start=14)
                folium.Marker([lat, lon], icon=folium.Icon(color="green" if status=="Verified" else "red")).add_to(m)
                for n, b in st.session_state.divisions.items():
                    folium.Rectangle([[b["lat_min"],b["lon_min"]],[b["lat_max"],b["lon_max"]]], color="blue", fill=True, fill_opacity=0.15).add_to(m)
                st_folium(m, width=700, height=400)
            
            record = {
                "Worker": worker,
                "Time": ptime.strftime('%d %b %Y, %I:%M %p') if ptime else "N/A",
                "Lat": lat or "N/A",
                "Lon": lon or "N/A",
                "Division": division or "Outside",
                "Face": "Found" if face_found else "Not Found",
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
        c2.metric("Verified", len(df[df["Status"]=="Verified"]))
        c3.metric("Failed", len(df[df["Status"]=="Failed"]))
        st.dataframe(df, use_container_width=True)
        st.download_button("CSV Download", df.to_csv(index=False), "report.csv", "text/csv")
