import requests
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

def fetch_full_movie_details(title: str, api_key: str) -> dict:
    """
    Fetch full movie details from TMDB.
    """
    if not api_key:
        return {}
    
    search_url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": api_key, "query": title, "region": "IN"}
    
    try:
        response = requests.get(search_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("results"):
            movie_id = data["results"]["id"]
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            details_params = {"api_key": api_key, "append_to_response": "credits,keywords"}
            
            det_response = requests.get(details_url, params=details_params, timeout=5)
            det_response.raise_for_status()
            return det_response.json()
    except Exception as e:
        logger.error(f"Error fetching detailed movie data: {str(e)}")
        
    return {}

def search_movies_by_synopsis(synopsis: str, genre_name: str, language_code: str, tmdb_api_key: str) -> list:
    """
    Finds historical archetype films from TMDB based on genre/language, 
    then applies TF-IDF and Cosine Similarity to calculate a narrative Likeness Score.
    """
    if not tmdb_api_key or not synopsis:
        return []

    # Map application genre keys to TMDB Genre IDs
    tmdb_genre_map = {
        "Action": 28, "Comedy": 35, "Drama": 18, "Thriller": 53, 
        "Romance": 10749, "Horror": 27, "Sci-Fi": 878, "Mythology": 14, "Biopic": 36
    }
    genre_id = tmdb_genre_map.get(genre_name, 28)

    # Core historical discovery pool targeting Indian Market context
    discover_url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": tmdb_api_key,
        "region": "IN",
        "with_original_language": language_code,
        "with_genres": genre_id,
        "sort_by": "revenue.desc",  # Focus comparison pool on financially validated archetypes
        "page": 1
    }

    try:
        response = requests.get(discover_url, params=params, timeout=5)
        response.raise_for_status()
        historical_pool = response.json().get("results", [])

        if not historical_pool:
            # Fallback if specific regional language filter is too restrictive
            params.pop("with_original_language")
            response = requests.get(discover_url, params=params, timeout=5)
            historical_pool = response.json().get("results", [])

        if not historical_pool:
            return []

        # Construct corpus for Vectorizer Matrix
        documents = [synopsis]  # Element is the target project text
        movie_metadata_map = []

        for movie in historical_pool:
            overview = movie.get("overview")
            if overview and len(overview.strip()) > 20:
                documents.append(overview)
                movie_metadata_map.append(movie)

        if len(documents) < 2:
            return []

        # Vector Engine Execution (TF-IDF NLP Analysis)
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(documents)

        # Vector comparison: Input text [0:1] evaluated against all pool matrices [1:]
        similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        compiled_comps = []
        for idx, score in enumerate(similarity_scores):
            raw_percent = float(score) * 100
            
            # Normalize and establish an industry baseline floor (base alignment match)
            likeness_score = min(round(raw_percent * 2.5 + 15.0, 1), 98.5)
            if likeness_score < 25.0:
                likeness_score = round(25.0 + (raw_percent * 0.5), 1)

            matched_movie = movie_metadata_map[idx]
            compiled_comps.append({
                "title": matched_movie.get("title"),
                "release_year": matched_movie.get("release_date", "####")[:4],
                "historical_overview": matched_movie.get("overview"),
                "likeness_score": likeness_score
            })

        # Return top 3 strongest historical structural comps
        compiled_comps = sorted(compiled_comps, key=lambda x: x["likeness_score"], reverse=True)
        return compiled_comps[:3]

    except Exception as e:
        logger.error(f"Error executing synopsis likeness engine: {str(e)}")
        return []

def calculate_future_likeness(synopsis: str, historical_overviews: list) -> float:
    """Helper component tracking raw baseline structural variance calculations."""
    if not synopsis or not historical_overviews:
        return 0.0
    try:
        corpus = [synopsis] + historical_overviews
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform(corpus)
        scores = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        return float(scores.mean() * 100)
    except:
        return 0.0

def classify_movie_success(predictability_score: float, roi_percentage: float) -> str:
    if predictability_score >= 85 and roi_percentage >= 50:
        return "High Probability Blockbuster Equity"
    elif predictability_score >= 65 and roi_percentage >= 0:
        return "Stable Break-Even / Controlled Risk Profile"
    else:
        return "High Capital Risk Contingency"

def analyze_success_reasons(inputs: dict) -> list:
    reasons = []
    if inputs.get("talent_score", 0) >= 85:
        reasons.append("Elite historical talent index anchor drastically lowers distribution risk windows.")
    if inputs.get("is_franchise"):
        reasons.append("Sequel IP leverage provides built-in minimum opening structural guarantees.")
    if inputs.get("market_multiplier", 1.0) >= 1.2:
        reasons.append("Wide Pan-India scaling structure offsets reliance on single state performance variables.")
    return reasons

def analyze_failure_reasons(inputs: dict) -> list:
    reasons = []
    if inputs.get("has_clash"):
        reasons.append("Market Screen saturation collision (Clash) severely diminishes early theater slot retention capacity.")
    if inputs.get("m_cert", 1.0) <= 0.8:
        reasons.append("Adult ('A') certification penalty creates a significant family audience block constraint.")
    if inputs.get("budget", 0) > 150:
        reasons.append("Extremely high capital exposure ceiling demands multi-region crossover metrics just to achieve par break-even.")
    return reasons