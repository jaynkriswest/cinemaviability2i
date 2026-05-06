import streamlit as st
from data import SOUTH_INDIAN_TALENT_DB, GENRE_BASELINES, get_talent_weight
from formula import calculate_v3i_logic

st.set_page_config(page_title="Cinema Predictor v3i", layout="wide")
st.title("🎬 Cinema Predictability AI (v3i)")

# Sidebar for Inputs
with st.sidebar:
    st.header("1. Core Inputs")
    actor = st.selectbox("Lead Actor", list(SOUTH_INDIAN_TALENT_DB.keys()))
    genre = st.selectbox("Genre", list(GENRE_BASELINES.keys()))
    budget = st.slider("Production Budget (Cr)", 5, 500, 50)
    
    st.header("2. Market Factors")
    window = st.selectbox("Release Window", ["Sankranti", "Summer", "Monsoon", "Normal"])
    clash = st.checkbox("Major Superstar Clash?")
    cert = st.selectbox("Certification", ["U", "UA", "A"])
    is_franchise = st.checkbox("IP / Franchise Sequel?")

# Mapping Logic from Document
m_cert = {"U": 1.2, "UA": 1.0, "A": 0.7}[cert]
market_scores = {"Sankranti": 100, "Summer": 90, "Monsoon": 75, "Normal": 70}
s_market = market_scores[window] - (15 if clash else 0)

# Process Results
input_data = {
    "talent_score": get_talent_weight(actor)["score"],
    "market_score": s_market,
    "content_score": GENRE_BASELINES[genre],
    "viral_score": 80,
    "seasonal_score": 85 if window != "Normal" else 70,
    "m_cert": m_cert,
    "m_align": 1.0,
    "budget": budget,
    "is_franchise": is_franchise
}

prob, revenue, roi = calculate_v3i_logic(input_data)

# Main Dashboard Display
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Predictability Score", f"{prob:.1f}%")
with col2:
    st.metric("Budget vs Revenue", f"₹{budget}Cr / ₹{revenue:.1f}Cr")
with col3:
    st.metric("Projected ROI", f"{roi:.1f}%", delta=f"{roi:.1f}%")

st.markdown("---")
st.subheader("Financial Breakdown")
st.write(f"Based on a budget of **₹{budget} Crores**, this project is expected to generate **₹{revenue:.1f} Crores** in theatrical revenue, resulting in a **{roi:.1f}%** return on investment.")