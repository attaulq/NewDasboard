import streamlit as st

def kpi_card(title, value, gap, progress=0, status=""):

    gap = gap or 0

    if gap >= 0:
        gap_class = "gap-green"
        icon = "⬆️"
    else:
        gap_class = "gap-red"
        icon = "⬇️"

    st.markdown(f"""
    <div class="card-kpi">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
        <div class="{gap_class}">
            GAP: {gap:,.0f} {icon}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(min(progress, 1.0))
    st.caption(status)