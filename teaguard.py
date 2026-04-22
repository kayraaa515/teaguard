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

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    .stApp {
        background: linear-gradient(135deg, #0d1b0f 0%, #1a2e1c 50%, #0d1b0f 100%);
        color: white;
    }
    h1, h2, h3 { color: #4ade80 !important; }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.05);
        border-radius: 15px; padding: 5px; gap: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent; color: #9ca3af;
        border-radius: 10px; font-weight: 600; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #16a34a, #15803d) !important;
        color: white !important;
    }
    .stTextInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(74,222,128,0.3) !important;
        border-radius: 10px !important; color: white !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #16a34a, #15803d) !important;
        color: white !important; border: none !important;
        border-radius: 12px !important; font-weight: 600 !important;
        width: 100% !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:30px 20px;
    background: linear-gradient(135deg, rgba(22,163,74,0.15), rgba(21,128,61,0.1));
    border-radius: 20px; border: 1px solid rgba(74,222,128,0.2); margin-bottom: 30px;">
    <div style="font-size:50px;">🌿</div>
    <h1 style="font-size:38px; font-weight:700; color:#4ade80; margin:0;">TeaGuard</h1>
    <p style="color:#9ca3af; font-size:16px; margin-top:8px;">
        AI-Powered Tea Garden Management System
    </p>
</div>
""", unsafe_allow_html=True)

# ---- Files ----
GARDENS_FILE = "gardens.json"
WORKERS_FILE = "workers.json"
ATTENDANCE_FILE = "attendance.json"

def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

if "gardens" not in st.session_state:
    st.session_state.gardens = load_json(GARDENS_FILE, {})
if "workers" not in st.session_state:
    st.session_state.workers = load_json(WORKERS_FILE, {})
if "attendance" not in st.session_state:
    st.session_state.attendance = load_json(ATTENDANCE_FILE, [])

tab1, tab2, tab3, tab4 = st.tabs([
    "📸 Attendance", "🏡 Garden Setup", "👷 Workers", "📊 Dashboard"
])

# ================================================
# TAB 2 - Garden Setup
# ================================================
with tab2:
    st.markdown("### 🏡 Garden & Field Setup")
    st.info("Ek baar set karo — hamesha save rahega!")

    garden_name = st.text_input("Garden ka naam:", key="gname")

    st.markdown("#### Field/Division add karo:")
    col1, col2 = st.columns(2)
    with col1:
        field_name = st.text_input("Field naam (jaise: Block A):", key="fname")
        clat = st.number_input("Center Latitude:", value=31.50, format="%.6f")
    with col2:
        field_number = st.text_input("Field number:", key="fnum")
        clon = st.number_input("Center Longitude:", value=74.85, format="%.6f")
    radius = st.slider("Field size (km):", 0.1, 5.0, 0.5, 0.1)

    if st.button("💾 Garden & Field Save Karo"):
        if garden_name and field_name:
            if garden_name not in st.session_state.gardens:
                st.session_state.gardens[garden_name] = {}
            offset = radius / 111
            field_key = f"{field_name} ({field_number})" if field_number else field_name
            st.session_state.gardens[garden_name][field_key] = {
                "lat_min": round(clat - offset, 6),
                "lat_max": round(clat + offset, 6),
                "lon_min": round(clon - offset, 6),
                "lon_max": round(clon + offset, 6),
            }
            save_json(GARDENS_FILE, st.session_state.gardens)
            st.success(f"✅ {garden_name} — {field_key} save ho gaya!")

    if st.session_state.gardens:
        st.markdown("### Saved Gardens & Fields:")
        for gname, fields in st.session_state.gardens.items():
            st.markdown(f"""
            <div style="background:rgba(74,222,128,0.08); border:1px solid rgba(74,222,128,0.2);
                border-radius:12px; padding:16px; margin:8px 0;">
                <b style="color:#4ade80; font-size:16px;">🏡 {gname}</b>
            </div>
            """, unsafe_allow_html=True)
            for fname, bounds in fields.items():
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.03); border-left:3px solid #4ade80;
                    border-radius:8px; padding:10px 16px; margin:4px 0 4px 20px;">
                    <span style="color:white;">📍 {fname}</span><br>
                    <span style="color:#9ca3af; font-size:12px;">
                        Lat: {bounds['lat_min']} → {bounds['lat_max']} | 
                        Lon: {bounds['lon_min']} → {bounds['lon_max']}
                    </span>
                </div>
                """, unsafe_allow_html=True)

# ================================================
# TAB 3 - Workers Register
# ================================================
with tab3:
    st.markdown("### 👷 Workers Register Karo")
    st.info("Pehle saare workers ka data daalo — ek baar kaam!")

    col1, col2 = st.columns(2)
    with col1:
        w_id = st.text_input("Worker ID (jaise: W001):")
        w_name = st.text_input("Worker ka naam:")
    with col2:
        w_garden = st.selectbox(
            "Garden:",
            options=list(st.session_state.gardens.keys()) if st.session_state.gardens else ["Pehle garden set karo"]
        )
        if st.session_state.gardens and w_garden in st.session_state.gardens:
            w_field = st.selectbox(
                "Field/Division:",
                options=list(st.session_state.gardens[w_garden].keys())
            )
        else:
            w_field = ""

    if st.button("✅ Worker Register Karo"):
        if w_id and w_name and w_garden:
            st.session_state.workers[w_id] = {
                "naam": w_name,
                "garden": w_garden,
                "field": w_field,
            }
            save_json(WORKERS_FILE, st.session_state.workers)
            st.success(f"✅ {w_name} (ID: {w_id}) register ho gaya!")

    if st.session_state.workers:
        st.markdown("### Registered Workers:")
        df_w = pd.DataFrame([
            {"ID": wid, "Naam": d["naam"], "Garden": d["garden"], "Field": d["field"]}
            for wid, d in st.session_state.workers.items()
        ])
        st.dataframe(df_w, use_container_width=True)

        if st.button("🗑️ Kisi Worker Ko Hatao"):
            del_id = st.text_input("Worker ID likho jo hatana hai:")
            if del_id and del_id in st.session_state.workers:
                del st.session_state.workers[del_id]
                save_json(WORKERS_FILE, st.session_state.workers)
                st.success("Worker hata diya!")

# ================================================
# TAB 1 - Daily Attendance
# ================================================
with tab1:
    st.markdown("### 📸 Daily Attendance")

    if not st.session_state.gardens:
        st.warning("⚠️ Pehle Garden Setup mein garden aur fields set karo!")
    elif not st.session_state.workers:
        st.warning("⚠️ Pehle Workers tab mein workers register karo!")
    else:
        worker_id = st.text_input("🪪 Apni Worker ID daalo:")

        worker_info = None
        if worker_id and worker_id in st.session_state.workers:
            worker_info = st.session_state.workers[worker_id]
            st.markdown(f"""
            <div style="background:rgba(74,222,128,0.1); border:1px solid rgba(74,222,128,0.3);
                border-radius:12px; padding:16px; margin:10px 0;">
                <b style="color:#4ade80;">✅ Worker Mila!</b><br>
                <span style="color:white;">👤 {worker_info['naam']}</span><br>
                <span style="color:#9ca3af;">🏡 {worker_info['garden']} — 📍 {worker_info['field']}</span>
            </div>
            """, unsafe_allow_html=True)
        elif worker_id:
            st.error("❌ Worker ID nahi mila — sahi ID daalo!")

        st.markdown("### 📍 Location")
        col1, col2 = st.columns(2)
        with col1:
            lat_input = st.number_input("Latitude (Google Maps se):", value=0.0, format="%.6f", key="alat")
        with col2:
            lon_input = st.number_input("Longitude (Google Maps se):", value=0.0, format="%.6f", key="alon")

        st.markdown("### 📸 Live Photo Lo")
        st.warning("⚠️ Sirf camera se photo lo — gallery nahi chalegi!")
        camera_photo = st.camera_input("📷 Abhi photo lo")

        if camera_photo and worker_info and lat_input != 0.0:
            img = Image.open(camera_photo)

            # Face detection
            arr = np.array(img.convert("RGB"))
            gray = cv2.cvtColor(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
            fc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = fc.detectMultiScale(gray, 1.1, 5)
            face_found = len(faces) > 0

            # Fake detection
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            is_fake = blur_score < 30

            # Location check
            lat = lat_input
            lon = lon_input
            garden = worker_info["garden"]
            expected_field = worker_info["field"]
            field_bounds = st.session_state.gardens[garden].get(expected_field, {})

            location_ok = False
            if field_bounds:
                location_ok = (
                    field_bounds["lat_min"] <= lat <= field_bounds["lat_max"] and
                    field_bounds["lon_min"] <= lon <= field_bounds["lon_max"]
                )

            now = datetime.datetime.now()

            # Results
            st.markdown("---")
            st.markdown("### Verification Results")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div style="background:rgba(74,222,128,0.1); border:1px solid rgba(74,222,128,0.3);
                    border-radius:12px; padding:20px; text-align:center;">
                    <div style="font-size:28px;">⏰</div>
                    <div style="color:#4ade80; font-weight:600;">Time</div>
                    <div style="color:white; font-size:13px;">{now.strftime('%d %b %Y')}</div>
                    <div style="color:#4ade80; font-weight:600;">{now.strftime('%I:%M %p')}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                fc_color = "#4ade80" if face_found and not is_fake else "#ef4444"
                fc_icon = "✅" if face_found and not is_fake else "❌"
                fc_text = "Face Mila!" if face_found and not is_fake else ("Fake Photo!" if is_fake else "Face Nahi Mila!")
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); border:1px solid {fc_color}40;
                    border-radius:12px; padding:20px; text-align:center;">
                    <div style="font-size:28px;">{fc_icon}</div>
                    <div style="color:{fc_color}; font-weight:600;">Face Check</div>
                    <div style="color:white; font-size:13px;">{fc_text}</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                lc_color = "#4ade80" if location_ok else "#ef4444"
                lc_icon = "✅" if location_ok else "❌"
                lc_text = expected_field if location_ok else "Galat Location!"
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); border:1px solid {lc_color}40;
                    border-radius:12px; padding:20px; text-align:center;">
                    <div style="font-size:28px;">{lc_icon}</div>
                    <div style="color:{lc_color}; font-weight:600;">Location</div>
                    <div style="color:white; font-size:13px;">{lc_text}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if face_found and location_ok and not is_fake:
                status = "Present"
                st.markdown("""
                <div style="background:linear-gradient(135deg, rgba(22,163,74,0.2), rgba(21,128,61,0.1));
                    border:2px solid #4ade80; border-radius:15px; padding:25px; text-align:center;">
                    <div style="font-size:50px;">✅</div>
                    <div style="color:#4ade80; font-size:24px; font-weight:700;">PRESENT!</div>
                    <div style="color:#9ca3af; margin-top:8px;">Attendance record ho gayi!</div>
                </div>
                """, unsafe_allow_html=True)
            elif is_fake:
                status = "Fake Photo"
                st.markdown("""
                <div style="background:linear-gradient(135deg, rgba(239,68,68,0.2), rgba(185,28,28,0.1));
                    border:2px solid #ef4444; border-radius:15px; padding:25px; text-align:center;">
                    <div style="font-size:50px;">🚨</div>
                    <div style="color:#ef4444; font-size:24px; font-weight:700;">FAKE PHOTO!</div>
                    <div style="color:#9ca3af; margin-top:8px;">Camera se live photo lo!</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                status = "Absent/Failed"
                st.markdown("""
                <div style="background:linear-gradient(135deg, rgba(239,68,68,0.2), rgba(185,28,28,0.1));
                    border:2px solid #ef4444; border-radius:15px; padding:25px; text-align:center;">
                    <div style="font-size:50px;">❌</div>
                    <div style="color:#ef4444; font-size:24px; font-weight:700;">FAILED!</div>
                    <div style="color:#9ca3af; margin-top:8px;">Location ya face verify nahi hua!</div>
                </div>
                """, unsafe_allow_html=True)

            # Map
            if lat and lon:
                m = folium.Map(location=[lat, lon], zoom_start=15)
                folium.Marker(
                    [lat, lon],
                    popup=f"{worker_info['naam']} — {status}",
                    icon=folium.Icon(color="green" if status == "Present" else "red")
                ).add_to(m)
                if field_bounds:
                    folium.Rectangle(
                        [[field_bounds["lat_min"], field_bounds["lon_min"]],
                         [field_bounds["lat_max"], field_bounds["lon_max"]]],
                        color="#4ade80", fill=True, fill_opacity=0.2
                    ).add_to(m)
                st_folium(m, width=700, height=350)

            # Save attendance
            record = {
                "Date": now.strftime('%d %b %Y'),
                "Time": now.strftime('%I:%M %p'),
                "Worker ID": worker_id,
                "Naam": worker_info["naam"],
                "Garden": worker_info["garden"],
                "Field": worker_info["field"],
                "Lat": lat,
                "Lon": lon,
                "Face": "✅" if face_found else "❌",
                "Location": "✅" if location_ok else "❌",
                "Status": status
            }
            st.session_state.attendance.append(record)
            save_json(ATTENDANCE_FILE, st.session_state.attendance)
            st.success("✅ Attendance save ho gayi!")

# ================================================
# TAB 4 - Manager Dashboard
# ================================================
with tab4:
    st.markdown("### 📊 Manager Dashboard")

    if not st.session_state.attendance:
        st.info("Koi attendance record nahi abhi")
    else:
        df = pd.DataFrame(st.session_state.attendance)

        # Today filter
        today = datetime.datetime.now().strftime('%d %b %Y')
        df_today = df[df["Date"] == today]

        st.markdown(f"#### Aaj ki Attendance — {today}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📊 Total", len(df_today))
        c2.metric("✅ Present", len(df_today[df_today["Status"] == "Present"]))
        c3.metric("❌ Absent/Failed", len(df_today[df_today["Status"] == "Absent/Failed"]))
        c4.metric("🚨 Fake", len(df_today[df_today["Status"] == "Fake Photo"]))

        st.markdown("---")
        st.markdown("#### Aaj ki detail:")
        if len(df_today) > 0:
            st.dataframe(df_today, use_container_width=True)
        else:
            st.info("Aaj koi attendance nahi")

        st.markdown("---")
        st.markdown("#### Poori history:")
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Aaj ki Report Download",
                df_today.to_csv(index=False) if len(df_today) > 0 else df.to_csv(index=False),
                f"attendance_{today}.csv",
                "text/csv"
            )
        with col2:
            st.download_button(
                "📥 Poori History Download",
                df.to_csv(index=False),
                "attendance_full.csv",
                "text/csv"
            )

        if st.button("🗑️ Saari History Clear"):
            st.session_state.attendance = []
            save_json(ATTENDANCE_FILE, [])
            st.rerun()
