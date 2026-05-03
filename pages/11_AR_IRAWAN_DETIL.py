import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
import os

conn = sqlite3.connect("database.db", check_same_thread=False)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

KODE_NIK = "IR166170"

from utils.auto_rotate import run_auto_rotate
run_auto_rotate()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
css_path = os.path.join(BASE_DIR, "assets", "style.css")

with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================
# AUTO DATE (FIX)
# =========================
from datetime import datetime

today = datetime.today()

tahun_default = today.year
bulan_default = today.month
tanggal = today.day
minggu_default = min((tanggal - 1) // 7 + 1, 4)

# =========================
# BULAN MAP (ASLI)
# =========================
bulan_map = {
    "Januari":1,"Februari":2,"Maret":3,"April":4,
    "Mei":5,"Juni":6,"Juli":7,"Agustus":8,
    "September":9,"Oktober":10,"November":11,"Desember":12
}

# =========================
# FILTER (FIX)
# =========================
f1, f2, f3 = st.columns(3)
col1, col2, col3 = st.columns(3)

tahun = col1.selectbox("Tahun", [2026], index=0)

bulan_list = list(bulan_map.keys())
bulan_index = list(bulan_map.values()).index(bulan_default)

bulan_nama = col2.selectbox("Bulan", bulan_list, index=bulan_index)
bulan = bulan_map[bulan_nama]

minggu = col3.selectbox("Minggu", [1,2,3,4], index=minggu_default-1)

# =========================
# INFO PERIODE (DIPINDAH KE BAWAH)
# =========================
st.caption(f"Periode otomatis: {bulan_nama} {tahun} • Minggu {minggu}")

# =========================
# (SISA FILE ASLI — TIDAK DIUBAH)
# =========================

def format_bulan(df):

    if df is None or df.empty:
        return pd.DataFrame({"Bulan":[], "nilai":[]})

    df = df.copy()

    if "BLN" in df.columns:
        df["Bulan"] = df["BLN"].map(bulan_map)
    else:
        df["Bulan"] = "-"

    if "nilai" not in df.columns:
        df["nilai"] = 0

    return df

# =========================
# HISTORICAL PU
# =========================
q_hist_pu = f"""
SELECT BLN, SUM(TOTAL_IURAN) as total
FROM "DATA_MONITORING_PERUSAHAAN"
WHERE KODE_NIK = '{KODE_NIK}'
AND TAHUN = {tahun}
GROUP BY BLN
ORDER BY BLN
"""
df_pu = pd.read_sql(q_hist_pu, conn)

# =========================
# TARGET
# =========================
target = pd.read_sql(
    f"SELECT TARGET_IURAN_PU_BLN FROM DATA_TARGET_SETUP_AR WHERE KODE_NIK='{KODE_NIK}'",
    conn
)

target_val = target.iloc[0][0] if not target.empty else 0

df_pu["target"] = target_val

# =========================
# BULAN
# =========================
bulan_map = {
    1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
    7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"
}
df_pu["Bulan"] = df_pu["BLN"].map(bulan_map)

# =========================
# IURAN BPU
# =========================
hist_bpu = pd.read_sql(f"""
SELECT BLN, SUM(TOTAL_IURAN) as nilai
FROM DATA_MONITORING_IURAN_PU_BARU
WHERE KODE_NIK='{KODE_NIK}' AND TAHUN={tahun}
GROUP BY BLN
ORDER BY BLN
""", conn)
df_bpu = format_bulan(hist_bpu)

# =========================
# IURAN JAKON
# =========================
hist_jakon = pd.read_sql(f"""
SELECT BLN, SUM(TOTAL_IURAN) as nilai
FROM DATA_IURAN_JAKON_HISTORY
WHERE KODE_NIK='{KODE_NIK}' AND TAHUN={tahun}
GROUP BY BLN
ORDER BY BLN
""", conn)

# =========================
# TK PU
# =========================
hist_tk_pu = pd.read_sql(f"""
SELECT BLN, SUM(TK_AKTIF) as nilai
FROM "DATA_MONITORING_PERUSAHAAN"
WHERE KODE_NIK='{KODE_NIK}' AND TAHUN={tahun}
GROUP BY BLN
ORDER BY BLN
""", conn)

# =========================
# TK BPU
# =========================
hist_tk_bpu = pd.read_sql(f"""
SELECT BLN, SUM(TOTAL_TK_BPU) as nilai
FROM DATA_TK_BPU_HISTORY
WHERE KODE_NIK='{KODE_NIK}' AND TAHUN={tahun}
GROUP BY BLN
ORDER BY BLN
""", conn)

# =========================
# GRAFIK IURAN
# =========================
st.markdown("### 📊 Grafik Iuran PU, BPU, dan Jasa Konstruksi", unsafe_allow_html=True)

def prep_hist(df, nama):
    df = format_bulan(df)
    df = df.rename(columns={"nilai": nama, "total": nama})
    return df[["Bulan", nama]] if "Bulan" in df.columns else pd.DataFrame()

df_pu2   = prep_hist(df_pu.rename(columns={"total":"nilai"}), "PU")
df_bpu2  = prep_hist(hist_bpu, "BPU")
df_jakon2= prep_hist(hist_jakon, "JAKON")

df_iuran = df_pu2.merge(df_bpu2, on="Bulan", how="outer") \
                .merge(df_jakon2, on="Bulan", how="outer") \
                .fillna(0)

df_iuran["T_PU"]    = target_val
df_iuran["T_BPU"]   = target.get("TARGET_IURAN_BPU_BLN", 0)
df_iuran["T_JAKON"] = target.get("TARGET_IURAN_JAKON_BLN", 0)

bulan_singkat = {
    "Januari":"Jan","Februari":"Feb","Maret":"Mar","April":"Apr",
    "Mei":"Mei","Juni":"Jun","Juli":"Jul","Agustus":"Agu",
    "September":"Sep","Oktober":"Okt","November":"Nov","Desember":"Des"
}
bulan_aktif = bulan_singkat[bulan_nama]

def warna_bar(realisasi, target):
    return ["#E53935" if r < target else "#43A047" for r in realisasi]

fig_iuran = go.Figure()

fig_iuran.add_bar(x=df_iuran["Bulan"], y=df_iuran["PU"], name="PU",
                 marker_color=warna_bar(df_iuran["PU"], df_iuran["T_PU"]))

fig_iuran.add_bar(x=df_iuran["Bulan"], y=df_iuran["BPU"], name="BPU",
                 marker_color=warna_bar(df_iuran["BPU"], df_iuran["T_BPU"]))

fig_iuran.add_bar(x=df_iuran["Bulan"], y=df_iuran["JAKON"], name="Jakon",
                 marker_color=warna_bar(df_iuran["JAKON"], df_iuran["T_JAKON"]))

fig_iuran.add_scatter(x=df_iuran["Bulan"], y=df_iuran["T_PU"],
                     name="Target PU", mode="lines", line=dict(dash="dash"))

fig_iuran.add_scatter(x=df_iuran["Bulan"], y=df_iuran["T_BPU"],
                     name="Target BPU", mode="lines", line=dict(dash="dash"))

fig_iuran.add_scatter(x=df_iuran["Bulan"], y=df_iuran["T_JAKON"],
                     name="Target Jakon", mode="lines", line=dict(dash="dash"))

fig_iuran.add_vline(x=bulan_aktif, line_width=2, line_dash="dot", line_color="blue")

fig_iuran.update_layout(barmode="group", template="plotly_white")

st.plotly_chart(fig_iuran, use_container_width=True)

# =========================
# GRAFIK TK
# =========================
st.markdown("### 👷 Grafik Tenaga Kerja PU, BPU, dan Jasa Konstruksi", unsafe_allow_html=True)

df_tkpu2  = prep_hist(hist_tk_pu, "PU")
df_tkbpu2 = prep_hist(hist_tk_bpu, "BPU")

df_tk = df_tkpu2.merge(df_tkbpu2, on="Bulan", how="outer").fillna(0)

df_tk["T_PU"]  = target.get("TARGET_TK_PU_BLN", 0)
df_tk["T_BPU"] = target.get("TARGET_TK_BPU_BLN", 0)

fig_tk = go.Figure()

fig_tk.add_bar(x=df_tk["Bulan"], y=df_tk["PU"], name="TK PU",
               marker_color=warna_bar(df_tk["PU"], df_tk["T_PU"]))

fig_tk.add_bar(x=df_tk["Bulan"], y=df_tk["BPU"], name="TK BPU",
               marker_color=warna_bar(df_tk["BPU"], df_tk["T_BPU"]))

fig_tk.add_scatter(x=df_tk["Bulan"], y=df_tk["T_PU"],
                   name="Target PU", mode="lines", line=dict(dash="dash"))

fig_tk.add_scatter(x=df_tk["Bulan"], y=df_tk["T_BPU"],
                   name="Target BPU", mode="lines", line=dict(dash="dash"))

fig_tk.add_vline(x=bulan_aktif, line_width=2, line_dash="dot", line_color="blue")

fig_tk.update_layout(barmode="group", template="plotly_white")

st.plotly_chart(fig_tk, use_container_width=True)

# =========================
# TABLE
# =========================
st.markdown("### 📋 Detail Historical Iuran")
st.dataframe(df_iuran, use_container_width=True)

st.markdown("### 📋 Detail Historical Tenaga Kerja")
st.dataframe(df_tk, use_container_width=True)