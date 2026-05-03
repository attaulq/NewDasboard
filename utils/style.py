import streamlit as st

def apply_sidebar_style():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #0B3C6F !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFD700 !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #4A90E2 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)