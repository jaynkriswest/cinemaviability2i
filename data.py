# data.py

# Based on Pillar 1: Talent (30% Weight) from v3i_3.docx
TALENT_DATABASE = {
    "Chiranjeevi": {
        "score": 98, 
        "tier": "Ultra-Veteran", 
        "criteria": "200+ Credits / Highest ROI Stability Floor"
    },
    "Rajinikanth": {
        "score": 98, 
        "tier": "Ultra-Veteran", 
        "criteria": "200+ Credits"
    },
    "Balakrishna": {
        "score": 90, 
        "tier": "Veteran", 
        "criteria": "25+ Year Track Record"
    },
    "Prabhas": {
        "score": 92, 
        "tier": "Superstar", 
        "criteria": "10-25 Year Career / Peak Popularity"
    },
    "Siddu Jonnalagadda": {
        "score": 70, 
        "tier": "Rising Star", 
        "criteria": "High Growth Velocity"
    }
}

# Based on Pillar 3: Content (20% Weight) from v3i_3.docx
GENRE_METRICS = {
    "Mass Action": {"base_score": 95, "risk": "Low / High ROI"},
    "Sci-Fi": {"base_score": 65, "risk": "High Risk"},
    "Family Drama": {"base_score": 85, "risk": "Stable / High Seasonal Affinity"}
}