#Clde version updates with gemini + CGPT

# app.py - Corrected Version

import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import date
import logging

# Import local modules
from data import (
    GENRE_METRICS,
    SOUTH_INDIAN_ACTORS,
    DIRECTORS,
    SEASONAL_MULTIPLIERS,
)

from formula import (
    calculate_v3i_logic,
    calculate_detailed_prediction,
)

# =====================================================
# SETUP & CONFIGURATION
# =====================================================

load_dotenv()

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="v3i Cinema Predictor",
    layout="wide"
)

# =====================================================
# API KEYS
# =====================================================

OMDB_API_KEY = st.secrets.get("OMDB_API_KEY") or os.getenv("OMDB_API_KEY")
TMDB_API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

# =====================================================
# VALIDATION
# =====================================================

if not OMDB_API_KEY:
    st.error("Missing OMDB_API_KEY in Streamlit secrets.")
    st.stop()

if not TMDB_API_KEY:
    st.error("Missing TMDB_API_KEY in Streamlit secrets.")
    st.stop()

# =====================================================
# DATA FETCHING FUNCTIONS
# =====================================================

def search_movies_list(query):
    """
    Search OMDB for movies matching a query.
    """

    url = f"http://www.omdbapi.com/?s={query}&apikey={OMDB_API_KEY}"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        data = response.json()

        if data.get("Response") == "True":
            return data.get("Search", [])

        return []

    except Exception as e:
        st.error(f"OMDB search error: {e}")
        return []


def fetch_detailed_data(imdb_id):
    """
    Fetch detailed OMDB + TMDB data.
    """

    try:
        # =====================================================
        # OMDB DETAILS
        # =====================================================

        omdb_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"

        omdb_response = requests.get(omdb_url, timeout=15)
        omdb_response.raise_for_status()

        omdb = omdb_response.json()

        title = omdb.get("Title", "")

        if not title:
            return omdb, {}

        # =====================================================
        # TMDB SEARCH
        # =====================================================

        tmdb_search_url = (
            f"https://api.themoviedb.org/3/search/movie"
            f"?api_key={TMDB_API_KEY}&query={title}"
        )

        tmdb_search_response = requests.get(
            tmdb_search_url,
            timeout=15
        )

        tmdb_search_response.raise_for_status()

        tmdb_search = tmdb_search_response.json()

        tmdb_data = {}

        if tmdb_search.get("results"):

            year = omdb.get("Year", "")[:4]

            # Try matching by year
            match = next(
                (
                    movie
                    for movie in tmdb_search["results"]
                    if movie.get("release_date", "").startswith(year)
                ),
                tmdb_search["results"][0]
            )

            movie_id = match.get("id")

            if movie_id:

                tmdb_detail_url = (
                    f"https://api.themoviedb.org/3/movie/{movie_id}"
                    f"?api_key={TMDB_API_KEY}"
                    f"&append_to_response=credits"
                )

                tmdb_response = requests.get(
                    tmdb_detail_url,
                    timeout=15
                )

                tmdb_response.raise_for_status()

                tmdb_data = tmdb_response.json()

        return omdb, tmdb_data

    except Exception as e:
        st.error(f"Movie detail fetch error: {e}")
        return None, None


# =====================================================
# APP TITLE
# =====================================================

st.title("South Indian Cinema Predictability Model v3i")

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("Step 1: Movie Search")

    search_query = st.text_input(
        "Enter Movie Title",
        value="Apex"
    )

    omdb = None
    tmdb = None

    if search_query:

        search_results = search_movies_list(search_query)

        if search_results:

            options = {
                f"{movie['Title']} ({movie['Year']})": movie["imdbID"]
                for movie in search_results
            }

            selected_label = st.selectbox(
                "Step 2: Select Movie",
                list(options.keys())
            )

            if selected_label:
                omdb, tmdb = fetch_detailed_data(
                    options[selected_label]
                )

        else:
            st.warning("No results found.")

    st.divider()

    st.header("Step 3: Analyze Pillars")

    # =====================================================
    # DEFAULT GENRE
    # =====================================================

    default_genre = "Action"

    if omdb:

        raw_genre = (
            omdb.get("Genre", "Action")
            .split(",")[0]
            .strip()
        )

        if raw_genre in GENRE_METRICS:
            default_genre = raw_genre

    genre = st.selectbox(
        "Genre",
        list(GENRE_METRICS.keys()),
        index=list(GENRE_METRICS.keys()).index(default_genre)
    )

    # =====================================================
    # ACTOR / DIRECTOR
    # =====================================================

    actor_key = st.selectbox(
        "Lead Actor",
        list(SOUTH_INDIAN_ACTORS.keys())
    )

    director_key = st.selectbox(
        "Director",
        list(DIRECTORS.keys())
    )

    # =====================================================
    # RELEASE DATE
    # =====================================================

    release_date = st.date_input(
        "Release Date",
        value=date(2026, 1, 12)
    )

    # =====================================================
    # CLASH
    # =====================================================

    has_clash = st.checkbox("Superstar Clash?")

    # =====================================================
    # BUDGET
    # =====================================================

    tmdb_budget = 0

    if tmdb:
        tmdb_budget = tmdb.get("budget", 0) / 10_000_000

    budget = st.number_input(
        "Budget (Crores)",
        min_value=1.0,
        value=float(tmdb_budget) if tmdb_budget > 0 else 100.0
    )

# =====================================================
# MAIN CALCULATION
# =====================================================

if omdb:

    market_multiplier = SEASONAL_MULTIPLIERS.get(
        release_date.month,
        1.0
    )

    calc_inputs = {
        "talent_score": (
            SOUTH_INDIAN_ACTORS[actor_key]["score"]
            + DIRECTORS[director_key]["score"]
        ) / 2,

        "market_base": 85,

        "market_multiplier": market_multiplier,

        "has_clash": has_clash,

        "content_score": GENRE_METRICS[genre]["base_score"],

        "viral_score": 75,

        "seasonal_score": (
            85 if market_multiplier > 1.0 else 70
        ),

        "m_cert": 1.0,

        "budget": budget if budget > 0 else 1.0,
    }

    report = calculate_detailed_prediction(calc_inputs)

    # =====================================================
    # METRICS
    # =====================================================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Predictability",
        f"{report['predictability_score']}%"
    )

    col2.metric(
        "Estimated Revenue",
        f"₹{report['revenue_estimate']} Cr"
    )

    col3.metric(
        "ROI",
        f"{report['roi_percentage']}%"
    )

    st.divider()

    # =====================================================
    # MOVIE DISPLAY
    # =====================================================

    left_col, right_col = st.columns([1, 2])

    with left_col:

        poster = omdb.get("Poster")

        if poster and poster != "N/A":
            st.image(poster)

    with right_col:

        st.subheader(
            f"{omdb.get('Title')} ({omdb.get('Year')})"
        )

        st.write(
            f"**Genre:** {omdb.get('Genre', 'N/A')}"
        )

        st.write(
            f"**Synopsis:** {omdb.get('Plot', 'N/A')}"
        )

        st.write(
            f"**Cast:** {omdb.get('Actors', 'N/A')}"
        )

        st.info(
            f"Risk Level: {report['risk_level']}"
        )

    # =====================================================
    # BREAKDOWN
    # =====================================================

    st.divider()

    st.subheader("Prediction Breakdown")

    breakdown = report.get("breakdown", {})

    for key, value in breakdown.items():
        st.write(f"**{key.title()} Score:** {value}")

else:
    st.info("Search for a movie to begin.")