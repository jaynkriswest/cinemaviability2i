import streamlit as st
from data import SOUTH_INDIAN_TALENT_DB, GENRE_BASELINES
from formula import calculate_v3i_logic

st.title("Cinema Predictor v3i")

with st.sidebar:
    actor_name = st.selectbox("Lead Actor", list(SOUTH_INDIAN_TALENT_DB.keys()))
    genre = st.selectbox("Genre", list(GENRE_BASELINES.keys()))
    budget = st.slider("Budget (Crores)", 10, 500, 100)
    window = st.selectbox("Window", ["Sankranti", "Summer", "Monsoon", "Normal"])
    cert = st.selectbox("Cert", ["U", "UA", "A"])
    is_franchise = st.checkbox("Is Franchise?")

# Input Mapping
actor_data = SOUTH_INDIAN_TALENT_DB[actor_name]
m_cert = {"U": 1.2, "UA": 1.0, "A": 0.7}[cert]
s_market = {"Sankranti": 100, "Summer": 90, "Monsoon": 75, "Normal": 70}[window]

inputs = {
    "talent_score": actor_data['score'],
    "market_score": s_market,
    "content_score": GENRE_BASELINES[genre],
    "viral_score": 80,
    "seasonal_score": 85,
    "m_cert": m_cert,
    "m_align": 1.0,
    "budget": budget,
    "is_franchise": is_franchise
}

prob, rev, roi = calculate_v3i_logic(inputs)

# Visualization
st.metric("Probability", f"{prob:.1f}%")
st.metric("Estimated Revenue", f"₹{rev:.1f} Cr")
st.metric("ROI", f"{roi:.1f}%")

if roi < 0:
    st.error("HIGH RISK: Budget exceeds talent-market reach.")
else:
    st.success("VIABLE: Talent and budget are in alignment.")