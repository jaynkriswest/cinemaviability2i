import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import date
from data import GENRE_METRICS
from formula import calculate_v3i_logic

# 1. SETUP & SECURITY
# Loads local .env for local testing; Streamlit Cloud will use its own Secrets
load_dotenv()

# Attempt to get keys from Streamlit Secrets (Production) or .env (Local)
OMDB_API_KEY = st.secrets.get("OMDB_API_KEY") or os.getenv("OMDB_API_KEY")
TMDB_API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

st.set_page_config(page_title="v3i Real-Time Predictor", layout="wide")
st.title("🎬 South Indian Cinema Predictability Model v3i")

# 2. DATA FETCHING FUNCTION
def fetch_movie_metadata(title):
    if not OMDB_API_KEY or not TMDB_API_KEY:
        st.error("API Keys missing. Please check your .env or Streamlit Secrets.")
        return None
    
    # Fetch from OMDb
    omdb_res = requests.get(f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}").json()
    
    # Fetch from TMDB for Credits & Budget
    tmdb_search = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}").json()
    
    tmdb_details = {}
    if tmdb_search.get('results'):
        movie_id = tmdb_search['results']['id']
        tmdb_details = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits").json()
    
    return omdb_res, tmdb_details

# 3. SIDEBAR INPUTS
with st.sidebar:
    st.header("🔍 Real-Time Search")
    search_query = st.text_input("Enter Movie Title", value="Mana Shankara Varaprasad Garu")
    
    omdb, tmdb = None, None
    if search_query:
        omdb, tmdb = fetch_movie_metadata(search_query)

    st.divider()
    
    if omdb and omdb.get("Response") == "True":
        st.success(f"Linked to: {omdb['Title']}")
        # Auto-map M_Cert from OMDB
        cert_val = omdb.get("Rated", "UA")
        m_cert = {"U": 1.2, "UA": 1.0, "U/A": 1.0, "A": 0.7}.get(cert_val, 1.0)
        
        # Auto-map Genre
        fetched_genre = omdb.get("Genre", "Mass Action").split(",")
        genre = fetched_genre if fetched_genre in GENRE_METRICS else "Mass Action"
        
        # Auto-map Budget (Convert to Crores)
        tmdb_budget = tmdb.get("budget", 0) / 10000000 
        budget = st.number_input("Budget (Crores)", value=float(tmdb_budget) if tmdb_budget > 0 else 200.0)
    else:
        st.warning("Manual fallback active.")
        m_cert = 1.0
        genre = "Mass Action"
        budget = st.number_input("Budget (Crores)", value=200.0)

    st.header("Pillar 1: Talent")
    talent_tier = st.selectbox("Assign Talent Tier", ["Ultra-Veteran", "Veteran", "Superstar", "Rising Star"])
    talent_map = {"Ultra-Veteran": 98, "Veteran": 90, "Superstar": 92, "Rising Star": 70}
    
    st.header("Pillar 2 & 4: Market & Viral")
    release_date = st.date_input("Release Date", value=date(2026, 1, 12))
    has_clash = st.checkbox("Major Superstar Clash?")
    viral_tier = st.select_slider("Viral Hype", options=["Low", "Moderate", "High"], value="Moderate")
    viral_map = {"Low": 40, "Moderate": 70, "High": 95}

# 4. LOGIC PROCESSING
# Calculate Market Multiplier
m_market = 1.0
if release_date.month == 1 and 12 <= release_date.day <= 17:
    m_market = 1.3 # Sankranti
elif 4 <= release_date.month <= 6:
    m_market = 1.15 # Summer

inputs = {
    "talent_score": talent_map[talent_tier],
    "market_base": 85,
    "market_multiplier": m_market,
    "has_clash": has_clash,
    "content_score": GENRE_METRICS[genre]['base_score'],
    "viral_score": viral_map[viral_tier],
    "seasonal_score": 85 if m_market > 1.0 else 70,
    "m_cert": m_cert,
    "m_align": 1.0,
    "budget": budget,
    "is_franchise": False # Could be automated by checking if title has digits
}

# Execute Formula
prob, revenue, roi = calculate_v3i_logic(inputs)

# 5. UI DISPLAY
col1, col2, col3 = st.columns(3)
with col1: st.metric("Predictability Score", f"{prob:.1f}%")
with col2: st.metric("Est. Gross Revenue", f"₹{revenue:.1f} Cr")
with col3: st.metric("Projected ROI", f"{roi:.1f}%")

if omdb:
    st.divider()
    st.subheader("Technical Analysis Data (IMDb)")
    st.write(f"**Synopsis:** {omdb.get('Plot')}")
    st.write(f"**Cast:** {omdb.get('Actors')}")
    st.write(f"**Genre:** {omdb.get('Genre')} | **Certification:** {omdb.get('Rated')}")