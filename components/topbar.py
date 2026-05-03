import streamlit as st

def topbar():
    col1, col2, col3, col4 = st.columns([3,1,1,1])

    with col1:
        st.markdown("## Dashboard Kepesertaan KSI")

    tahun = col2.selectbox("Tahun", [2026, 2025])
    cabang = col3.selectbox("Cabang", ["Semua", "Jakarta"])
    periode = col4.selectbox("Periode", ["Mei", "April"])

    return tahun, cabang, periode