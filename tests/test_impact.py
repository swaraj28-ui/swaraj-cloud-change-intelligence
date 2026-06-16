import pytest
from app.models import ReleaseNote
from app.services.impact_engine import calculate_impact
from datetime import datetime

def test_impact_engine_clamping():
    """
    Ensures the final computed impact score is clamped to a maximum of 10.
    """
    note = ReleaseNote(
        title="Vulnerability exploit patch for BigQuery endpoints",
        content="A vulnerability bypass CVE-2026-9901 has been fixed. Migration required immediately.",
        link="https://cloud.google.com/bq/vuln",
        published_date=datetime.utcnow()
    )
    
    # Starting with a high score of 9, modifiers should not exceed 10
    raw_analysis = {
        "impact_score": 9,
        "category": "Security"
    }
    
    refined = calculate_impact(note, raw_analysis)
    assert refined['impact_score'] == 10
    assert refined['severity'] == 'Critical'

def test_impact_engine_security_bump():
    """
    Ensures that security updates receive a deterministic boost in severity points.
    """
    note = ReleaseNote(
        title="Security advisory patch",
        content="This update fixes a TLS configuration anomaly.",
        link="https://cloud.google.com/sec/patch",
        published_date=datetime.utcnow()
    )
    
    raw_analysis = {
        "impact_score": 4,
        "category": "Infrastructure"
    }
    
    refined = calculate_impact(note, raw_analysis)
    # Starts at 4 + 3 (security keyword in title) = 7
    assert refined['impact_score'] == 7
    assert refined['severity'] == 'High'

def test_severity_levels():
    """
    Validates severity boundaries matching calculated scores.
    """
    note = ReleaseNote(title="Minor update", content="Routine metadata adjustments.", link="https://cloud.google.com/", published_date=datetime.utcnow())
    
    # Low score test
    l_analysis = calculate_impact(note, {"impact_score": 3})
    assert l_analysis['severity'] == 'Low'
    
    # Medium score test
    m_analysis = calculate_impact(note, {"impact_score": 5})
    assert m_analysis['severity'] == 'Medium'
    
    # High score test
    h_analysis = calculate_impact(note, {"impact_score": 7})
    assert h_analysis['severity'] == 'High'
    
    # Critical score test
    c_analysis = calculate_impact(note, {"impact_score": 9})
    assert c_analysis['severity'] == 'Critical'
