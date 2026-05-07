# data.py
# Reference your v3i_5 rules here

GENRE_METRICS = {
    "Action": {"base_score": 95, "risk": "Low / High ROI"},
    "Drama": {"base_score": 80, "risk": "Moderate"},
    "Sci-Fi": {"base_score": 65, "risk": "High Risk"},
    # Add other genres from your document
}

TALENT_TIERS = {
    "Ultra-Veteran": {"score": 98, "min_credits": 200},
    "Veteran": {"score": 90, "min_credits": 25},
    "Superstar": {"score": 92, "min_credits": 10},
    "Rising Star": {"score": 70, "min_credits": 1}
}