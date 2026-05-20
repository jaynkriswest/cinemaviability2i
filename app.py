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
st.set_page_config(
    page_title="Cinema Intelligence Platform",
    layout="wide"
)

TMDB_API_KEY = (
    st.secrets.get("TMDB_API_KEY")
    or os.getenv("TMDB_API_KEY")
)

if not TMDB_API_KEY:
    st.error("Missing TMDB_API_KEY. Please specify this parameter in your environment config.")
    st.stop()

# DATA MODULE IMPORT CONSTRAINTS
try:
    from data import (
        GENRE_METRICS,
        SOUTH_INDIAN_ACTORS,
        DIRECTORS,
        SEASONAL_MULTIPLIERS,
    )
    from formula import calculate_detailed_prediction
    from movie_insights import (
        search_movies_by_synopsis,
        fetch_full_movie_details,
        classify_movie_success,
        analyze_success_reasons,
        analyze_failure_reasons,
    )
except ImportError as e:
    st.error(f"Required structural subsystem reference loading failed: {e}")
    st.stop()

# =====================================================
# DISPLAY MAPPING COMPILATIONS
# =====================================================

ACTOR_DISPLAY_MAP = {
    "Chirankeevi": "chiranjeevi",
    "Kamal Haasan": "kamal_haasan",
    "Rajinikanth": "rajinikanth",
}

DIRECTOR_DISPLAY_MAP = {
    "S.S. Rajamouli": "rajamouli",
    "Sukumar": "sukumar",
    "Lokesh Kanagaraj": "lokesh_kanagaraj",
    "Trivikram Srinivas": "trivikram_srinivas",
}

GENRE_DISPLAY_MAP = {
    "Action": "Action",
    "Drama": "Drama",
    "Thriller": "Thriller",
    "Comedy": "Comedy",
    "Romance": "Romance",
}

# =====================================================
# LAYOUT STRUCTURE RATIO DEFINITION (Side-By-Side Split)
# =====================================================

st.title("South Indian Cinema Predictability Model v5")
st.markdown("Production-grade ROI prediction engine featuring structural narrative likeness comparisons")
st.divider()

prediction_col, search_col = st.columns([1.2, 1])

# =====================================================
# LEFT PANEL: PREDICTABILITY ENGINE INPUTS & PILLARS
# =====================================================

with prediction_col:
    st.header("Predictability Model Engine")
    
    actor_label = st.selectbox("Lead Actor Profile", options=list(ACTOR_DISPLAY_MAP.keys()))
    director_label = st.selectbox("Director Profile", options=list(DIRECTOR_DISPLAY_MAP.keys()))
    genre_label = st.selectbox("Primary Genre Definition", options=list(GENRE_DISPLAY_MAP.keys()))
    
    budget = st.number_input("Budget Exposure Ceiling (INR Crores)", min_value=1.0, max_value=600.0, value=150.0, step=10.0)
    release_date = st.date_input("Target Release Schedule Date", value=date(2026, 1, 1))
    
    has_clash = st.checkbox("Holiday Release Clashes / Competition Constraints")
    is_franchise = st.checkbox("Franchise / IP Sequel Capitalization Model")
    
    censor_rating = st.radio("Censor Allocation Multiplier Status", options=["U", "UA", "A"], index=1)
    viral_hype = st.select_slider("Promotional Viral Traction Track", options=["Low", "Moderate", "High"], value="Moderate")
    marketing_alignment = st.slider("Marketing Messaging Core Consistency Floor", min_value=0.8, max_value=1.0, value=0.95, step=0.01)

    future_synopsis_text = st.text_area(
        "Future Script Synopsis/Treatment (For Similarity Processing)",
        value="A dynamic protagonist works within an underground network, taking on powerful elements to restore equilibrium and rescue hostages."
    )

    if st.button("Run Analytics Engine Pipeline", type="primary", use_container_width=True):
        actor_key = ACTOR_DISPLAY_MAP[actor_label]
        director_key = DIRECTOR_DISPLAY_MAP[director_label]
        genre_key = GENRE_DISPLAY_MAP[genre_label]
        
        actor_score = SOUTH_INDIAN_ACTORS[actor_key]["score"]
        director_score = DIRECTORS[director_key]["score"]
        
        talent_score = (actor_score * 0.6) + (director_score * 0.4)
        content_score = GENRE_METRICS[genre_key]["base_score"]
        
        month = release_date.month
        seasonal_score = min(85 * SEASONAL_MULTIPLIERS.get(month, 1.0), 100)
        viral_score = {"Low": 50, "Moderate": 70, "High": 90}[viral_hype]
        m_cert = {"U": 1.2, "UA": 1.0, "A": 0.7}[censor_rating]
        
        inputs = {
            "talent_score": talent_score, "market_base": 85, "market_multiplier": 1.0,
            "has_clash": has_clash, "content_score": content_score, "viral_score": viral_score,
            "seasonal_score": seasonal_score, "m_cert": m_cert, "m_align": marketing_alignment,
            "budget": budget, "is_franchise": is_franchise
        }
        
        pred = calculate_detailed_prediction(inputs)
        
        st.divider()
        st.subheader("Engine Valuation Metrics Output")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Predictability Score Index", f"{pred['predictability_score']:.1f}%")
        m2.metric("Gross Revenue Projection", f"₹{pred['revenue_estimate']:.1f} Cr")
        m3.metric("Expected Investment Yield ROI", f"{pred['roi_percentage']:.1f}%")
        
        st.info(f"**Engine Framework Risk Assessment:** {pred['risk_level']}")
        
        t1, t2, t3 = st.tabs(["Pillar Weight Details", "Strategic Guidance Log", "📜 Narrative Likeness Analysis"])
        
        with t1:
            st.write(f"• Talent Profile Assessment Anchor: {pred['breakdown']['talent']:.1f}/100")
            st.write(f"• Market Distribution Strategy Track: {pred['breakdown']['market']:.1f}/100")
            st.write(f"• Script/Genre Content Structural Weight: {pred['breakdown']['content']:.1f}/100")
            
        with t2:
            suc_reasons = analyze_success_reasons(inputs)
            fail_reasons = analyze_failure_reasons(inputs)
            if suc_reasons:
                st.markdown("**Positive Predictive Multipliers:**")
                for r in suc_reasons: st.write(f"✅ {r}")
            if fail_reasons:
                st.markdown("**Structural Financial Constraints:**")
                for r in fail_reasons: st.write(f"⚠️ {r}")

        with t3:
            with st.spinner("Processing narrative likeness vector matching lists..."):
                historical_comps = search_movies_by_synopsis(future_synopsis_text, TMDB_API_KEY)
            
            if not historical_comps:
                st.warning("No statistically valid structural comps found for text input.")
            else:
                st.markdown("### Top Identified Narrative Archetypes")
                for comp in historical_comps:
                    st.markdown(f"**{comp.get('title')} ({comp.get('release_year')})**")
                    st.caption(f"Historical Narrative Plot Context: {comp.get('overview')}")
                    st.write(f"**Thematic Likeness Score:** {comp.get('likeness_score')}%")
                    st.divider()

# =====================================================
# RIGHT PANEL: TITLE SEARCH ENGINE & HISTORICAL LOOKUPS
# =====================================================

with search_col:
    st.header("Historical Narrative Benchmarking")
    
    query = st.text_input(
        "Search Regional Reference Title",
        placeholder="Enter film title (e.g., Apex, Pushpa, Vikram)...",
        key="right_panel_title_query"
    )
    
    def search_movies_by_title_raw(title_query):
        url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": TMDB_API_KEY, "query": title_query, "region": "IN"}
        try:
            res = requests.get(url, params=params, timeout=5)
            return res.json().get("results", [])[:5]
        except Exception:
            return []

    movie_data = None
    if query:
        with st.spinner("Searching title database records..."):
            historical_pool = search_movies_by_title_raw(query)
            
            if historical_pool:
                # Map selection criteria straight to primary structural IDs to prevent naming collisions
                options = {}
                for m in historical_pool:
                    t_str = m.get('title', 'Unknown Title')
                    y_str = m.get('release_date', '####')[:4]
                    m_id = m.get('id')
                    if m_id:
                        options[f"{t_str} ({y_str})"] = m_id
                        
                selected_label = st.selectbox(
                    "Resolve Target Entity Identity Match",
                    options=list(options.keys()),
                    key="right_panel_selector_dropdown"
                )
                if selected_label:
                    target_id = options[selected_label]
                    
                    with st.spinner("Loading complete production indexes..."):
                        movie_details = fetch_full_movie_details(target_id, TMDB_API_KEY)
                        
                    if movie_details:
                        poster_path = movie_details.get("poster_path")
                        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                        genres = [g.get("name") for g in movie_details.get("genres", [])]
                        
                        movie_data = {
                            "title": movie_details.get("title"),
                            "year": movie_details.get("release_date", "####")[:4],
                            "genre": ", ".join(genres) if genres else "N/A",
                            "actors": movie_details.get("extracted_cast", "N/A"),
                            "plot": movie_details.get("overview") or "No textual summary cataloged.",
                            "poster": poster_url,
                            "recommendations": movie_details.get("extracted_recommendations", [])
                        }
            else:
                st.warning("No historical films indexed with that exact title string.")

    # RENDER ENGINE PROFILE CARD
    if movie_data:
        st.write("") # Margin spacer
        card_left, card_right = st.columns()
        
        with card_left:
            if movie_data["poster"]:
                st.image(movie_data["poster"], use_container_width=True)
            else:
                st.markdown(
                    "<div style='border:1px dashed #444; height:240px; display:flex; "
                    "align-items:center; justify-content:center; border-radius:6px; color:#666;'>"
                    "No Poster Found</div>", unsafe_allow_html=True
                )
                
        with card_right:
            st.subheader(f"{movie_data['title']} ({movie_data['year']})")
            st.markdown(f"**Genre:** {movie_data['genre']}")
            st.markdown(f"**Cast:** {movie_data['actors']}")
        
        # Clear normal paragraph formatting style for synopsis text block (Removes blue tint box)
        st.write("")
        st.write(movie_data["plot"])

        # STYLED NATIVE RECOMMENDATIONS LISTS
        st.write("")
        st.subheader("Similar Historical Films")

        if movie_data["recommendations"]:
            for movie in movie_data["recommendations"]:
                st.markdown(f"• {movie.get('title')}")
        else:
            st.info("No matching cross-references indexed for this specific feature set.")

# =====================================================
# FOOTER ARCHITECTURE
# =====================================================
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85em;">
    <p>Cinema Predictability Model v5 | Powered by OMDB/TMDB APIs & Curated South Indian Database</p>
    <p>Predictions are probabilistic estimates based on historical patterns. No model perfectly predicts creative industries.</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# FOOTER
# =====================================================

st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85em;">
    <p>Cinema Predictability Model v5 | Powered by OMDB/TMDB APIs & Curated South Indian Database</p>
    <p>Predictions are probabilistic estimates based on historical patterns. No model perfectly predicts creative industries.</p>
</div>
""", unsafe_allow_html=True)