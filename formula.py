def calculate_v3i_logic(inputs):
    # 1. Core Pillar Calculation
    s_talent = inputs['talent_score']
    s_market = inputs['market_score']
    s_content = inputs['content_score']
    s_viral = inputs['viral_score']
    s_seasonal = inputs['seasonal_score']
    
    weighted_sum = (
        (s_talent * 0.30) + 
        (s_market * 0.20) + 
        (s_content * 0.20) + 
        (s_viral * 0.15) + 
        (s_seasonal * 0.15)
    )
    
    # 2. Apply Multipliers (Certification & Alignment)
    final_prob = weighted_sum * inputs['m_cert'] * inputs['m_align']
    final_prob = min(final_prob, 99.0)

    # 3. Revenue & ROI Logic
    # Revenue is estimated based on probability, market reach, and franchise status
    rev_multiplier = 1.4 if inputs['is_franchise'] else 1.0
    # Formula: (Prob/100) * (Market Weighting) * Multiplier
    est_revenue = (final_prob / 100) * (inputs['budget'] * 2.8) * rev_multiplier
    
    # ROI % = ((Revenue - Cost) / Cost) * 100
    roi_percent = ((est_revenue - inputs['budget']) / inputs['budget']) * 100

    return final_prob, est_revenue, roi_percent