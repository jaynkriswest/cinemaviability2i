def calculate_v3i_logic(inputs):
    # Core weighted sum from the v3i formula
    s_talent = inputs['talent_score']
    s_market = inputs['market_score']
    s_content = inputs['content_score']
    s_viral = inputs['viral_score']
    s_seasonal = inputs['seasonal_score']
    
    base_prob = (
        (s_talent * 0.30) + 
        (s_market * 0.20) + 
        (s_content * 0.20) + 
        (s_viral * 0.15) + 
        (s_seasonal * 0.15)
    )
    
    # Final predictability score with multipliers
    final_prob = base_prob * inputs['m_cert'] * inputs['m_align']
    final_prob = min(final_prob, 99.0)

    # NEW LOGIC: Talent-Budget Efficiency
    # This prevents revenue from scaling linearly with budget if talent tier is low
    efficiency_multiplier = 1.0
    
    # If budget exceeds 100Cr, we check if the talent score justifies it
    if inputs['budget'] > 100:
        if s_talent < 80: # Rising Star Tier
            efficiency_multiplier = 0.5 # 50% penalty for over-leveraging
        elif s_talent < 95: # Superstar Tier
            efficiency_multiplier = 0.8 # 20% penalty
        # Ultra-Veterans (95+) stay at 1.0 efficiency

    # Revenue Calculation: Probability scaled by a Market Cap and Efficiency
    # (Removes the 'Infinite Revenue' bug)
    market_potential = 400 # Max theatrical cap in Crores
    rev_bonus = 1.4 if inputs['is_franchise'] else 1.0
    
    est_revenue = (final_prob / 100) * market_potential * efficiency_multiplier * rev_bonus
    
    # ROI Calculation
    roi_percent = ((est_revenue - inputs['budget']) / inputs['budget']) * 100

    return final_prob, est_revenue, roi_percent