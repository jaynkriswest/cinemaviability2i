#Clde version updates with gemini + CGPT

# app.py - Corrected Version

import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import date
import logging

# =====================================================
# IMPORT LOCAL MODULES
# =====================================================

from data import (
    GENRE_METRICS,
    SOUTH_INDIAN_ACTORS,
    DIRECTORS,
    SEASONAL_MULTIPLIERS,
)

from formula import (
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

TMDB_API_KEY = (
    st.secrets.get("TMDB_API_KEY")
    or os.getenv("TMDB_API_KEY")
)

# =====================================================
# VALIDATION
# =====================================================

if not TMDB_API_KEY:
    st.error("Missing TMDB_API_KEY in Streamlit secrets.")
    st.stop()

# =====================================================
# TMDB SEARCH FUNCTION
# =====================================================

def search_movies_list(query):
    """
    Search TMDB for movies.
    """

    try:

        url = (
            "https://api.themoviedb.org/3/search/movie"
            f"?api_key={TMDB_API_KEY}"
            f"&query={query}"
        )

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for movie in data.get("results", []):

            release_date = movie.get("release_date", "")

            year = (
                release_date[:4]
                if release_date
                else "Unknown"
            )

            results.append({
                "Title": movie.get("title", "Unknown"),
                "Year": year,
                "tmdbID": movie.get("id")
            })

        return results

    except Exception as e:
        st.error(f"TMDB search error: {e}")
        return []

# =====================================================
# FETCH MOVIE DETAILS
# =====================================================

def fetch_detailed_data(tmdb_id):

    try:

        url = (
            f"https://api.themoviedb.org/3/movie/{tmdb_id}"
            f"?api_key={TMDB_API_KEY}"
            f"&append_to_response=credits"
        )

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        tmdb = response.json()

        poster_path = tmdb.get("poster_path")

        poster_url = None

        if poster_path:
            poster_url = (
                f"https://image.tmdb.org/t/p/w500"
                f"{poster_path}"
            )

        genres = ", ".join(
            [
                genre["name"]
                for genre in tmdb.get("genres", [])
            ]
        )

        cast_names = ", ".join(
            [
                cast["name"]
                for cast in tmdb.get(
                    "credits",
                    {}
                ).get("cast", [])[:5]
            ]
        )

        movie_data = {
            "Title": tmdb.get("title", "Unknown"),
            "Year": tmdb.get(
                "release_date",
                ""
            )[:4],
            "Genre": genres,
            "Plot": tmdb.get(
                "overview",
                "No overview available."
            ),
            "Poster": poster_url,
            "Actors": cast_names,
        }

        return movie_data, tmdb

    except Exception as e:
        st.error(f"TMDB detail fetch error: {e}")
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

    movie_data = None
    tmdb_data = None

    # =====================================================
    # SEARCH RESULTS
    # =====================================================

    if search_query:

        search_results = search_movies_list(
            search_query
        )

        if search_results:

            options = {
                f"{movie['Title']} ({movie['Year']})":
                movie["tmdbID"]

                for movie in search_results
            }

            selected_label = st.selectbox(
                "Step 2: Select Movie",
                list(options.keys())
            )

            if selected_label:

                movie_data, tmdb_data = (
                    fetch_detailed_data(
                        options[selected_label]
                    )
                )

        else:
            st.warning("No results found.")

    st.divider()

    # =====================================================
    # ANALYSIS SECTION
    # =====================================================

    st.header("Step 3: Analyze Pillars")

    default_genre = "Action"

    if movie_data:

        raw_genre = (
            movie_data.get("Genre", "Action")
            .split(",")[0]
            .strip()
        )

        if raw_genre in GENRE_METRICS:
            default_genre = raw_genre

    genre = st.selectbox(
        "Genre",
        list(GENRE_METRICS.keys()),
        index=list(GENRE_METRICS.keys()).index(
            default_genre
        )
    )

    actor_key = st.selectbox(
        "Lead Actor",
        list(SOUTH_INDIAN_ACTORS.keys())
    )

    director_key = st.selectbox(
        "Director",
        list(DIRECTORS.keys())
    )

    release_date = st.date_input(
        "Release Date",
        value=date(2026, 1, 12)
    )

    has_clash = st.checkbox(
        "Superstar Clash?"
    )

    # =====================================================
    # BUDGET
    # =====================================================

    tmdb_budget = 0

    if tmdb_data:
        tmdb_budget = (
            tmdb_data.get("budget", 0)
            / 10_000_000
        )

    budget = st.number_input(
        "Budget (Crores)",
        min_value=1.0,
        value=(
            float(tmdb_budget)
            if tmdb_budget > 0
            else 100.0
        )
    )

# =====================================================
# MAIN DISPLAY
# =====================================================

if movie_data:

    market_multiplier = (
        SEASONAL_MULTIPLIERS.get(
            release_date.month,
            1.0
        )
    )

    calc_inputs = {

        "talent_score": (
            SOUTH_INDIAN_ACTORS[actor_key]["score"]
            + DIRECTORS[director_key]["score"]
        ) / 2,

        "market_base": 85,

        "market_multiplier": market_multiplier,

        "has_clash": has_clash,

        "content_score": (
            GENRE_METRICS[genre]["base_score"]
        ),

        "viral_score": 75,

        "seasonal_score": (
            85
            if market_multiplier > 1.0
            else 70
        ),

        "m_cert": 1.0,

        "budget": (
            budget
            if budget > 0
            else 1.0
        ),
    }

    report = calculate_detailed_prediction(
        calc_inputs
    )

    # =====================================================
    # TOP METRICS
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
    # MOVIE INFO
    # =====================================================

    left_col, right_col = st.columns([1, 2])

    with left_col:

        poster = movie_data.get("Poster")

        if poster:
            st.image(
                poster,
                use_container_width=True
            )

    with right_col:

        st.subheader(
            f"{movie_data.get('Title')} "
            f"({movie_data.get('Year')})"
        )

        st.write(
            f"**Genre:** "
            f"{movie_data.get('Genre', 'N/A')}"
        )

        st.write(
            f"**Synopsis:** "
            f"{movie_data.get('Plot', 'N/A')}"
        )

        st.write(
            f"**Cast:** "
            f"{movie_data.get('Actors', 'N/A')}"
        )

        st.info(
            f"Risk Level: "
            f"{report['risk_level']}"
        )

    # =====================================================
    # BREAKDOWN
    # =====================================================

    st.divider()

    st.subheader("Prediction Breakdown")

    breakdown = report.get(
        "breakdown",
        {}
    )

    for key, value in breakdown.items():

        st.write(
            f"**{key.title()} Score:** {value}"
        )

else:

    st.info(
        "Search for a movie to begin."
    )