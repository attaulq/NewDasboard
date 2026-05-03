import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import os

conn = sqlite3.connect("database.db", check_same_thread=False)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# =========================
# IDENTITAS AR
# =========================
KODE_NIK = "WY255440"

from utils.auto_rotate import run_auto_rotate
run_auto_rotate()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
css_path = os.path.join(BASE_DIR, "assets", "style.css")

with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================
# AUTO DATE (FIX - TIDAK DOUBLE)
# =========================
from datetime import datetime

today = datetime.today()

bulan_map = {
    "Januari":1,"Februari":2,"Maret":3,"April":4,
    "Mei":5,"Juni":6,"Juli":7,"Agustus":8,
    "September":9,"Oktober":10,"November":11,"Desember":12
}

tahun_default = today.year
bulan_default = today.month
tanggal = today.day

minggu_default = min((tanggal - 1) // 7 + 1, 4)

# =========================
# FILTER (URUTAN DIPERBAIKI)
# =========================
col1, col2, col3 = st.columns(3)

tahun = col1.selectbox("Tahun", [2026], index=0)

bulan_list = list(bulan_map.keys())
bulan_index = list(bulan_map.values()).index(bulan_default)

bulan_nama = col2.selectbox("Bulan", bulan_list, index=bulan_index)
bulan = bulan_map[bulan_nama]

minggu = col3.selectbox("Minggu", [1,2,3,4], index=minggu_default-1)

# =========================
# INFO PERIODE (PINDAH KE SINI)
# =========================
st.caption(f"Periode otomatis: {bulan_nama} {tahun} • Minggu {minggu}")

# =========================
# FORMAT BULAN
# =========================
def format_bulan(df):
    if df is None or df.empty:
        return pd.DataFrame({"Bulan":[], "nilai":[]})

    df = df.copy()

    bulan_map2 = {
        1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
        7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"
    }

    if "BLN" in df.columns:
        df["Bulan"] = df["BLN"].map(bulan_map2)
    else:
        df["Bulan"] = "-"

    if "nilai" not in df.columns:
        df["nilai"] = 0

    return df

# =========================
# HISTORICAL DATA
# =========================
# PU
hist_pu = pd.read_sql(f"""
SELECT BLN, SUM(TOTAL_IURAN) as nilai
FROM "DATA_MONITORING_PERUSAHAAN"
WHERE KODE_NIK='{KODE_NIK}' AND TAHUN={tahun}
GROUP BY BLN
ORDER BY BLN
""", conn)

# BPU
hist_bpu = pd.read_sql(f"""
SELECT BLN, SUM(TOTAL_IURAN) as nilai
FROM DATA_MONITORING_IURAN_PU_BARU
WHERE KODE_NIK='{KODE_NIK}' AND TAHUN={tahun}
GROUP BY BLN
ORDER BY BLN
""", conn)

# TK PU
hist_tk_pu = pd.read_sql(f"""
SELECT BLN, SUM(TK_AKTIF) as nilai
FROM "DATA_MONITORING_PERUSAHAAN"
WHERE KODE_NIK='{KODE_NIK}' AND TAHUN={tahun}
GROUP BY BLN
ORDER BY BLN
""", conn)

# TK BPU
hist_tk_bpu = pd.read_sql(f"""
SELECT BLN, SUM(TOTAL_TK_BPU) as nilai
FROM DATA_TK_BPU_HISTORY
WHERE KODE_NIK='{KODE_NIK}' AND TAHUN={tahun}
GROUP BY BLN
ORDER BY BLN
""", conn)

# =========================
# TARGET
# =========================
df_target = pd.read_sql(f"""
SELECT *
FROM DATA_TARGET_SETUP_AR
WHERE KODE_NIK = '{KODE_NIK}'
LIMIT 1
""", conn)

target = df_target.iloc[0].to_dict() if not df_target.empty else {}

# =========================
# PREP DATA
# =========================
def prep_hist(df, nama):
    df = format_bulan(df)
    df = df.rename(columns={"nilai": nama})
    return df[["Bulan", nama]]

df_pu  = prep_hist(hist_pu, "PU")
df_bpu = prep_hist(hist_bpu, "BPU")

df_iuran = df_pu.merge(df_bpu, on="Bulan", how="outer").fillna(0)

df_iuran["T_PU"]  = target.get("TARGET_IURAN_PU_BLN", 0)
df_iuran["T_BPU"] = target.get("TARGET_IURAN_BPU_BLN", 0)

# =========================
# CHART IURAN
# =========================
st.markdown("### 📊 Grafik Iuran PU & BPU")

bulan_singkat = {
    "Januari":"Jan","Februari":"Feb","Maret":"Mar","April":"Apr",
    "Mei":"Mei","Juni":"Jun","Juli":"Jul","Agustus":"Agu",
    "September":"Sep","Oktober":"Okt","November":"Nov","Desember":"Des"
}
bulan_aktif = bulan_singkat[bulan_nama]

def warna_bar(real, target):
    return ["#E53935" if r < target else "#43A047" for r in real]

fig = go.Figure()

fig.add_bar(x=df_iuran["Bulan"], y=df_iuran["PU"], name="PU",
            marker_color=warna_bar(df_iuran["PU"], df_iuran["T_PU"]))

fig.add_bar(x=df_iuran["Bulan"], y=df_iuran["BPU"], name="BPU",
            marker_color=warna_bar(df_iuran["BPU"], df_iuran["T_BPU"]))

fig.add_scatter(x=df_iuran["Bulan"], y=df_iuran["T_PU"],
                name="Target PU", mode="lines", line=dict(dash="dash"))

fig.add_scatter(x=df_iuran["Bulan"], y=df_iuran["T_BPU"],
                name="Target BPU", mode="lines", line=dict(dash="dash"))

fig.add_vline(x=bulan_aktif, line_dash="dot", line_color="blue")

fig.update_layout(barmode="group", template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

# =========================
# CHART TK
# =========================
st.markdown("### 👷 Grafik Tenaga Kerja PU & BPU")

df_tkpu = prep_hist(hist_tk_pu, "PU")
df_tkbpu = prep_hist(hist_tk_bpu, "BPU")

df_tk = df_tkpu.merge(df_tkbpu, on="Bulan", how="outer").fillna(0)

df_tk["T_PU"]  = target.get("TARGET_TK_PU_BLN", 0)
df_tk["T_BPU"] = target.get("TARGET_TK_BPU_BLN", 0)

fig2 = go.Figure()

fig2.add_bar(x=df_tk["Bulan"], y=df_tk["PU"], name="TK PU",
             marker_color=warna_bar(df_tk["PU"], df_tk["T_PU"]))

fig2.add_bar(x=df_tk["Bulan"], y=df_tk["BPU"], name="TK BPU",
             marker_color=warna_bar(df_tk["BPU"], df_tk["T_BPU"]))

fig2.add_scatter(x=df_tk["Bulan"], y=df_tk["T_PU"],
                 name="Target PU", mode="lines", line=dict(dash="dash"))

fig2.add_scatter(x=df_tk["Bulan"], y=df_tk["T_BPU"],
                 name="Target BPU", mode="lines", line=dict(dash="dash"))

fig2.add_vline(x=bulan_aktif, line_dash="dot", line_color="blue")

fig2.update_layout(barmode="group", template="plotly_white")

st.plotly_chart(fig2, use_container_width=True)

# =========================
# TABLE
# =========================
st.markdown("### 📋 Detail Historical Iuran")
st.dataframe(df_iuran, use_container_width=True)

st.markdown("### 📋 Detail Historical Tenaga Kerja")
st.dataframe(df_tk, use_container_width=True)