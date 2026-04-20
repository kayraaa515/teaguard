import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import folium
from streamlit_folium import st_folium
import datetime
import pandas as pd
import cv2
import numpy as np

st.set_page_config(page_title="TeaGuard", page_icon="🌿", layout="wide")
st.title("🌿 TeaGuard - Field Verification System")

# ---- Session state ----
if "divisions" not in st.session_state:
    st.session_state.divisions = {}
if "history" not in st.session_state:
    st.session_state.history = []

# ---- Helper functions ----
def get_exif_data(image):
    exif_data = {}
    try:
        info = image._getexif()
        if info:
            for tag, value in info.items():
                tag_name = TAGS.get(tag, tag)
                exif_data[tag_name] = value
    except:
        pass
    return exif_data

def get_gps(exif_data):
    if "GPSInfo" not in exif_data:
        return None, None
    gps_info = {}
    for key, val in exif_data["GPSInfo"].items():
        gps_info[GPSTAGS.get(key, key)] = val
    try:
        lat = gps_info["GPSLatitude"]
        lon = gps_info["GPSLongitude"]
        lat = lat[0] + lat[1]/60 + lat[2]/3600
        lon = lon[0] + lon[1]/60 + lon[2]/3600
        if gps_info.get("GPSLatitudeRef") == "S":
            lat = -lat
        if gps_info.get("GPSLongitudeRef") == "W":
            lon = -lon
        return round(lat, 6), round(lon, 6)
    except:
        return None, None

def get_exif_time(exif_data):
    time_str = exif_data.get("DateTimeOriginal", None)
    if time_str:
        try:
            return datetime.datetime.strptime(time_str, "%Y:%m:%d %H:%M:%S")
        except:
            return None
    return None

def detect_face(image):
    img_array = np.array(image.convert("RGB"))
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return len(faces) > 0, len(faces)

def check_division(lat, lon):
    for division, bounds in st.session_state.divisions.items():
        if (bounds["lat_min"] <= lat <= bounds["lat_max"] and
                bounds["lon_min"] <= lon <= bounds["lon_max"]):
            return division
    return None

# ---- Tabs ----
tab1, tab2, tab3 = st.tabs(["📸 Photo Verify", "🗺️ Division Setup", "📊 Manager Dashboard"])

# ================================================
# TAB 1 - Photo Verification
# ================================================
with tab1:
    st.subheader("Worker Photo Verification")

    if len(st.session_state.divisions) == 0:
        st.warning("Pehle Division Setup tab mein apni field ki location set karo!")
    else:
        worker_name = st.text_input("Worker ka naam:")
        uploaded_file = st.file_uploader("Photo upload karo", type=["jpg", "jpeg", "png"])

        if uploaded_file and worker_name:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Photo", width=300)

            exif_data = get_exif_data(image)
            lat, lon = get_gps(exif_data)
            photo_time = get_exif_time(exif_data)

            st.markdown("---")
            st.subheader("Verification Results")

            col1, col2, col3 = st.columns(3)

            # Time check
            with col1:
                st.markdown("**Time Check**")
                if photo_time:
                    st.success(f"{photo_time.strftime('%d %b %Y, %I:%M %p')}")
                    time_status = "OK"
                else:
                    st.warning("Time nahi mila")
                    time_status = "Missing"

            # Face check
            with col2:
                st.markdown("**Face Check**")
                face_found, face_count = detect_face(image)
                if face_found:
                    st.success(f"Face mila ({face_count} detected)")
                    face_status = "Found"
                else:
                    st.error("Face nahi mila!")
                    face_status = "Not Found"

            # GPS check
            with col3:
                st.markdown("**Location Check**")
                if lat and lon:
                    division = check_division(lat, lon)
                    if division:
                        st.success(f"Division: {division}")
                        location_status = "Verified"
                    else:
                        st.error("Division se bahar!")
                        location_status = "Outside"
                else:
                    st.error("GPS nahi mila")
                    location_status = "No GPS"
                    division = None

            # Overall status
            st.markdown("---")
            if face_found and lat and lon and division:
                st.success("VERIFIED — Worker sahi jagah tha aur photo authentic hai!")
                final_status = "Verified"
            else:
                st.error("FAILED — Verification fail hua!")
                final_status = "Failed"

            # Map
            if lat and lon:
                m = folium.Map(location=[lat, lon], zoom_start=14)
                folium.Marker(
                    [lat, lon],
                    popup=f"{worker_name} - {final_status}",
                    icon=folium.Icon(color="green" if final_status == "Verified" else "red")
                ).add_to(m)
                for div_name, bounds in st.session_state.divisions.items():
                    folium.Rectangle(
                        bounds=[[bounds["lat_min"], bounds["lon_min"]],
                                 [bounds["lat_max"], bounds["lon_max"]]],
                        color="blue",
                        fill=True,
                        fill_opacity=0.15,
                        popup=div_name
                    ).add_to(m)
                st.subheader("Map:")
                st_folium(m, width=700, height=400)

            # Save to history
            st.session_state.history.append({
                "Worker": worker_name,
                "Time": photo_time.strftime('%d %b %Y, %I:%M %p') if photo_time else "N/A",
                "Latitude": lat if lat else "N/A",
                "Longitude": lon if lon else "N/A",
                "Division": division if division else "Outside",
                "Face": face_status,
                "Status": final_status
            })
            st.info("Record dashboard mein save ho gaya!")

# ================================================
# TAB 2 - Division Setup
# ================================================
with tab2:
    st.subheader("Apni Field ki Location Set Karo")
    st.info("Google Maps pe jaao, apni tea garden ke center pe right-click karo, coordinates copy karo aur yahan paste karo.")

    with st.form("division_form"):
        div_name = st.text_input("Division ka naam (jaise: Block A, Field 1):")
        col1, col2 = st.columns(2)
        with col1:
            center_lat = st.number_input("Center Latitude (Google Maps se):", value=31.50, format="%.6f")
        with col2:
            center_lon = st.number_input("Center Longitude (Google Maps se):", value=74.85, format="%.6f")

        radius = st.slider("Field ka size (km mein):", min_value=0.1, max_value=5.0, value=0.5, step=0.1)
        submitted = st.form_submit_button("Division Save Karo")

        if submitted and div_name:
            offset = radius / 111
            st.session_state.divisions[div_name] = {
                "lat_min": round(center_lat - offset, 6),
                "lat_max": round(center_lat + offset, 6),
                "lon_min": round(center_lon - offset, 6),
                "lon_max": round(center_lon + offset, 6),
            }
            st.success(f"'{div_name}' save ho gaya!")

    # Show saved divisions
    if st.session_state.divisions:
        st.markdown("---")
        st.subheader("Saved Divisions:")
        for name, bounds in st.session_state.divisions.items():
            st.write(f"**{name}** — Lat: {bounds['lat_min']} to {bounds['lat_max']}, Lon: {bounds['lon_min']} to {bounds['lon_max']}")

        if st.button("Sab Divisions Map pe Dekho"):
            first = list(st.session_state.divisions.values())[0]
            m2 = folium.Map(location=[(first["lat_min"]+first["lat_max"])/2,
                                       (first["lon_min"]+first["lon_max"])/2], zoom_start=13)
            for div_name, bounds in st.session_state.divisions.items():
                folium.Rectangle(
                    bounds=[[bounds["lat_min"], bounds["lon_min"]],
                             [bounds["lat_max"], bounds["lon_max"]]],
                    color="blue", fill=True, fill_opacity=0.2,
                    popup=div_name
                ).add_to(m2)
            st_folium(m2, width=700, height=400)

        if st.button("Saari Divisions Delete Karo"):
            st.session_state.divisions = {}
            st.success("Sab delete ho gaya!")

# ================================================
# TAB 3 - Manager Dashboard
# ================================================
with tab3:
    st.subheader("Manager Dashboard")

    if len(st.session_state.history) == 0:
        st.info("Abhi koi record nahi — pehle Photo Verify tab mein photo upload karo")
    else:
        df = pd.DataFrame(st.session_state.history)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", len(df))
        with col2:
            st.metric("Verified", len(df[df["Status"] == "Verified"]))
        with col3:
            st.metric("Failed", len(df[df["Status"] == "Failed"]))
        with col4:
            st.metric("Face Missing", len(df[df["Face"] == "Not Found"]))

        st.markdown("---")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False)
        st.download_button(
            label="CSV Download karo",
            data=csv,
            file_name="teaguard_report.csv",
            mime="text/csv"
        )