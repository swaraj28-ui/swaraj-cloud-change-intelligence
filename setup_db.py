import os
import sys
from datetime import datetime, timedelta

# Ensure parent directory is in python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Disable scheduler during DB migration and seeding
os.environ['DISABLE_SCHEDULER'] = 'true'

from app import create_app

from app.database import db
from app.models import Source, ReleaseNote, AIAnalysis, NotificationRule

def seed_database():
    app = create_app()
    with app.app_context():
        # Drop all tables first if we want a fresh start
        db.create_all()
        print("Database tables created successfully.")
        
        # 1. Seed Sources
        default_sources = [
            {"name": "Google Cloud Platform", "feed_url": "https://cloud.google.com/feeds/gcp-release-notes.xml", "is_active": True},
            {"name": "BigQuery Release Notes", "feed_url": "https://cloud.google.com/feeds/bigquery-release-notes.xml", "is_active": True},
            {"name": "Vertex AI Release Notes", "feed_url": "https://cloud.google.com/feeds/vertex-ai-release-notes.xml", "is_active": True},
            {"name": "Cloud Run Release Notes", "feed_url": "https://cloud.google.com/feeds/cloud-run-release-notes.xml", "is_active": True}
        ]
        
        seeded_sources = {}
        for src_data in default_sources:
            existing = Source.query.filter_by(feed_url=src_data["feed_url"]).first()
            if not existing:
                source = Source(
                    name=src_data["name"],
                    feed_url=src_data["feed_url"],
                    is_active=src_data["is_active"],
                    last_fetched_at=datetime.utcnow() - timedelta(hours=2)
                )
                db.session.add(source)
                db.session.flush() # Populate ID
                seeded_sources[src_data["name"]] = source
            else:
                seeded_sources[src_data["name"]] = existing
        
        db.session.commit()
        print("Default release note sources seeded.")

        # 2. Seed Mock Data (if empty)
        if ReleaseNote.query.count() == 0:
            mock_notes = [
                {
                    "source": seeded_sources["BigQuery Release Notes"],
                    "title": "Vulnerability CVE-2026-9918 In BigQuery Spark Connector Fixed",
                    "link": "https://cloud.google.com/bigquery/docs/release-notes#June_15_2026_security",
                    "content": "A vulnerability in the BigQuery Spark connector has been identified (CVE-2026-9918) which could allow remote code execution during query processing if untrusted schemas are loaded. We have released patch version v2.4.1 to address this. All users of the BigQuery Spark connector are strongly recommended to upgrade immediately. No mitigations are available for older versions.",
                    "published_date": datetime.utcnow() - timedelta(days=1),
                    "analysis": {
                        "executive_summary": "A critical remote code execution vulnerability (CVE-2026-9918) in the BigQuery Spark connector has been fixed in v2.4.1. Old versions are vulnerable during query rendering with untrusted schemas.",
                        "category": "Security",
                        "impact_score": 9,
                        "recommended_action": "Upgrade BigQuery Spark connector to version 2.4.1 immediately in all Spark environments (Dataproc, Databricks, etc.).",
                        "risk_level": "Critical",
                        "why_it_matters": "Remote code execution allows attackers to run arbitrary code on the processing nodes, potentially exposing secret credentials and system data.",
                        "severity": "Critical"
                    }
                },
                {
                    "source": seeded_sources["Cloud Run Release Notes"],
                    "title": "Upcoming Breaking Change: TLS 1.3 enforced by default",
                    "link": "https://cloud.google.com/run/docs/release-notes#June_12_2026_breaking",
                    "content": "Starting September 1, 2026, Cloud Run will enforce TLS 1.3 as the minimum transport layer security protocol for all standard gservice endpoints. TLS 1.0, 1.1, and 1.2 connections will be rejected by the frontend load balancers. Action is required for teams running legacy clients or integrations that do not support modern cipher suites.",
                    "published_date": datetime.utcnow() - timedelta(days=3),
                    "analysis": {
                        "executive_summary": "Cloud Run is enforcing TLS 1.3 as the minimum protocol standard starting September 1, 2026. This will break older client integrations relying on TLS 1.2 and below.",
                        "category": "Breaking Change",
                        "impact_score": 8,
                        "recommended_action": "Audit clients connecting to Cloud Run services to ensure they support TLS 1.3. Update connection libraries where necessary.",
                        "risk_level": "High",
                        "why_it_matters": "Enforcement of TLS 1.3 will block legacy APIs, mobile apps, or webhook consumers that cannot negotiate TLS 1.3, resulting in service disruptions.",
                        "severity": "High"
                    }
                },
                {
                    "source": seeded_sources["Vertex AI Release Notes"],
                    "title": "Vertex AI Custom Training Billing Granularity Reduced to 1-Second Increments",
                    "link": "https://cloud.google.com/vertex-ai/docs/release-notes#June_10_2026_cost",
                    "content": "We are pleased to announce that billing granularity for custom machine training jobs on Vertex AI has been optimized. Charges will now be computed in 1-second increments with a minimum billing time of 1 minute. Previously, billing was computed in 1-minute increments. This change is automatically active and applies to all custom training jobs in all regions.",
                    "published_date": datetime.utcnow() - timedelta(days=5),
                    "analysis": {
                        "executive_summary": "Billing for Vertex AI Custom Training custom machines is now calculated per second rather than per minute, providing finer granularity and reducing costs for short runs.",
                        "category": "Cost Optimization",
                        "impact_score": 5,
                        "recommended_action": "No code changes required. Short training iterations or fine-tuning pipelines will automatically see reduced infrastructure costs.",
                        "risk_level": "Low",
                        "why_it_matters": "Transitioning to per-second billing reduces cost wastage for micro-training tasks, automated CI/CD validation runs, and pipeline testing.",
                        "severity": "Low"
                    }
                },
                {
                    "source": seeded_sources["Google Cloud Platform"],
                    "title": "Google Cloud Storage Deprecates Regional and Multi-Regional API Storage Classes",
                    "link": "https://cloud.google.com/storage/docs/release-notes#June_05_2026_deprecation",
                    "content": "To streamline storage models, Google Cloud Storage is deprecating the legacy regional and multi-regional API class names. Developers should migrate configurations to use Standard, Nearline, Coldline, or Archive classes combined with location targets. The deprecated regional API fields will be completely decommissioned by June 2027.",
                    "published_date": datetime.utcnow() - timedelta(days=10),
                    "analysis": {
                        "executive_summary": "Google Cloud Storage is deprecating legacy Regional and Multi-Regional API class labels in favor of Standard storage class. Decommissioning will be complete by June 2027.",
                        "category": "Deprecation",
                        "impact_score": 6,
                        "recommended_action": "Migrate IaC code (Terraform, CloudFormation, SDKs) references of storage classes from 'REGIONAL' or 'MULTI_REGIONAL' to 'STANDARD'.",
                        "risk_level": "Medium",
                        "why_it_matters": "Although decommission is in 2027, updating configurations now avoids pipeline failure and ensures compliance with modern object storage APIs.",
                        "severity": "Medium"
                    }
                }
            ]

            for note_data in mock_notes:
                note = ReleaseNote(
                    source_id=note_data["source"].id,
                    title=note_data["title"],
                    link=note_data["link"],
                    content=note_data["content"],
                    published_date=note_data["published_date"]
                )
                db.session.add(note)
                db.session.flush() # Get note ID
                
                analysis_data = note_data["analysis"]
                analysis = AIAnalysis(
                    release_note_id=note.id,
                    executive_summary=analysis_data["executive_summary"],
                    category=analysis_data["category"],
                    impact_score=analysis_data["impact_score"],
                    recommended_action=analysis_data["recommended_action"],
                    risk_level=analysis_data["risk_level"],
                    why_it_matters=analysis_data["why_it_matters"],
                    severity=analysis_data["severity"]
                )
                db.session.add(analysis)

            db.session.commit()
            print("Realistic demo release notes and AI analyses seeded.")
            
        # 3. Seed Default Notification Rules
        if NotificationRule.query.count() == 0:
            rules = [
                NotificationRule(
                    rule_name="Critical Alert Rule",
                    condition_type="severity",
                    condition_value="Critical",
                    delivery_channel="slack",
                    recipient="https://example.com/slack-webhook-placeholder",
                    is_active=False # Inactive by default so it doesn't cause errors
                ),
                NotificationRule(
                    rule_name="Security Category Rule",
                    condition_type="category",
                    condition_value="Security",
                    delivery_channel="email",
                    recipient="security-alerts@example.com",
                    is_active=False
                )
            ]
            for rule in rules:
                db.session.add(rule)
            db.session.commit()
            print("Default alert notification rules seeded.")

if __name__ == '__main__':
    seed_database()
