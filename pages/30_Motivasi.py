import streamlit as st
import pandas as pd
import sqlite3
import os
import time


st.title("Motivasi")
st.set_page_config(layout="wide")

st.title("BPJS Ketenagakerjaan Dashboard Kepesertaan")
st.write("Pilih menu di sidebar")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
img_path = os.path.join(BASE_DIR, "assets", "Kacab_Pontianak_Juara.png")

st.image("assets/Kacab_Pontianak_Juara.png")

# =========================
# STYLE SIDEBAR
# =========================
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #0B3C6F !important;
}
[data-testid="stSidebar"] * {
    color: #FFD700 !important;
}
[data-testid="stSidebarNav"] a {
    color: #FFD700 !important;
}
[data-testid="stSidebarNav"] a:hover {
    background-color: #1E5FA8 !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #4A90E2 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# PAGES
# =========================
pages = [
    "1_Dashboard","2_Tenaga_Kerja","3_Perusahaan",
    "4_AR_AGUNG","5_AR_AGUNG_DETIL",
    "6_AR_ATTA_UL_Q","7_AR_ATTA_UL_Q_DETIL",
    "8_AR_BAYU","9_AR_BAYU_DETIL",
    "10_AR_IRAWAN","11_AR_IRAWAN_DETIL",
    "12_AR_DHIKA","13_AR_DHIKA_DETIL",
    "14_ARK_ABHIMATA","15_ARK_ABHIMATA_DETIL",
    "16_ARK_ANNA","17_ARK_ANNA_DETIL",
    "18_ARK_FRANS","19_ARK_FRANS_DETIL",
    "20_ARK_IQBAL","21_ARK_IQBAL_DETIL",
    "22_ARK_JEFRY","23_ARK_JEFRY_DETIL",
    "24_ARK_TIO","25_ARK_TIO_DETIL",
    "26_ARK_WYANDRA","27_ARK_WYANDRA_DETIL","28_Motivasi"
]

# =========================
# STATE
# =========================
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "last_switch" not in st.session_state:
    st.session_state.last_switch = time.time()
if "rotate_seconds" not in st.session_state:
    st.session_state.rotate_seconds = 6
if "auto_rotate" not in st.session_state:
    st.session_state.auto_rotate = False
if "tv_mode" not in st.session_state:
    st.session_state.tv_mode = False

# =========================
# SIDEBAR CONTROL
# =========================
st.sidebar.markdown("## ⚙️ Control Dashboard")

st.session_state.rotate_seconds = st.sidebar.selectbox(
    "⏱️ Waktu Rotasi",
    [3,6,9,12,15],
    index=[3,6,9,12,15].index(st.session_state.rotate_seconds)
)

st.session_state.auto_rotate = st.sidebar.toggle("▶️ Rotasi", value=st.session_state.auto_rotate)
st.session_state.tv_mode = st.sidebar.toggle("📺 Mode TV", value=st.session_state.tv_mode)

# =========================
# MODE TV (FIX FINAL)
# =========================
if st.session_state.tv_mode:

    st.markdown("""
    <style>

    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}

    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }

    [data-testid="stAppViewContainer"] {
        padding: 0 !important;
        margin: 0 !important;
    }

    img {
        width: 100vw !important;
        height: 100vh !important;
        object-fit: contain !important;
        background-color: black;
    }

    .top-bar {
        position: fixed;
        top: 15px;
        right: 20px;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(0,0,0,0.4);
        padding: 8px 14px;
        border-radius: 12px;
    }

    .top-text {
        color: white;
        font-size: 14px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ESC KEY
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(e) {
        if (e.key === "Escape") {
            window.location.reload();
        }
    });
    </script>
    """, unsafe_allow_html=True)

    # TOMBOL KELUAR
    col1, col2 = st.columns([8,1])
    with col2:
        if st.button("⚙️"):
            st.session_state.tv_mode = False
            st.rerun()

# =========================
# HEADER
# =========================
current_page = pages[st.session_state.idx]
judul = current_page.replace("_"," ")

st.markdown(f"""
<div style="text-align:center;font-size:24px;font-weight:700;">
{judul}
</div>
""", unsafe_allow_html=True)

# =========================
# ROTATE
# =========================
if st.session_state.auto_rotate:
    now = time.time()
    if now - st.session_state.last_switch >= st.session_state.rotate_seconds:
        st.session_state.idx = (st.session_state.idx + 1) % len(pages)
        st.session_state.last_switch = now
        st.switch_page(f"pages/{pages[st.session_state.idx]}.py")

# =========================
# START
# =========================
if "started" not in st.session_state:
    st.session_state.started = True
    st.switch_page(f"pages/{pages[0]}.py")

# =========================
# LOOP
# =========================
time.sleep(1)
st.rerun()