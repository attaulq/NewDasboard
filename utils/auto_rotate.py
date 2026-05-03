from streamlit_autorefresh import st_autorefresh
import streamlit as st
import time

pages = [
    "1_Dashboard",
    "2_Tenaga_Kerja",
    "3_Perusahaan",
    "4_AR_AGUNG",
    "5_AR_AGUNG_DETIL",
    "6_AR_ATTA_UL_Q",
    "7_AR_ATTA_UL_Q_DETIL",
    "8_AR_BAYU",
    "9_AR_BAYU_DETIL",
    "10_AR_IRAWAN",
    "11_AR_IRAWAN_DETIL",
    "12_AR_DHIKA",
    "13_AR_DHIKA_DETIL",
    "14_ARK_ABHIMATA",
    "15_ARK_ABHIMATA_DETIL",
    "16_ARK_ANNA",
    "17_ARK_ANNA_DETIL",
    "18_ARK_FRANS",
    "19_ARK_FRANS_DETIL",
    "20_ARK_IQBAL",
    "21_ARK_IQBAL_DETIL",
    "22_ARK_JEFRY",
    "23_ARK_JEFRY_DETIL",
    "24_ARK_TIO",
    "25_ARK_TIO_DETIL",
    "26_ARK_WYANDRA",
    "27_ARK_WYANDRA_DETIL",
    "28_ARK_AJI"
    "29_ARK_AJI_DETIL"
    "30_Motivasi"
]


def run_auto_rotate():

    # 🔥 WAJIB → trigger rerun tiap 1 detik
    st_autorefresh(interval=1000, key="auto_refresh")

    if "idx" not in st.session_state:
        st.session_state.idx = 0

    if "last_switch" not in st.session_state:
        st.session_state.last_switch = time.time()

    if not st.session_state.get("auto_rotate", False):
        return

    now = time.time()

    if now - st.session_state.last_switch >= st.session_state.get("rotate_seconds", 6):
        st.session_state.idx = (st.session_state.idx + 1) % len(pages)
        st.session_state.last_switch = now

        next_page = pages[st.session_state.idx]
        st.switch_page(f"pages/{next_page}.py")
