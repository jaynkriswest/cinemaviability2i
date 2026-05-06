SOUTH_INDIAN_TALENT_DB = {
    "Chiranjeevi": {"score": 98, "tier": "Ultra-Veteran"},
    "Rajinikanth": {"score": 98, "tier": "Ultra-Veteran"},
    "Mammootty": {"score": 96, "tier": "Ultra-Veteran"},
    "Prabhas": {"score": 94, "tier": "Superstar"},
    "Allu Arjun": {"score": 93, "tier": "Superstar"},
    "Siddu Jonnalagadda": {"score": 72, "tier": "Rising Star"}
}

GENRE_BASELINES = {
    "Mass Action": 95,
    "Family Drama": 85,
    "Mythological": 90,
    "Romance": 75,
    "Sci-Fi": 65
}

def get_talent_weight(name):
    return SOUTH_INDIAN_TALENT_DB.get(name, {"score": 60, "tier": "Rising Star"})