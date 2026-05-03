import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
from utils.auto_rotate import run_auto_rotate
run_auto_rotate()
# =========================
# CONNECT DB
# =========================
conn = sqlite3.connect("database.db", check_same_thread=False)

# =========================
# PATH
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# =========================
# LOAD CSS
# =========================
css_path = os.path.join(BASE_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================
# LOAD LOGO
# =========================
assets_path = os.path.join(BASE_DIR, "assets")
logo_file = [f for f in os.listdir(assets_path) if "logo" in f.lower()][0]
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
    st.markdown("## Dashboard Perusahaan Terdaftar")

# =========================
# FILTER
# =========================
col1, col2 = st.columns(2)

tahun = col1.selectbox("Tahun", [2026])

bulan_map = {
    "Januari":1,"Februari":2,"Maret":3,"April":4,
    "Mei":5,"Juni":6,"Juli":7,"Agustus":8,
    "September":9,"Oktober":10,"November":11,"Desember":12
}

bulan_nama = col2.selectbox("Bulan", list(bulan_map.keys()))
bulan = bulan_map[bulan_nama]

# =========================
# KPI PU (FIX BENAR)
# =========================
q_pu = f"""
SELECT COUNT(TOTAL_PRS_PU) as total
FROM "DATA_TK_PU_HISTORY"
WHERE TAHUN = {tahun}
AND BLN = {bulan}
"""
df_pu = pd.read_sql(q_pu, conn)
prs_pu = df_pu.iloc[0]["total"] if not df_pu.empty else 0
prs_pu = prs_pu or 0

# =========================
# KPI BPU (FIX)
# =========================
q_bpu = f"""
SELECT SUM(TOTAL_PRS_BPU) as total
FROM DATA_TK_BPU_HISTORY
WHERE TAHUN = {tahun}
AND BLN = {bulan}
"""
df_bpu = pd.read_sql(q_bpu, conn)
prs_bpu = df_bpu.iloc[0]["total"] if not df_bpu.empty else 0
prs_bpu = prs_bpu or 0

# =========================
# KPI UI
# =========================
st.markdown("### 🏢 Perusahaan")

col1, col2 = st.columns(2)

col1.metric("Perusahaan PU", f"{int(prs_pu):,}")
col2.metric("Perusahaan BPU", f"{int(prs_bpu):,}")

# =========================
# DONUT SKALA USAHA
# =========================
q_skala = """
SELECT SKALA_USAHA, COUNT(*) as total
FROM "DATA_MONITORING_PERUSAHAAN"
GROUP BY SKALA_USAHA
"""
df_skala = pd.read_sql(q_skala, conn)

if df_skala.empty:
    st.warning("Data skala usaha tidak tersedia")
else:
    fig_donut = px.pie(
        df_skala,
        names="SKALA_USAHA",
        values="total",
        hole=0.6,
        title="Distribusi Skala Usaha"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# =========================
# HISTORICAL PU
# =========================
q_hist_pu = f"""
SELECT BLN, COUNT(TOTAL_PRS_PU) as total
FROM "DATA_TK_PU_HISTORY"
WHERE TAHUN = {tahun}
GROUP BY BLN
ORDER BY BLN
"""
df_hist_pu = pd.read_sql(q_hist_pu, conn)

# =========================
# HISTORICAL BPU
# =========================
q_hist_bpu = f"""
SELECT BLN, SUM(TOTAL_PRS_BPU) as total
FROM DATA_TK_BPU_HISTORY
WHERE TAHUN = {tahun}
GROUP BY BLN
ORDER BY BLN
"""
df_hist_bpu = pd.read_sql(q_hist_bpu, conn)

# =========================
# TARGET
# =========================
df_target = pd.read_sql("SELECT TARGET_PRS_PU_BLN FROM DATA_TARGET_SETUP_KANTOR", conn)
target_val = df_target.iloc[0]["TARGET_PU_PRS_BLN"] if not df_target.empty else 0
target_val = target_val or 0

# =========================
# HANDLE DATA KOSONG (WAJIB)
# =========================
def fill_bulan(df):
    bulan_all = pd.DataFrame({"BLN": list(range(1,13))})
    df_full = bulan_all.merge(df, on="BLN", how="left")

    df_full["total"] = df_full["total"].fillna(0)
    df_full["target"] = target_val

    return df_full

df_hist_pu = fill_bulan(df_hist_pu)
df_hist_bpu = fill_bulan(df_hist_bpu)

# =========================
# FORMAT BULAN
# =========================
bulan_map_short = {
    1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
    7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"
}

df_hist_pu["Bulan"] = df_hist_pu["BLN"].map(bulan_map_short)
df_hist_bpu["Bulan"] = df_hist_bpu["BLN"].map(bulan_map_short)

# =========================
# CHART PU
# =========================
fig_pu = go.Figure()

fig_pu.add_bar(x=df_hist_pu["Bulan"], y=df_hist_pu["total"], name="PU")

fig_pu.add_scatter(
    x=df_hist_pu["Bulan"],
    y=df_hist_pu["target"],
    mode="lines",
    name="Target",
    line=dict(color="red", dash="dash")
)

fig_pu.update_layout(title="Perusahaan PU (Historical vs Target)")

# =========================
# CHART BPU
# =========================
fig_bpu = go.Figure()

fig_bpu.add_bar(x=df_hist_bpu["Bulan"], y=df_hist_bpu["total"], name="BPU")

fig_bpu.add_scatter(
    x=df_hist_bpu["Bulan"],
    y=df_hist_bpu["target"],
    mode="lines",
    name="Target",
    line=dict(color="red", dash="dash")
)

fig_bpu.update_layout(title="Perusahaan BPU (Historical vs Target)")

# =========================
# DISPLAY
# =========================
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_pu, use_container_width=True)

with col2:
    st.plotly_chart(fig_bpu, use_container_width=True)