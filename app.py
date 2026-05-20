# New testing, old code added to Main Code

# app.py - new testing version 05202026

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
    page_title="South Indian Cinema Predictor v5",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API KEY SETUP
try:
    OMDB_API_KEY = st.secrets.get("OMDB_API_KEY")
except:
    OMDB_API_KEY = os.getenv("OMDB_API_KEY")

try:
    TMDB_API_KEY = st.secrets.get("TMDB_API_KEY")
except:
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not OMDB_API_KEY:
    st.error("OMDB API Key not found. Add to .env or Streamlit secrets.")
    st.stop()

if not TMDB_API_KEY:
    st.warning("TMDB API Key not found. Systems requiring direct TMDB historical lookup will be restricted.")

# DATA IMPORT
try:
    from data import (
        GENRE_METRICS,
        TALENT_TIERS,
        SOUTH_INDIAN_ACTORS,
        SEASONAL_MULTIPLIERS,
        PRODUCTION_HOUSES
    )
except ImportError:
    st.error("Missing data.py module file in current working directory framework context.")
    st.stop()

try:
    from formula import calculate_v3i_logic, calculate_detailed_prediction
except ImportError:
    st.error("Missing formula.py calculation engine framework matrix configurations.")
    st.stop()

try:
    from movie_insights import (
        search_movies_by_synopsis,
        fetch_full_movie_details,
        calculate_future_likeness,
        classify_movie_success,
        analyze_success_reasons,
        analyze_failure_reasons,
    )
except ImportError:
    st.error("Missing movie_insights.py component structure references.")
    st.stop()

# HEADER UI
st.title("South Indian Cinema Predictability Model v5")
st.markdown("Production-grade ROI prediction engine featuring structural narrative likeness comparisons")
st.divider()

# API FETCH LOGIC
@st.cache_data(ttl=3600)
def fetch_omdb_data(title: str) -> dict:
    try:
        if not OMDB_API_KEY: return None
        url = "https://www.omdbapi.com/"
        params = {"t": title, "type": "movie", "apikey": OMDB_API_KEY}
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data if data.get("Response") == "True" else None
    except Exception as e:
        logger.error(f"OMDb Error: {str(e)}")
        return None

def get_talent_score_from_db(actor_name: str) -> tuple:
    name_normalized = actor_name.lower().replace(" ", "_")
    if name_normalized in SOUTH_INDIAN_ACTORS:
        actor_data = SOUTH_INDIAN_ACTORS[name_normalized]
        return actor_data['score'], actor_data['tier'], True
    return None, None, False

def extract_genre(genre_string: str) -> str:
    if not genre_string: return "Action"
    genres = genre_string.split(",")
    primary_genre = genres.strip()
    return primary_genre if primary_genre in GENRE_METRICS else "Action"

# SIDEBAR CONTROLS
with st.sidebar:
    st.header("Project Configuration")
    
    search_query = st.text_input(
        "Reference Project Lookup",
        value="Pushpa 2",
        help="Query a benchmark project to prepopulate core parameters."
    )
    
    omdb_data = None
    if search_query and st.button("Query API Database Sync", use_container_width=True):
        with st.spinner("Synchronizing reference pools..."):
            omdb_data = fetch_omdb_data(search_query)

    st.divider()
    
    # 1. TALENT PILLAR
    st.subheader("Pillar 1: Talent Metric Profile")
    actor_name = st.text_input("Target Lead Actor", value="Allu Arjun")
    db_score, db_tier, found = get_talent_score_from_db(actor_name)
    
    if found:
        st.success(f"Verified Database Profile: {db_tier}")
        talent_tier = db_tier
        talent_score = db_score
    else:
        st.warning("Talent profile unlisted. Fallback manually.")
        talent_tier = st.selectbox("Assign Actor Tier Profile", ["Ultra-Veteran", "Veteran", "Superstar", "Rising Star"], index=2)
        talent_score = TALENT_TIERS[talent_tier]['score']
        
    st.info(f"**Talent Operational Quotient Score:** {talent_score}/100")
    
    # 2. FINANCIAL / MARKET
    st.subheader("Pillar 2: Market Scale Strategy")
    col_b, col_m = st.columns(2)
    with col_b:
        budget = st.number_input("Budget (INR Crores)", min_value=1.0, max_value=600.0, value=250.0, step=10.0)
    with col_m:
        market_reach = st.selectbox("Distribution Structural Scope", ["Limited (Single State)", "Standard (South India)", "Pan-India", "Global"], index=2)
        
    # Regional Core Language Map for strict semantic targeting
    regional_language = st.selectbox("Primary Language Demographics", ["Telugu", "Tamil", "Malayalam", "Kannada"], index=0)
    lang_code_map = {"Telugu": "te", "Tamil": "ta", "Malayalam": "ml", "Kannada": "kn"}
    selected_lang_code = lang_code_map[regional_language]

    # 3. CONTENT PILLAR & THEMATIC SYNOPSIS
    st.subheader("Pillar 3: Script & Narrative Footprint")
    omdb_genre = extract_genre(omdb_data["Genre"]) if omdb_data and omdb_data.get("Genre") else None
    genre = st.selectbox("Core Genre Baseline Definition", list(GENRE_METRICS.keys()), index=list(GENRE_METRICS.keys()).index(omdb_genre) if omdb_genre else 0)
    
    script_type = st.selectbox("IP Structuring Classification", ["Original", "Remake/Adaptation", "Franchise/Sequel"], index=2)
    is_franchise = (script_type == "Franchise/Sequel")
    
    # NEW INPUT: Future Synopsis Narrative treatment string
    future_synopsis_text = st.text_area(
        "Script Concept Treatment Summary",
        value="A laborer rises through the ranks of an illicit smuggling empire, challenging corrupt cartels and systemic power dynamics to protect his community.",
        help="Paste script treatments here to activate TF-IDF/Cosine textual similarity processing engines."
    )

    # 4. TIMING & MARKET PROFILE
    st.subheader("Pillar 4: Timing & External Modifiers")
    release_date = st.date_input("Target Theater Window Lock", value=date(2026, 12, 25))
    
    month = release_date.month
    seasonal_multiplier = SEASONAL_MULTIPLIERS.get(month, 1.0)
    seasonal_score = min(85 * seasonal_multiplier, 100)
    
    has_clash = st.checkbox("Superstar Holiday Window Collision / Clash?", value=False)
    censor_rating = st.radio("Target Censor Class Metric", ["U", "UA", "A"], index=1)
    m_cert = {"U": 1.2, "UA": 1.0, "A": 0.7}[censor_rating]
    
    viral_hype = st.select_slider("Promotional Visibility Projections", options=["Low", "Moderate", "High"], value="High")
    s_viral = {"Low": 50, "Moderate": 70, "High": 90}[viral_hype]
    
    marketing_alignment = st.slider("Marketing Concept Alignment Core Coefficient", min_value=0.80, max_value=1.0, value=0.95, step=0.05)

# LAYOUT OUTPUT MANAGEMENT
col_main_left, col_main_right = st.columns([1])

with col_main_left:
    st.subheader("Configuration Metric Blueprint")
    if omdb_data:
        st.info("OMDb Context Synced Successfully")
        with st.expander("Reference Metadata Summary"):
            st.write(f"**Synced Identity:** {omdb_data.get('Title')}")
            st.write(f"**Plot Abstract:** {omdb_data.get('Plot')}")
            st.write(f"**IMDb Baseline Rating:** {omdb_data.get('imdbRating')}")
            
    st.markdown("---")
    execute_calculation = st.button("Run Engine Analytics Processing", use_container_width=True, type="primary")

with col_main_right:
    if execute_calculation:
        # Map distribution multipliers
        m_market = {"Limited (Single State)": 0.85, "Standard (South India)": 1.0, "Pan-India": 1.2, "Global": 1.3}[market_reach]
        
        inputs = {
            "talent_score": talent_score,
            "market_base": 85,
            "market_multiplier": m_market,
            "has_clash": has_clash,
            "content_score": GENRE_METRICS[genre]['base_score'],
            "viral_score": s_viral,
            "seasonal_score": seasonal_score,
            "m_cert": m_cert,
            "m_align": marketing_alignment,
            "budget": budget,
            "is_franchise": is_franchise
        }
        
        # Calculate Math Predictions
        prob, revenue, roi = calculate_v3i_logic(inputs)
        detailed = calculate_detailed_prediction(inputs)
        
        # Process NLP Narrative Analysis
        with st.spinner("Running historical plot likeness similarity scans..."):
            historical_comps = search_movies_by_synopsis(
                synopsis=future_synopsis_text,
                genre_name=genre,
                language_code=selected_lang_code,
                tmdb_api_key=TMDB_API_KEY
            )
            
        # Display Core Metrics
        st.subheader("Predictive Risk Intelligence Results")
        m1, m2, m3 = st.columns(3)
        m1.metric("Predictability Index Score", f"{detailed['predictability_score']:.1f}%")
        m2.metric("Projected Gross Revenue", f"₹{detailed['revenue_estimate']:.1f} Cr")
        m3.metric("Projected ROI Base Yield", f"{detailed['roi_percentage']:.1f}%")
        
        st.info(f"**Classification Architecture:** {classify_movie_success(detailed['predictability_score'], detailed['roi_percentage'])}")
        
        # Section Split
        tab_breakdown, tab_scenarios, tab_nlp = st.tabs(["Engine Score Breakdown", "Financial Risk Tiers", "📜 Narrative Likeness Analysis"])
        
        with tab_breakdown:
            b1, b2, b3 = st.columns(3)
            b1.metric("Talent Weight Pillar", f"{detailed['breakdown']['talent']:.0f}/100")
            b2.metric("Market Timing Weight", f"{detailed['breakdown']['market']:.0f}/100")
            b3.metric("Genre Strategy Weight", f"{detailed['breakdown']['content']:.0f}/100")
            
            # Dynamic reasoning feedback blocks
            pos_reasons = analyze_success_reasons(inputs)
            neg_reasons = analyze_failure_reasons(inputs)
            if pos_reasons:
                st.markdown("**Positive Catalysts Identified:**")
                for r in pos_reasons: st.markdown(f"- :green[{r}]")
            if neg_reasons:
                st.markdown("**Structural Risk Impediments Identified:**")
                for r in neg_reasons: st.markdown(f"- :red[{r}]")
                
        with tab_scenarios:
            s1, s2, s3 = st.columns(3)
            s1.metric("Optimistic Scenario Yield", f"{detailed['roi_optimistic']:.1f}%")
            s2.metric("Realistic Expectation Yield", f"{detailed['roi_percentage']:.1f}%")
            s3.metric("Pessimistic Stress Floor", f"{detailed['roi_pessimistic']:.1f}%")
            
        with tab_nlp:
            if not TMDB_API_KEY:
                st.error("TMDB API validation structural context token missing. NLP Similarity Scans unavailable.")
            elif not historical_comps:
                st.warning("No statistically valid historical narrative comps found matching selected parameters.")
            else:
                st.markdown("### Top Identified Historical Narrative Archetypes")
                st.caption("Matches discovered via vector matrix keyword/thematic evaluation scores against localized box office records.")
                st.write("")
                
                for comp in historical_comps:
                    col_card, col_score = st.columns([1])
                    with col_card:
                        st.markdown(f"**{comp['title']} ({comp['release_year']})**")
                        st.markdown(f"<p style='color:#777; font-size:0.92em; font-style:italic;'>Historical Plot Abstract: {comp['historical_overview']}</p>", unsafe_allow_html=True)
                    with col_score:
                        st.metric("Thematic Likeness Match", f"{comp['likeness_score']}%")
                    st.divider()
    else:
        st.info("Execute 'Run Engine Analytics Processing' once variable distributions match project parameters.")

# FOOTER ARCHITECTURE
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85em;">
    <p>Cinema Predictability Framework Model Infrastructure v5 | Dynamic Vector Context Mapping Enabled</p>
    <p>Probabilistic system estimations are strictly calibrated for market environment validation. Total investment protection limits depend entirely on variable validation parity.</p>
</div>
""", unsafe_allow_html=True)