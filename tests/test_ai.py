import pytest
from app.models import ReleaseNote
from app.services.ai_service import get_heuristic_analysis
from datetime import datetime

def test_security_heuristic():
    """
    Verifies that security-related keywords classify release notes under 'Security'.
    """
    note = ReleaseNote(
        title="Security Advisory: Vulnerability CVE-2026-1029 patched in Cloud Run",
        content="We have patched a critical authentication bypass vulnerability in Cloud Run configurations.",
        link="https://cloud.google.com/run/cve-1029",
        published_date=datetime.utcnow()
    )
    analysis = get_heuristic_analysis(note)
    assert analysis['category'] == 'Security'
    assert analysis['impact_score'] >= 8
    assert analysis['risk_level'] == 'Critical'

def test_deprecation_heuristic():
    """
    Verifies that deprecation labels classify release notes under 'Deprecation'.
    """
    note = ReleaseNote(
        title="Artifact Registry GCR translation API is deprecated",
        content="Please migrate client integrations from older GCR interfaces.",
        link="https://cloud.google.com/run/gcr-dep",
        published_date=datetime.utcnow()
    )
    analysis = get_heuristic_analysis(note)
    assert analysis['category'] == 'Deprecation'
    assert analysis['impact_score'] == 6
    assert analysis['risk_level'] == 'Medium'

def test_cost_heuristic():
    """
    Verifies that cost/pricing labels classify notes under 'Cost Optimization'.
    """
    note = ReleaseNote(
        title="Compute Engine pricing modifications for E2 instances",
        content="We are adjusting the hourly running rates for older instance types.",
        link="https://cloud.google.com/compute/pricing-e2",
        published_date=datetime.utcnow()
    )
    analysis = get_heuristic_analysis(note)
    assert analysis['category'] == 'Cost Optimization'
    assert analysis['risk_level'] == 'Low'
