import feedparser
from datetime import datetime
import time
from app.database import db
from app.models import Source, ReleaseNote, AIAnalysis
from app.services.ai_service import analyze_release_note
from app.services.impact_engine import calculate_impact
from app.services.notification import dispatch_notifications

def sync_feeds(app):
    """
    Synchronizes RSS feeds for all active sources in the database.
    Integrates feed fetching, AI analysis, impact assessment, and notifications.
    """
    with app.app_context():
        app.logger.info("Starting background feed synchronization...")
        active_sources = Source.query.filter_by(is_active=True).all()
        
        for source in active_sources:
            app.logger.info(f"Syncing source: {source.name} ({source.feed_url})")
            try:
                # Parse RSS/Atom Feed
                feed = feedparser.parse(source.feed_url)
                
                # Check for general parsing errors (feedparser puts exceptions in feed.bozo)
                if feed.bozo and hasattr(feed, 'bozo_exception'):
                    app.logger.warning(f"Parser warning for source '{source.name}': {feed.bozo_exception}")
                
                new_notes_count = 0
                for entry in feed.entries:
                    link = entry.get('link')
                    if not link:
                        continue
                    
                    # Prevent duplicate ingestion
                    existing = ReleaseNote.query.filter_by(link=link).first()
                    if existing:
                        continue
                    
                    title = entry.get('title', 'No Title Available')
                    # Standard RSS feeds use summary or description; Atom uses content
                    content = entry.get('summary', '')
                    if not content and 'description' in entry:
                        content = entry.get('description', '')
                    if not content and 'content' in entry:
                        content = entry.content[0].value if isinstance(entry.content, list) else entry.content
                    
                    # Clean content if empty
                    if not content:
                        content = "No description provided."
                        
                    # Parse published date structure
                    pub_date_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                    if pub_date_struct:
                        published_date = datetime.fromtimestamp(time.mktime(pub_date_struct))
                    else:
                        published_date = datetime.utcnow()
                    
                    # Ingest Release Note
                    note = ReleaseNote(
                        source_id=source.id,
                        title=title,
                        link=link,
                        content=content,
                        published_date=published_date,
                        fetched_at=datetime.utcnow()
                    )
                    db.session.add(note)
                    db.session.flush() # Flush to assign note.id
                    
                    # Run AI Analysis Layer
                    try:
                        analysis_data = analyze_release_note(note)
                        # Process and enhance with rule-based impact scoring
                        analysis_data = calculate_impact(note, analysis_data)
                        
                        # Store AI analysis results
                        analysis = AIAnalysis(
                            release_note_id=note.id,
                            executive_summary=analysis_data.get('executive_summary', 'Summarization failed.'),
                            category=analysis_data.get('category', 'Infrastructure'),
                            impact_score=analysis_data.get('impact_score', 5),
                            recommended_action=analysis_data.get('recommended_action', 'Review changes.'),
                            risk_level=analysis_data.get('risk_level', 'Low'),
                            why_it_matters=analysis_data.get('why_it_matters', 'No specific context generated.'),
                            severity=analysis_data.get('severity', 'Low')
                        )
                        db.session.add(analysis)
                        db.session.flush()
                        
                        # Trigger dispatch of notifications based on rules
                        dispatch_notifications(note, analysis)
                        
                    except Exception as ai_err:
                        app.logger.error(f"Failed to analyze release note {note.id} ({note.title}): {ai_err}")
                        # Provide a safe fallback analysis entry
                        fallback_analysis = AIAnalysis(
                            release_note_id=note.id,
                            executive_summary=f"Fallback: AI analysis failed. Title: {note.title}",
                            category="Infrastructure",
                            impact_score=5,
                            recommended_action="Please review original documentation.",
                            risk_level="Medium",
                            why_it_matters="System was unable to contact AI provider.",
                            severity="Medium"
                        )
                        db.session.add(fallback_analysis)
                    
                    new_notes_count += 1
                
                # Update last fetched timestamp
                source.last_fetched_at = datetime.utcnow()
                db.session.commit()
                app.logger.info(f"Completed sync for '{source.name}'. Added {new_notes_count} updates.")
                
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error during synchronization of feed source {source.name}: {e}")
