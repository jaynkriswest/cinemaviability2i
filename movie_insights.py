import requests
from difflib import SequenceMatcher

# =====================================================
# SEARCH MOVIES USING SYNOPSIS
# =====================================================

def search_movies_by_synopsis(
    synopsis,
    api_key
):

    try:

        query = synopsis[:100]

        url = (
            "https://api.themoviedb.org/3/search/movie"
            f"?api_key={api_key}"
            f"&query={query}"
        )

        response = requests.get(
            url,
            timeout=15
        )

        data = response.json()

        return data.get("results", [])[:5]

    except:
        return []

# =====================================================
# FETCH FULL MOVIE DETAILS
# =====================================================

def fetch_full_movie_details(
    movie_id,
    api_key
):

    try:

        url = (
            f"https://api.themoviedb.org/3/movie/{movie_id}"
            f"?api_key={api_key}"
        )

        response = requests.get(
            url,
            timeout=15
        )

        return response.json()

    except:
        return {}

# =====================================================
# FUTURE FILM LIKENESS SCORE
# =====================================================

def calculate_future_likeness(
    future_synopsis,
    future_genre,
    historical_movie
):

    score = 0

    # Synopsis similarity
    overview = historical_movie.get(
        "overview",
        ""
    )

    synopsis_similarity = (
        SequenceMatcher(
            None,
            future_synopsis.lower(),
            overview.lower()
        ).ratio()
    )

    score += synopsis_similarity * 70

    # Genre weighting
    genre_ids = historical_movie.get(
        "genre_ids",
        []
    )

    if genre_ids:
        score += 20

    # Popularity weighting
    popularity = historical_movie.get(
        "popularity",
        0
    )

    score += min(popularity / 10, 10)

    return round(min(score, 100), 1)

# =====================================================
# PERFORMANCE CLASSIFICATION
# =====================================================

def classify_movie_success(movie):

    revenue = movie.get(
        "revenue",
        0
    )

    budget = movie.get(
        "budget",
        1
    )

    if budget <= 0:
        return "Unknown"

    roi = revenue / budget

    if roi >= 3:
        return "Blockbuster"

    elif roi >= 1.5:
        return "Hit"

    elif roi >= 1:
        return "Average"

    return "Flop"

# =====================================================
# SUCCESS ANALYSIS
# =====================================================

def analyze_success_reasons(movie):

    reasons = []

    popularity = movie.get(
        "popularity",
        0
    )

    vote_average = movie.get(
        "vote_average",
        0
    )

    runtime = movie.get(
        "runtime",
        0
    )

    revenue = movie.get(
        "revenue",
        0
    )

    budget = movie.get(
        "budget",
        1
    )

    roi = revenue / max(budget, 1)

    if popularity > 80:

        reasons.append(
            "Strong audience engagement and awareness."
        )

    if roi > 2:

        reasons.append(
            "Excellent commercial ROI efficiency."
        )

    if vote_average > 7:

        reasons.append(
            "Positive audience reception."
        )

    if runtime < 170:

        reasons.append(
            "Audience-friendly runtime supported theatrical performance."
        )

    genres = [
        genre["name"]
        for genre in movie.get(
            "genres",
            []
        )
    ]

    if "Action" in genres:

        reasons.append(
            "Strong mass-market action appeal."
        )

    if "Family" in genres:

        reasons.append(
            "Broad family audience accessibility."
        )

    return reasons

# =====================================================
# FAILURE ANALYSIS
# =====================================================

def analyze_failure_reasons(movie):

    reasons = []

    popularity = movie.get(
        "popularity",
        0
    )

    runtime = movie.get(
        "runtime",
        0
    )

    revenue = movie.get(
        "revenue",
        0
    )

    budget = movie.get(
        "budget",
        1
    )

    roi = revenue / max(budget, 1)

    if roi < 1:

        reasons.append(
            "Weak commercial ROI performance."
        )

    if popularity < 40:

        reasons.append(
            "Low audience engagement and buzz."
        )

    if runtime > 180:

        reasons.append(
            "Excessive runtime may reduce repeat viewership."
        )

    if budget > 250000000:

        reasons.append(
            "High production budget increased financial risk."
        )

    return reasons