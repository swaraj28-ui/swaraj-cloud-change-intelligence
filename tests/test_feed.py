import os
import pytest
from app import create_app
from app.database import db
from app.models import Source, ReleaseNote
from app.config import Config

TEST_DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.db')

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{TEST_DB_PATH}'
    GEMINI_API_KEY = None # Ensure heuristics fallback during testing

@pytest.fixture
def app():
    """
    Creates an isolated test application instance and sets up in-memory tables.
    """
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

@pytest.fixture
def client(app):
    return app.test_client()

def test_source_creation(app):
    """
    Verifies that Source feeds are properly stored and validated.
    """
    source = Source(name="AWS Updates", feed_url="https://aws.amazon.com/about-aws/whats-new/recent/feed/")
    db.session.add(source)
    db.session.commit()
    
    assert Source.query.count() == 1
    assert Source.query.first().name == "AWS Updates"
    assert Source.query.first().is_active is True

def test_release_note_relation(app):
    """
    Verifies relationship link between ReleaseNote and Source.
    """
    source = Source(name="GCP Feed", feed_url="https://cloud.google.com/feeds/gcp-release-notes.xml")
    db.session.add(source)
    db.session.commit()
    
    from datetime import datetime
    note = ReleaseNote(
        source_id=source.id,
        title="Artifact Registry deprecations",
        link="https://cloud.google.com/artifact-registry/deprecation",
        content="Artifact Registry is deprecating older container formats.",
        published_date=datetime.utcnow()
    )
    db.session.add(note)
    db.session.commit()
    
    assert ReleaseNote.query.count() == 1
    assert note.source.name == "GCP Feed"

