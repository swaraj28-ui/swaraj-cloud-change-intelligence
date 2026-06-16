def calculate_impact(note, analysis_data):
    """
    Refines the AI-provided impact score by applying rule-based weighting
    for critical keywords and maps the score to visual severity levels.
    """
    title_lower = note.title.lower()
    content_lower = note.content.lower()
    
    # Get current score from analysis, defaulting to 5
    score = int(analysis_data.get('impact_score', 5))
    
    # Keyword criteria for impact enhancements
    breaking_keywords = ["deprecated", "deprecation", "removal", "breaking change", "migration required", "sunset"]
    security_keywords = ["security", "vulnerability", "cve-", "patch", "exploit", "attack", "compromise"]
    
    # Apply modifier points
    if any(kw in title_lower or kw in content_lower for kw in breaking_keywords):
        score += 2
        
    if any(kw in title_lower or kw in content_lower for kw in security_keywords):
        score += 3
        
    # Clamp score to standard 1-10 range
    score = max(1, min(10, score))
    
    # Determine visual severity badge value
    if score >= 9:
        severity = "Critical"
    elif score >= 7:
        severity = "High"
    elif score >= 5:
        severity = "Medium"
    else:
        severity = "Low"
        
    analysis_data['impact_score'] = score
    analysis_data['severity'] = severity
    
    # Keep risk level synchronized with the severity score classification
    analysis_data['risk_level'] = severity
    
    return analysis_data
