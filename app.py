# Updated from Main folder updated from testing (Claudegem1i)

# app.py - Production Layout and Argument Synchronizer

import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import date
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page config
st.set_page_config(page_title="Cinema Intelligence Platform", layout="wide")

TMDB_API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    st.error("Missing TMDB_API_KEY. Please specify this parameter in your environment config.")
    st.stop()

# Helper function defined BEFORE usage
def search_movies_by_title_raw_internal(title_query):
    try:
        res = requests.get("https://api.themoviedb.org/3/search/movie", 
                           params={"api_key": TMDB_API_KEY, "query": title_query, "region": "IN"}, timeout=5)
        return res.json().get("results", [])[:5]
    except: return []

# DATA MODULE IMPORT CONSTRAINTS
try:
    from data import GENRE_METRICS, SOUTH_INDIAN_ACTORS, DIRECTORS, SEASONAL_MULTIPLIERS
    from formula import calculate_detailed_prediction
    from movie_insights import (
        search_movies_by_synopsis, fetch_full_movie_details,
        analyze_success_reasons, analyze_failure_reasons
    )
except ImportError as e:
    st.error(f"Required structural subsystem reference loading failed: {e}")
    st.stop()

# =====================================================
# DISPLAY MAPPINGS
# =====================================================
ACTOR_DISPLAY_MAP = {"Chirankeevi": "chiranjeevi", "Kamal Haasan": "kamal_haasan", "Rajinikanth": "rajinikanth"}
DIRECTOR_DISPLAY_MAP = {"S.S. Rajamouli": "rajamouli", "Sukumar": "sukumar", "Lokesh Kanagaraj": "lokesh_kanagaraj", "Trivikram Srinivas": "trivikram_srinivas"}
GENRE_DISPLAY_MAP = {"Action": "Action", "Drama": "Drama", "Thriller": "Thriller", "Comedy": "Comedy", "Romance": "Romance"}

# =====================================================
# LAYOUT STRUCTURE
# =====================================================
st.title("South Indian Cinema Predictability Model v5")
st.divider()

prediction_col, search_col = st.columns([1.2, 1])

# =====================================================
# LEFT PANEL: PREDICTABILITY ENGINE
# =====================================================
with prediction_col:
    st.header("Predictability Model Engine")
    actor_label = st.selectbox("Lead Actor Profile", options=list(ACTOR_DISPLAY_MAP.keys()))
    director_label = st.selectbox("Director Profile", options=list(DIRECTOR_DISPLAY_MAP.keys()))
    genre_label = st.selectbox("Primary Genre Definition", options=list(GENRE_DISPLAY_MAP.keys()))
    budget = st.number_input("Budget Exposure Ceiling (INR Crores)", min_value=1.0, value=150.0)
    future_synopsis_text = st.text_area("Future Script Synopsis", value="A dynamic protagonist works within an underground network...")

    if st.button("Run Analytics Engine Pipeline", type="primary", use_container_width=True):
        inputs = {
            "talent_score": (SOUTH_INDIAN_ACTORS[ACTOR_DISPLAY_MAP[actor_label]]["score"] * 0.6) + (DIRECTORS[DIRECTOR_DISPLAY_MAP[director_label]]["score"] * 0.4),
            "content_score": GENRE_METRICS[GENRE_DISPLAY_MAP[genre_label]]["base_score"],
            "budget": budget
        }
        pred = calculate_detailed_prediction(inputs)
        
        st.subheader("Engine Valuation Metrics")
        m1, m2, m3 = st.columns(3)
        m1.metric("Predictability", f"{pred['predictability_score']:.1f}%")
        m2.metric("Gross Revenue", f"₹{pred['revenue_estimate']:.1f} Cr")
        m3.metric("ROI Yield", f"{pred['roi_percentage']:.1f}%")
        
        t1, t2, t3 = st.tabs(["Pillar Weights", "Strategic Log", "Narrative Likeness"])
        with t1:
            st.write(f"Talent Assessment: {pred['breakdown']['talent']:.1f}/100")
        with t2:
            for r in analyze_success_reasons(inputs): st.write(f"✅ {r}")
        with t3:
            for comp in search_movies_by_synopsis(future_synopsis_text, TMDB_API_KEY):
                st.write(f"• {comp['title']} ({comp['release_year']}) - Likeness: {comp['likeness_score']}%")

# =====================================================
# RIGHT PANEL: TITLE SEARCH ENGINE
# =====================================================
with search_col:
    st.header("Historical Narrative Benchmarking")
    query = st.text_input("Search Regional Reference Title", key="right_panel_title_query")
    if query:
        historical_pool = search_movies_by_title_raw_internal(query)
        if historical_pool:
            options = {f"{m['title']} ({m.get('release_date', '####')[:4]})": m['id'] for m in historical_pool}
            selected_label = st.selectbox("Resolve Match", options=list(options.keys()))
            if selected_label:
                details = fetch_full_movie_details(options[selected_label], TMDB_API_KEY)
                if details:
                    # FIXED: Added weights to prevent TypeError
                    card_left, card_right = st.columns()
                    with card_left:
                        if details.get("poster_path"):
                            st.image(f"https://image.tmdb.org/t/p/w500{details['poster_path']}", use_container_width=True)
                    with card_right:
                        st.subheader(details.get("title"))
                        st.write(f"**Cast:** {details.get('extracted_cast', 'N/A')}")
                    st.write(details.get("overview", "No plot summary."))
                    st.subheader("Similar Historical Films")
                    for rec in details.get("extracted_recommendations", []):
                        st.markdown(f"• {rec.get('title')}")

# Footer
st.divider()
st.markdown("<div style='text-align: center; color: #666;'>Cinema Predictability Model v5</div>", unsafe_allow_html=True)