import sys
import os
import streamlit as st
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
#from utils.auto_rotate import run_auto_rotate
run_auto_rotate()
# =========================
# PATH ROOT
# =========================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

BASE_DIR = ROOT_DIR

# =========================
# LOAD CSS
# =========================
css_path = os.path.join(BASE_DIR, "assets", "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================
# LOAD LOGO
# =========================
assets_path = os.path.join(BASE_DIR, "assets")
files = os.listdir(assets_path)
logo_file = [f for f in files if "logo" in f.lower()][0]
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
    st.markdown("## Dashboard Tenaga Kerja")

# =========================
# IMPORT MODULE
# =========================
from components.card import kpi_card
from modules.query_sqlite import (
    get_tk_pu, get_tk_bpu, get_tk_jakon,
    get_target_kantor
)
from modules.utils import get_target_kumulatif
from modules.insight import generate_insight

# =========================
# FILTER
# =========================
col1, col2, col3 = st.columns(3)

tahun = col1.selectbox("Tahun", [2026])

bulan_map = {
    "Januari":1,"Februari":2,"Maret":3,"April":4,
    "Mei":5,"Juni":6,"Juli":7,"Agustus":8,
    "September":9,"Oktober":10,"November":11,"Desember":12
}

bulan_nama = col2.selectbox("Bulan", list(bulan_map.keys()))
bulan = bulan_map[bulan_nama]

minggu = col3.selectbox("Minggu", [1,2,3,4])

# =========================
# DATA
# =========================
target = get_target_kantor()

tk_pu = get_tk_pu(bulan, tahun)
tk_bpu = get_tk_bpu(bulan, tahun)
tk_jakon = get_tk_jakon(bulan, tahun)

# TARGET (pakai satu target TK dulu)
target_tk = get_target_kumulatif(target["TARGET_TK_BLN"], minggu)

# =========================
# INSIGHT
# =========================
insight_pu = generate_insight(tk_pu, target_tk, minggu)
insight_bpu = generate_insight(tk_bpu, target_tk, minggu)
insight_jakon = generate_insight(tk_jakon, target_tk, minggu)

# =========================
# KPI
# =========================
st.markdown('<div class="section-title">👷 Tenaga Kerja</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

gap_pu = tk_pu - target_tk
gap_bpu = tk_bpu - target_tk
gap_jakon = tk_jakon - target_tk

with col1:
    kpi_card("TK PU", f"{tk_pu:,}", gap_pu, insight_pu["progress"], insight_pu["status"])

with col2:
    kpi_card("TK BPU", f"{tk_bpu:,}", gap_bpu, insight_bpu["progress"], insight_bpu["status"])

with col3:
    kpi_card("TK Jakon", f"{tk_jakon:,}", gap_jakon, insight_jakon["progress"], insight_jakon["status"])

# =========================
# SIMPLE TREND (OPTIONAL)
# =========================
st.markdown('<div class="section-title">📊 Trend TK (Sederhana)</div>', unsafe_allow_html=True)

df = {
    "Kategori": ["PU","BPU","Jakon"],
    "Jumlah": [tk_pu, tk_bpu, tk_jakon]
}

fig = px.bar(df, x="Kategori", y="Jumlah", title="Perbandingan TK")

st.plotly_chart(fig, use_container_width=True)
