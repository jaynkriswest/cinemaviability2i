def calculate_v3i_logic(inputs):
    # Pillar 1: Talent (30%)
    s_talent = inputs['talent_score']
    
    # Pillar 2: Market (20%)
    # Using 'market_base' to match the key in app.py
    s_market = (inputs['market_base'] * inputs['market_multiplier'])
    if inputs['has_clash']:
        s_market -= 15 # -0.15 Clash Penalty

    # Pillar 3: Content (20%)
    s_content = inputs['content_score']
    if inputs['is_franchise']:
        s_content *= 1.4 # Franchise Bonus

    # Pillar 4: Viral (15%)
    s_viral = inputs['viral_score']
    
    # Pillar 5: Seasonal (15%)
    s_seasonal = inputs['seasonal_score']

    # THE PREDICTABILITY EQUATION
    weighted_sum = (
        (s_talent * 0.30) + 
        (s_market * 0.20) + 
        (s_content * 0.20) + 
        (s_viral * 0.15) + 
        (s_seasonal * 0.15)
    )
    
    # Global Reach Multipliers
    final_prob = weighted_sum * inputs['m_cert'] * inputs['m_align']
    
    # Financial Logic: Revenue & ROI
    # Check for Efficiency Penalty (Budget > 150 Cr + Lower Talent)
    efficiency = 1.0
    if inputs['budget'] > 150 and s_talent < 90:
        efficiency = 0.8 
    
    # Standard ROI floor for Ultra-Veterans
    revenue_multiplier = 2.0 
    est_revenue = (final_prob / 100) * (inputs['budget'] * revenue_multiplier) * efficiency
    
    roi = ((est_revenue - inputs['budget']) / inputs['budget']) * 100

    return min(final_prob, 99.0), est_revenue, roi