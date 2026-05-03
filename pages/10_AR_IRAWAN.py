import streamlit as st
import pandas as pd
import sqlite3
import os

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

#from utils.auto_rotate import run_auto_rotate
#run_auto_rotate()

conn = sqlite3.connect("database.db", check_same_thread=False)

KODE_NIK = "IR166170"
NAMA_AR = "IRAWAN ALVIANTO"

# =========================
# LOAD CSS (reuse style.css)
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
css_path = os.path.join(BASE_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================
# HEADER BAR (logo + title + filter)
# =========================
assets_path = os.path.join(BASE_DIR, "assets")
logo_file = None
for f in os.listdir(assets_path):
    if "logo" in f.lower():
        logo_file = f
        break
logo_path = os.path.join(assets_path, logo_file) if logo_file else None

h1, h2, h3, h4 = st.columns([0.1, 14, 4.5, 2.5])

with h3:
    if logo_path:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.image(logo_path, width=400)

with h2:
    st.write("")
    st.write("")
    st.markdown("# **Dashboard AR Performance**")
    st.caption("### **Monitoring Progress Iuran & Tenaga Kerja**")

st.markdown("""
<div style="margin-top:40px; padding-top:5px;">
</div>
""", unsafe_allow_html=True)

# =========================
# AUTO DATE (FIX ONLY THIS)
# =========================
from datetime import datetime

today = datetime.today()

tahun_default = today.year
bulan_default = today.month
tanggal = today.day
minggu_default = min((tanggal - 1) // 7 + 1, 4)

# =========================
# BULAN MAP
# =========================
bulan_map = {
    "Januari":1,"Februari":2,"Maret":3,"April":4,
    "Mei":5,"Juni":6,"Juli":7,"Agustus":8,
    "September":9,"Oktober":10,"November":11,"Desember":12
}

# =========================
# FILTER
# =========================
col1, col2, col3 = st.columns(3)

tahun = col1.selectbox("Tahun", [2026], index=0)

bulan_list = list(bulan_map.keys())
bulan_index = list(bulan_map.values()).index(bulan_default)

bulan_nama = col2.selectbox("Bulan", bulan_list, index=bulan_index)
bulan = bulan_map[bulan_nama]

minggu = col3.selectbox("Minggu", [1,2,3,4], index=minggu_default-1)

# =========================
# INFO PERIODE
# =========================
st.caption(f"Periode otomatis: {bulan_nama} {tahun} • Minggu {minggu}")

# =========================
# (SISA FILE ASLI KAMU — TIDAK DIUBAH)
# =========================

def get_val(q):
    df = pd.read_sql(q, conn)
    if df.empty:
        return 0
    v = df.iloc[0][0]
    return v or 0

def target_kumulatif(target_bln, minggu):
    return (target_bln or 0) * minggu

def progress(val, tgt):
    return (val / tgt) if tgt else 0

def status(p):
    if p >= 1:
        return "🟢 On Track"
    elif p >= 0.8:
        return "🟡 Warning"
    else:
        return "🔴 Risk"

def kpi_card(title, value, gap, prog, status_txt):
    gap_class = "gap-red" if gap < 0 else "gap-green"
    arrow = "⬇️" if gap < 0 else "⬆️"
    st.markdown(f"""
        <div class="card-kpi">
            <div class="card-title">{title}</div>
            <div class="card-value">{value}</div>
            <div class="{gap_class}">GAP: {gap:,.0f} {arrow}</div>
        </div>
    """, unsafe_allow_html=True)
    st.progress(min(prog, 1.0))
    st.caption(status_txt)

def gap_color(val):
    return "🟢" if val >= 0 else "🔴"

# =========================
# GET DATA KARYAWAN
# =========================
df_karyawan = pd.read_sql(f"""
SELECT NAMA_AR, JABATAN
FROM DATA_KARYAWAN
WHERE KODE_NIK = '{KODE_NIK}'
LIMIT 1
""", conn)

# =========================
# DATA TARGET AR
# =========================
df_target = pd.read_sql(f"""
SELECT *
FROM DATA_TARGET_SETUP_AR
WHERE KODE_NIK = '{KODE_NIK}'
LIMIT 1
""", conn)

target = df_target.iloc[0].to_dict() if not df_target.empty else {}

# =========================
# DATA REALISASI
# =========================
iuran_pu = get_val(f"""
SELECT SUM(TOTAL_IURAN)
FROM "DATA_MONITORING_PERUSAHAAN"
WHERE KODE_NIK='{KODE_NIK}' AND BLN={bulan} AND TAHUN={tahun}
""")

iuran_bpu = get_val(f"""
SELECT SUM(TOTAL_IURAN)
FROM DATA_MONITORING_IURAN_PU_BARU
WHERE KODE_NIK='{KODE_NIK}' AND BLN={bulan} AND TAHUN={tahun}
""")

iuran_jakon = get_val(f"""
SELECT SUM(TOTAL_IURAN)
FROM DATA_IURAN_JAKON_HISTORY
WHERE KODE_NIK='{KODE_NIK}' AND BLN={bulan} AND TAHUN={tahun}
""")

tk_pu = get_val(f"""
SELECT SUM(TK_AKTIF)
FROM "DATA_MONITORING_PERUSAHAAN"
WHERE KODE_NIK='{KODE_NIK}' AND BLN={bulan} AND TAHUN={tahun}
""")

tk_bpu = get_val(f"""
SELECT SUM(TOTAL_TK_BPU)
FROM DATA_TK_BPU_HISTORY
WHERE KODE_NIK='{KODE_NIK}' AND BLN={bulan} AND TAHUN={tahun}
""")

tk_jakon = get_val(f"""
SELECT SUM(TOTAL_TK_JAKON)
FROM DATA_TK_JAKON_HISTORY
WHERE KODE_NIK='{KODE_NIK}' AND BLN={bulan} AND TAHUN={tahun}
""")

prs_pu = get_val(f"""
SELECT COUNT(NPP)
FROM "DATA_MONITORING_PERUSAHAAN"
WHERE (BLTH_NA IS NULL OR BLTH_NA='') AND KODE_NIK='{KODE_NIK}'
AND BLN={bulan} AND TAHUN={tahun}
""")

prs_bpu = get_val(f"""
SELECT SUM(TOTAL_PRS_BPU)
FROM DATA_TK_BPU_HISTORY
WHERE KODE_NIK='{KODE_NIK}' AND BLN={bulan} AND TAHUN={tahun}
""")

# =========================
# TARGET KUMULATIF
# =========================
t_pu = target_kumulatif(target.get("TARGET_IURAN_PU_BLN", 0), minggu)
t_bpu = target_kumulatif(target.get("TARGET_IURAN_BPU_BLN", 0), minggu)
t_jakon = target_kumulatif(target.get("TARGET_IURAN_JAKON_BLN", 0), minggu)

t_tk_pu = target_kumulatif(target.get("TARGET_TK_PU_BLN", 0), minggu)
t_tk_bpu = target_kumulatif(target.get("TARGET_TK_BPU_BLN", 0), minggu)
t_tk_jakon = target_kumulatif(target.get("TARGET_TK_JAKON_BLN", 0), minggu)

t_prs_pu = target_kumulatif(target.get("TARGET_PRS_PU_BLN", 0), minggu)
t_prs_bpu = target_kumulatif(target.get("TARGET_PRS_BPU_BLN", 0), minggu)

# =========================
# PROGRESS & GAP
# =========================
p_pu = progress(iuran_pu, t_pu)
p_bpu = progress(iuran_bpu, t_bpu)
p_jakon = progress(iuran_jakon, t_jakon)

g_pu = iuran_pu - t_pu
g_bpu = iuran_bpu - t_bpu
g_jakon = iuran_jakon - t_jakon

g_tk_pu = tk_pu - t_tk_pu
g_tk_bpu = tk_bpu - t_tk_bpu
g_tk_jakon = tk_jakon - t_tk_jakon

g_prs_pu = prs_pu - t_prs_pu
g_prs_bpu = (prs_bpu or 0) - t_prs_bpu

if df_karyawan.empty:
    nama_ar = NAMA_AR
    jabatan = "Account Representative"
else:
    nama_ar = df_karyawan.iloc[0]["NAMA_AR"]
    jabatan = df_karyawan.iloc[0]["JABATAN"] or "Account Representative"

# =========================
# UI (ASLI TIDAK DIUBAH)
# =========================
st.markdown("## ")

left, right = st.columns([3, 10])

with left:
    st.markdown(f"""
    <div style="font-size:28px;font-weight:700;margin-bottom:10px;">
        {nama_ar}
    </div>
    <div style="color:#6B7280;margin-bottom:10px;">
        {jabatan}
    </div>
    """, unsafe_allow_html=True)

    foto_path = os.path.join(assets_path, "166171591-irawan.jpg")
    if os.path.exists(foto_path):
        st.image(foto_path, width=340)
    else:
        st.image("https://via.placeholder.com/340", width=340)

    avg_p = (p_pu + p_bpu + p_jakon) / 3 if (t_pu + t_bpu + t_jakon) else 0

    st.markdown(f"<b>Status:</b> {status(avg_p)}", unsafe_allow_html=True)
    st.caption(f"Periode: {bulan_nama} {tahun} • Minggu {minggu}")

with right:
    st.markdown('<div class="section-title">💰 Iuran</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Iuran PU", f"Rp {iuran_pu:,.0f}", g_pu, p_pu, status(p_pu))
    with c2:
        kpi_card("Iuran BPU", f"Rp {iuran_bpu:,.0f}", g_bpu, p_bpu, status(p_bpu))
    with c3:
        kpi_card("Iuran Jakon", f"Rp {iuran_jakon:,.0f}", g_jakon, p_jakon, status(p_jakon))

    st.markdown('<div class="section-title">👷 Tenaga Kerja & Perusahaan</div>', unsafe_allow_html=True)

    k1, k2, k3 = st.columns(3)
    k1.metric("TK PU", f"{int(tk_pu):,}")
    k1.caption(f"GAP: {g_tk_pu:,}")

    k2.metric("TK BPU", f"{int(tk_bpu):,}")
    k2.caption(f"GAP: {g_tk_bpu:,}")

    k3.metric("TK Jakon", f"{int(tk_jakon):,}")
    k3.caption(f"GAP: {g_tk_jakon:,}")

    p1, p2 = st.columns(2)
    p1.metric("Perusahaan PU", f"{int(prs_pu):,}")
    p1.caption(f"GAP: {g_prs_pu:,}")

    p2.metric("Perusahaan BPU", f"{int(prs_bpu or 0):,}")
    p2.caption(f"GAP: {g_prs_bpu:,}")

# =========================
# PROGRESS SUMMARY
# =========================
st.markdown('<div class="section-title">📊 Progress Summary</div>', unsafe_allow_html=True)

ps1, ps2, ps3 = st.columns(3)
ps1.write(f"PU : {p_pu*100:.1f}%  {status(p_pu)}")
ps2.write(f"BPU: {p_bpu*100:.1f}%  {status(p_bpu)}")
ps3.write(f"Jakon: {p_jakon*100:.1f}%  {status(p_jakon)}")

# =========================
# FOOTER
# =========================
st.caption("Update: data sesuai filter bulan & minggu berjalan")
