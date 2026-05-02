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

# ---- Language ----
if "lang" not in st.session_state:
    st.session_state.lang = "Hindi"

lang = st.session_state.lang

T = {
    "English": {
        "title": "TeaGuard", "subtitle": "AI-Powered Tea Garden Management System",
        "attendance": "Attendance", "garden_setup": "Garden Setup",
        "workers": "Workers", "chemicals": "Chemicals",
        "irrigation": "Irrigation", "dashboard": "Dashboard",
        "daily_attendance": "Daily Attendance", "worker_id": "Worker ID:",
        "enter_id": "Enter your Worker ID",
        "location": "Location (from Google Maps):",
        "lat": "Latitude", "lon": "Longitude",
        "take_photo": "Take Live Photo",
        "photo_warning": "Only camera photo accepted — no gallery!",
        "present": "PRESENT!", "failed": "FAILED!",
        "fake": "FAKE PHOTO!", "attendance_saved": "Attendance saved!",
        "worker_found": "Worker Found!", "worker_not_found": "Worker ID not found!",
        "garden_name": "Garden Name", "field_name": "Field Name",
        "field_number": "Field Number", "field_size": "Field Size (km)",
        "save_garden": "Save Garden & Field",
        "saved_gardens": "Saved Gardens & Fields",
        "register_worker": "Register Worker",
        "worker_name": "Worker Name", "worker_type": "Worker Type",
        "permanent": "Permanent", "temporary": "Temporary", "new": "New",
        "garden": "Garden", "field": "Field",
        "save_worker": "Save Worker",
        "registered_workers": "Registered Workers",
        "chemical_record": "Chemical Record",
        "chemical_name": "Chemical Name", "chemical_qty": "Quantity (Litre/KG)",
        "chemical_field": "Field Used In", "chemical_date": "Date",
        "save_chemical": "Save Chemical Record",
        "irrigation_record": "Irrigation Record",
        "irrigation_field": "Field", "irrigation_date": "Date",
        "irrigation_duration": "Duration (Hours)", "irrigation_type": "Type",
        "save_irrigation": "Save Irrigation Record",
        "weighment": "Tea Leaf Weighment (KG)",
        "daily_wage": "Daily Wage (₹)",
        "today_attendance": "Today's Attendance",
        "full_history": "Full History",
        "download_today": "Download Today's Report",
        "download_full": "Download Full History",
        "clear_history": "Clear All History",
        "setup_warning": "First setup Garden and register Workers!",
        "time_check": "Time", "face_check": "Face Check",
        "location_check": "Location", "face_found": "Face Found!",
        "face_not_found": "Face Not Found!", "fake_photo": "Fake Photo!",
        "correct_location": "Correct Location!", "wrong_location": "Wrong Location!",
    },
    "Hindi": {
        "title": "TeaGuard", "subtitle": "AI-Powered Tea Garden Management System",
        "attendance": "Attendance", "garden_setup": "Garden Setup",
        "workers": "Workers", "chemicals": "Chemicals",
        "irrigation": "Irrigation", "dashboard": "Dashboard",
        "daily_attendance": "Daily Attendance", "worker_id": "Worker ID:",
        "enter_id": "Apni Worker ID daalo",
        "location": "Location (Google Maps se):",
        "lat": "Latitude", "lon": "Longitude",
        "take_photo": "Live Photo Lo",
        "photo_warning": "Sirf camera se photo lo — gallery nahi chalegi!",
        "present": "PRESENT!", "failed": "FAILED!",
        "fake": "FAKE PHOTO!", "attendance_saved": "Attendance save ho gayi!",
        "worker_found": "Worker Mila!", "worker_not_found": "Worker ID nahi mila!",
        "garden_name": "Garden ka Naam", "field_name": "Field ka Naam",
        "field_number": "Field Number", "field_size": "Field Size (km)",
        "save_garden": "Garden & Field Save Karo",
        "saved_gardens": "Saved Gardens & Fields",
        "register_worker": "Worker Register Karo",
        "worker_name": "Worker ka Naam", "worker_type": "Worker Type",
        "permanent": "Permanent", "temporary": "Temporary", "new": "Naya",
        "garden": "Garden", "field": "Field",
        "save_worker": "Worker Save Karo",
        "registered_workers": "Registered Workers",
        "chemical_record": "Chemical Record",
        "chemical_name": "Chemical ka Naam", "chemical_qty": "Matra (Litre/KG)",
        "chemical_field": "Kis Field Mein", "chemical_date": "Tarikh",
        "save_chemical": "Chemical Record Save Karo",
        "irrigation_record": "Irrigation Record",
        "irrigation_field": "Field", "irrigation_date": "Tarikh",
        "irrigation_duration": "Kitni Der (Ghante)", "irrigation_type": "Prakar",
        "save_irrigation": "Irrigation Record Save Karo",
        "weighment": "Chai Patti Weighment (KG)",
        "daily_wage": "Daily Wage (₹)",
        "today_attendance": "Aaj ki Attendance",
        "full_history": "Poori History",
        "download_today": "Aaj ki Report Download",
        "download_full": "Poori History Download",
        "clear_history": "Saari History Clear Karo",
        "setup_warning": "Pehle Garden Setup karo aur Workers register karo!",
        "time_check": "Time", "face_check": "Face Check",
        "location_check": "Location", "face_found": "Face Mila!",
        "face_not_found": "Face Nahi Mila!", "fake_photo": "Fake Photo!",
        "correct_location": "Sahi Location!", "wrong_location": "Galat Location!",
    }
}

t = T[lang]

# ---- CSS ----
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0d1b0f 0%, #1a2e1c 50%, #0d1b0f 100%); color: white; }
    h1, h2, h3 { color: #4ade80 !important; }
    .stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.05); border-radius: 15px; padding: 5px; gap: 5px; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #9ca3af; border-radius: 10px; font-weight: 600; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #16a34a, #15803d) !important; color: white !important; }
    .stTextInput input { background: rgba(255,255,255,0.08) !important; border: 1px solid rgba(74,222,128,0.3) !important; border-radius: 10px !important; color: white !important; }
    .stButton button { background: linear-gradient(135deg, #16a34a, #15803d) !important; color: white !important; border: none !important; border-radius: 12px !important; font-weight: 600 !important; width: 100% !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---- Language Toggle ----
col_lang1, col_lang2, col_lang3 = st.columns([6, 1, 1])
with col_lang2:
    if st.button("🇮🇳 Hindi"):
        st.session_state.lang = "Hindi"
        st.rerun()
with col_lang3:
    if st.button("🇬🇧 English"):
        st.session_state.lang = "English"
        st.rerun()

# ---- Header ----
st.markdown(f"""
<div style="text-align:center; padding:30px 20px;
    background: linear-gradient(135deg, rgba(22,163,74,0.15), rgba(21,128,61,0.1));
    border-radius: 20px; border: 1px solid rgba(74,222,128,0.2); margin-bottom: 30px;">
    <div style="font-size:50px;">🌿</div>
    <h1 style="font-size:38px; font-weight:700; color:#4ade80; margin:0;">{t['title']}</h1>
    <p style="color:#9ca3af; font-size:16px; margin-top:8px;">{t['subtitle']}</p>
    <div style="display:flex; justify-content:center; gap:15px; margin-top:15px; flex-wrap:wrap;">
        <span style="background:rgba(74,222,128,0.1); border:1px solid rgba(74,222,128,0.3); padding:6px 16px; border-radius:20px; color:#4ade80; font-size:13px;">📍 GPS Verify</span>
        <span style="background:rgba(74,222,128,0.1); border:1px solid rgba(74,222,128,0.3); padding:6px 16px; border-radius:20px; color:#4ade80; font-size:13px;">👤 Face Detection</span>
        <span style="background:rgba(74,222,128,0.1); border:1px solid rgba(74,222,128,0.3); padding:6px 16px; border-radius:20px; color:#4ade80; font-size:13px;">🧪 Chemical Record</span>
        <span style="background:rgba(74,222,128,0.1); border:1px solid rgba(74,222,128,0.3); padding:6px 16px; border-radius:20px; color:#4ade80; font-size:13px;">💧 Irrigation</span>
        <span style="background:rgba(74,222,128,0.1); border:1px solid rgba(74,222,128,0.3); padding:6px 16px; border-radius:20px; color:#4ade80; font-size:13px;">⚖️ Weighment</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- Files ----
GARDENS_FILE = "gardens.json"
WORKERS_FILE = "workers.json"
ATTENDANCE_FILE = "attendance.json"
CHEMICALS_FILE = "chemicals.json"
IRRIGATION_FILE = "irrigation.json"

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
if "chemicals" not in st.session_state:
    st.session_state.chemicals = load_json(CHEMICALS_FILE, [])
if "irrigation" not in st.session_state:
    st.session_state.irrigation = load_json(IRRIGATION_FILE, [])

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    f"📸 {t['attendance']}",
    f"🏡 {t['garden_setup']}",
    f"👷 {t['workers']}",
    f"🧪 {t['chemicals']}",
    f"💧 {t['irrigation']}",
    f"📊 {t['dashboard']}"
])

# ================================================
# TAB 2 - Garden Setup
# ================================================
with tab2:
    st.markdown(f"### 🏡 {t['garden_setup']}")
    st.info("Ek baar set karo — hamesha save rahega!")

    garden_name = st.text_input(t['garden_name'], key="gname")
    col1, col2 = st.columns(2)
    with col1:
        field_name = st.text_input(t['field_name'], key="fname")
        clat = st.number_input(t['lat'], value=31.50, format="%.6f")
    with col2:
        field_number = st.text_input(t['field_number'], key="fnum")
        clon = st.number_input(t['lon'], value=74.85, format="%.6f")
    radius = st.slider(t['field_size'], 0.1, 5.0, 0.5, 0.1)

    if st.button(f"💾 {t['save_garden']}"):
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
        st.markdown(f"### {t['saved_gardens']}:")
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
# TAB 3 - Workers
# ================================================
with tab3:
    st.markdown(f"### 👷 {t['register_worker']}")
    col1, col2 = st.columns(2)
    with col1:
        w_id = st.text_input("Worker ID (W001):")
        w_name = st.text_input(t['worker_name'])
        w_wage = st.number_input(t['daily_wage'], min_value=0, value=400)
    with col2:
        w_type = st.selectbox(t['worker_type'], [t['permanent'], t['temporary'], t['new']])
        w_garden = st.selectbox(t['garden'], options=list(st.session_state.gardens.keys()) if st.session_state.gardens else ["Pehle garden set karo"])
        if st.session_state.gardens and w_garden in st.session_state.gardens:
            w_field = st.selectbox(t['field'], options=list(st.session_state.gardens[w_garden].keys()))
        else:
            w_field = ""

    if st.button(f"✅ {t['save_worker']}"):
        if w_id and w_name:
            st.session_state.workers[w_id] = {
                "naam": w_name, "type": w_type,
                "garden": w_garden, "field": w_field,
                "wage": w_wage
            }
            save_json(WORKERS_FILE, st.session_state.workers)
            st.success(f"✅ {w_name} (ID: {w_id}) register ho gaya!")

    if st.session_state.workers:
        st.markdown(f"### {t['registered_workers']}:")
        df_w = pd.DataFrame([
            {"ID": wid, "Naam": d["naam"], "Type": d["type"],
             "Garden": d["garden"], "Field": d["field"], "Wage": f"₹{d['wage']}"}
            for wid, d in st.session_state.workers.items()
        ])
        st.dataframe(df_w, use_container_width=True)

# ================================================
# TAB 4 - Chemicals
# ================================================
with tab4:
    st.markdown(f"### 🧪 {t['chemical_record']}")

    col1, col2 = st.columns(2)
    with col1:
        chem_name = st.text_input(t['chemical_name'])
        chem_qty = st.number_input(t['chemical_qty'], min_value=0.0, value=1.0)
    with col2:
        chem_field = st.selectbox(
            t['chemical_field'],
            options=[f for g in st.session_state.gardens.values() for f in g.keys()] or ["Pehle field set karo"]
        )
        chem_date = st.date_input(t['chemical_date'])
    chem_notes = st.text_area("Notes (optional):")

    if st.button(f"💾 {t['save_chemical']}"):
        if chem_name:
            st.session_state.chemicals.append({
                "Date": str(chem_date),
                "Chemical": chem_name,
                "Quantity": chem_qty,
                "Field": chem_field,
                "Notes": chem_notes
            })
            save_json(CHEMICALS_FILE, st.session_state.chemicals)
            st.success(f"✅ {chem_name} record save ho gaya!")

    if st.session_state.chemicals:
        st.markdown("### Chemical History:")
        df_c = pd.DataFrame(st.session_state.chemicals)
        st.dataframe(df_c, use_container_width=True)
        st.download_button("📥 Download", df_c.to_csv(index=False), "chemicals.csv", "text/csv")

# ================================================
# TAB 5 - Irrigation
# ================================================
with tab5:
    st.markdown(f"### 💧 {t['irrigation_record']}")

    col1, col2 = st.columns(2)
    with col1:
        irr_field = st.selectbox(
            t['irrigation_field'],
            options=[f for g in st.session_state.gardens.values() for f in g.keys()] or ["Pehle field set karo"],
            key="ifield"
        )
        irr_duration = st.number_input(t['irrigation_duration'], min_value=0.0, value=1.0)
    with col2:
        irr_date = st.date_input(t['irrigation_date'], key="idate")
        irr_type = st.selectbox(t['irrigation_type'], ["Drip", "Sprinkler", "Flood", "Manual"])
    irr_notes = st.text_area("Notes:", key="inotes")

    if st.button(f"💾 {t['save_irrigation']}"):
        st.session_state.irrigation.append({
            "Date": str(irr_date),
            "Field": irr_field,
            "Type": irr_type,
            "Duration (hrs)": irr_duration,
            "Notes": irr_notes
        })
        save_json(IRRIGATION_FILE, st.session_state.irrigation)
        st.success("✅ Irrigation record save ho gaya!")

    if st.session_state.irrigation:
        st.markdown("### Irrigation History:")
        df_i = pd.DataFrame(st.session_state.irrigation)
        st.dataframe(df_i, use_container_width=True)
        st.download_button("📥 Download", df_i.to_csv(index=False), "irrigation.csv", "text/csv")

# ================================================
# TAB 1 - Daily Attendance
# ================================================
with tab1:
    st.markdown(f"### 📸 {t['daily_attendance']}")

    if not st.session_state.gardens or not st.session_state.workers:
        st.warning(f"⚠️ {t['setup_warning']}")
    else:
        worker_id = st.text_input(t['worker_id'], placeholder=t['enter_id'])

        worker_info = None
        if worker_id and worker_id in st.session_state.workers:
            worker_info = st.session_state.workers[worker_id]
            st.markdown(f"""
            <div style="background:rgba(74,222,128,0.1); border:1px solid rgba(74,222,128,0.3);
                border-radius:12px; padding:16px; margin:10px 0;">
                <b style="color:#4ade80;">✅ {t['worker_found']}</b><br>
                <span style="color:white;">👤 {worker_info['naam']}</span>
                <span style="background:rgba(74,222,128,0.2); border-radius:20px; padding:3px 10px;
                    color:#4ade80; font-size:12px; margin-left:10px;">{worker_info['type']}</span><br>
                <span style="color:#9ca3af;">🏡 {worker_info['garden']} — 📍 {worker_info['field']}</span>
            </div>
            """, unsafe_allow_html=True)
        elif worker_id:
            st.error(f"❌ {t['worker_not_found']}")

        st.markdown(f"### 📍 {t['location']}")
        col1, col2 = st.columns(2)
        with col1:
            lat_in = st.number_input(t['lat'], value=0.0, format="%.6f", key="alat")
        with col2:
            lon_in = st.number_input(t['lon'], value=0.0, format="%.6f", key="alon")

        # Weighment
        weighment = st.number_input(f"⚖️ {t['weighment']}", min_value=0.0, value=0.0)

        st.markdown(f"### 📸 {t['take_photo']}")
        st.warning(f"⚠️ {t['photo_warning']}")
        camera_photo = st.camera_input("📷")

        if camera_photo and worker_info and lat_in != 0.0:
            img = Image.open(camera_photo)

            arr = np.array(img.convert("RGB"))
            gray = cv2.cvtColor(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
            fc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = fc.detectMultiScale(gray, 1.1, 5)
            face_found = len(faces) > 0
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            is_fake = blur_score < 30

            lat = lat_in
            lon = lon_in
            garden = worker_info["garden"]
            expected_field = worker_info["field"]
            field_bounds = st.session_state.gardens.get(garden, {}).get(expected_field, {})

            location_ok = False
            if field_bounds:
                location_ok = (
                    field_bounds["lat_min"] <= lat <= field_bounds["lat_max"] and
                    field_bounds["lon_min"] <= lon <= field_bounds["lon_max"]
                )

            now = datetime.datetime.now()

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div style="background:rgba(74,222,128,0.1); border:1px solid rgba(74,222,128,0.3);
                    border-radius:12px; padding:20px; text-align:center;">
                    <div style="font-size:28px;">⏰</div>
                    <div style="color:#4ade80; font-weight:600;">{t['time_check']}</div>
                    <div style="color:white; font-size:13px;">{now.strftime('%d %b %Y')}</div>
                    <div style="color:#4ade80; font-weight:600;">{now.strftime('%I:%M %p')}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                fc_color = "#4ade80" if face_found and not is_fake else "#ef4444"
                fc_icon = "✅" if face_found and not is_fake else "❌"
                fc_text = t['face_found'] if face_found and not is_fake else (t['fake_photo'] if is_fake else t['face_not_found'])
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); border:1px solid {fc_color}40;
                    border-radius:12px; padding:20px; text-align:center;">
                    <div style="font-size:28px;">{fc_icon}</div>
                    <div style="color:{fc_color}; font-weight:600;">{t['face_check']}</div>
                    <div style="color:white; font-size:13px;">{fc_text}</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                lc_color = "#4ade80" if location_ok else "#ef4444"
                lc_icon = "✅" if location_ok else "❌"
                lc_text = t['correct_location'] if location_ok else t['wrong_location']
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); border:1px solid {lc_color}40;
                    border-radius:12px; padding:20px; text-align:center;">
                    <div style="font-size:28px;">{lc_icon}</div>
                    <div style="color:{lc_color}; font-weight:600;">{t['location_check']}</div>
                    <div style="color:white; font-size:13px;">{lc_text}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if face_found and location_ok and not is_fake:
                status = "Present"
                salary_today = worker_info.get("wage", 400)
                st.markdown(f"""
                <div style="background:linear-gradient(135deg, rgba(22,163,74,0.2), rgba(21,128,61,0.1));
                    border:2px solid #4ade80; border-radius:15px; padding:25px; text-align:center;">
                    <div style="font-size:50px;">✅</div>
                    <div style="color:#4ade80; font-size:24px; font-weight:700;">{t['present']}</div>
                    <div style="color:#9ca3af; margin-top:8px;">
                        ⚖️ Weighment: {weighment} KG &nbsp;|&nbsp; 💰 Aaj ki Salary: ₹{salary_today}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif is_fake:
                status = "Fake Photo"
                salary_today = 0
                st.markdown(f"""
                <div style="background:linear-gradient(135deg, rgba(239,68,68,0.2), rgba(185,28,28,0.1));
                    border:2px solid #ef4444; border-radius:15px; padding:25px; text-align:center;">
                    <div style="font-size:50px;">🚨</div>
                    <div style="color:#ef4444; font-size:24px; font-weight:700;">{t['fake']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                status = "Absent"
                salary_today = 0
                st.markdown(f"""
                <div style="background:linear-gradient(135deg, rgba(239,68,68,0.2), rgba(185,28,28,0.1));
                    border:2px solid #ef4444; border-radius:15px; padding:25px; text-align:center;">
                    <div style="font-size:50px;">❌</div>
                    <div style="color:#ef4444; font-size:24px; font-weight:700;">{t['failed']}</div>
                </div>
                """, unsafe_allow_html=True)

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

            record = {
                "Date": now.strftime('%d %b %Y'),
                "Time": now.strftime('%I:%M %p'),
                "Worker ID": worker_id,
                "Naam": worker_info["naam"],
                "Type": worker_info["type"],
                "Garden": worker_info["garden"],
                "Field": worker_info["field"],
                "Lat": lat, "Lon": lon,
                "Weighment (KG)": weighment,
                "Salary (₹)": salary_today,
                "Face": "✅" if face_found else "❌",
                "Location": "✅" if location_ok else "❌",
                "Status": status
            }
            st.session_state.attendance.append(record)
            save_json(ATTENDANCE_FILE, st.session_state.attendance)
            st.success(f"✅ {t['attendance_saved']}")

# ================================================
# TAB 6 - Dashboard
# ================================================
with tab6:
    st.markdown(f"### 📊 {t['dashboard']}")

    today = datetime.datetime.now().strftime('%d %b %Y')

    subtab1, subtab2, subtab3 = st.tabs(["📅 Aaj", "📋 Poori History", "💰 Payroll"])

    with subtab1:
        if not st.session_state.attendance:
            st.info("Koi record nahi abhi")
        else:
            df = pd.DataFrame(st.session_state.attendance)
            df_today = df[df["Date"] == today]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📊 Total", len(df_today))
            c2.metric("✅ Present", len(df_today[df_today["Status"] == "Present"]))
            c3.metric("❌ Absent", len(df_today[df_today["Status"] == "Absent"]))
            c4.metric("🚨 Fake", len(df_today[df_today["Status"] == "Fake Photo"]))

            if len(df_today) > 0:
                st.dataframe(df_today, use_container_width=True)
                st.download_button(
                    f"📥 {t['download_today']}",
                    df_today.to_csv(index=False),
                    f"attendance_{today}.csv", "text/csv"
                )

    with subtab2:
        if not st.session_state.attendance:
            st.info("Koi record nahi")
        else:
            df = pd.DataFrame(st.session_state.attendance)
            st.dataframe(df, use_container_width=True)
            st.download_button(
                f"📥 {t['download_full']}",
                df.to_csv(index=False),
                "attendance_full.csv", "text/csv"
            )
            if st.button(f"🗑️ {t['clear_history']}"):
                st.session_state.attendance = []
                save_json(ATTENDANCE_FILE, [])
                st.rerun()

    with subtab3:
        st.markdown("### 💰 Payroll Calculator")
        if not st.session_state.attendance:
            st.info("Koi attendance record nahi")
        else:
            df = pd.DataFrame(st.session_state.attendance)
            df_present = df[df["Status"] == "Present"]

            if len(df_present) > 0:
                payroll = df_present.groupby(["Worker ID", "Naam", "Type"]).agg(
                    Days_Present=("Status", "count"),
                    Total_Weighment=("Weighment (KG)", "sum"),
                    Total_Salary=("Salary (₹)", "sum")
                ).reset_index()

                st.dataframe(payroll, use_container_width=True)
                st.download_button(
                    "📥 Payroll Download",
                    payroll.to_csv(index=False),
                    "payroll.csv", "text/csv"
                )
                
