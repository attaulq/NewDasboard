import streamlit as st

def sidebar():
    with st.sidebar:
        st.image("assets/logo.png", width=120)
        st.markdown("### Menu")
        st.page_link("app.py", label="Dashboard")
        st.page_link("pages/1_Dashboard.py", label="Dashboard Utama")