import sys
import os
import streamlit as st
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
from utils.auto_rotate import run_auto_rotate
run_auto_rotate()
# =========================
# PATH ROOT
# =========================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

BASE_DIR = ROOT_DIR

# =========================
# LOAD CSS (FIX)
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
css_path = os.path.join(BASE_DIR, "assets", "style.css")

with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================
# LOAD LOGO (AUTO DETECT)
# =========================
assets_path = os.path.join(BASE_DIR, "assets")
files = os.listdir(assets_path)

logo_candidates = [f for f in files if "logo" in f.lower()]
logo_file = logo_candidates[0]
logo_path = os.path.join(assets_path, logo_file)

# =========================
# HEADER
# =========================
col_logo, col_title = st.columns([3,8])

with col_logo:
    st.write("")
    st.write("")
    st.image(logo_path, width=340)

with col_title:
    st.write("")
    st.write("")
    st.markdown("## Dashboard Kepesertaan (Kumulatif Mingguan)")

# =========================
# IMPORT
# =========================
from components.card import kpi_card
from modules.query_sqlite import (
    get_iuran_pu, get_iuran_bpu, get_iuran_jakon,
    get_target_kantor,
    get_tren_iuran_pu, get_tren_iuran_bpu
)
from modules.utils import get_target_kumulatif
from modules.insight import generate_insight

# =========================
# FILTER
# =========================
col1, col2, col3 = st.columns(3)

bulan_map = {
    "Januari": 1,
    "Februari": 2,
    "Maret": 3,
    "April": 4,
    "Mei": 5,
    "Juni": 6,
    "Juli": 7,
    "Agustus": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Desember": 12
}


tahun = col1.selectbox("Tahun", [2026])
#bulan = col2.selectbox("Bulan", list(range(1,13)))
bulan_nama = col2.selectbox("Bulan", list(bulan_map.keys()))
bulan = bulan_map[bulan_nama]
minggu = col3.selectbox("Minggu", [1,2,3,4])

# =========================
# DATA
# =========================
target = get_target_kantor()

iuran_pu = get_iuran_pu(bulan, tahun)
iuran_bpu = get_iuran_bpu(bulan, tahun)
iuran_jakon = get_iuran_jakon(bulan, tahun)

target_pu = get_target_kumulatif(target["TARGET_IURAN_PU_BLN"], minggu)
target_bpu = get_target_kumulatif(target["TARGET_IURAN_BPU_BLN"], minggu)
target_jakon = get_target_kumulatif(target["TARGET_IURAN_JAKON_BLN"], minggu)

insight_pu = generate_insight(iuran_pu, target_pu, minggu)
insight_bpu = generate_insight(iuran_bpu, target_bpu, minggu)
insight_jakon = generate_insight(iuran_jakon, target_jakon, minggu)

# =========================
# KPI
# =========================
st.markdown('<div class="section-title">📊 Penerimaan Iuran</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

gap_pu = iuran_pu - target_pu
gap_bpu = iuran_bpu - target_bpu
gap_jakon = iuran_jakon - target_jakon

with col1:
    kpi_card("Iuran PU", f"Rp {iuran_pu:,}", gap_pu, insight_pu["progress"], insight_pu["status"])

with col2:
    kpi_card("Iuran BPU", f"Rp {iuran_bpu:,}", gap_bpu, insight_bpu["progress"], insight_bpu["status"])

with col3:
    kpi_card("Iuran Jakon", f"Rp {iuran_jakon:,}", gap_jakon, insight_jakon["progress"], insight_jakon["status"])

# =========================
# GRAFIK
# =========================
st.markdown('<div class="section-title">📊 Tren Iuran Bulanan</div>', unsafe_allow_html=True)

tren_pu = get_tren_iuran_pu(tahun)
tren_bpu = get_tren_iuran_bpu(tahun)

bulan_map = {
    1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
    7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"
}

tren_pu["Bulan"] = tren_pu["BLN"].map(bulan_map)
tren_bpu["Bulan"] = tren_bpu["BLN"].map(bulan_map)

fig_pu = px.line(tren_pu, x="Bulan", y="total", markers=True, title="Iuran PU")
fig_bpu = px.line(tren_bpu, x="Bulan", y="total", markers=True, title="Iuran BPU")

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_pu, use_container_width=True)

with col2:
    st.plotly_chart(fig_bpu, use_container_width=True)