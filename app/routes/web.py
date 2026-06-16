from flask import Blueprint, render_template, abort
from datetime import datetime, timedelta
from app.models import ReleaseNote, Source, AIAnalysis

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
@web_bp.route('/dashboard')
def dashboard():
    """
    Renders the main dashboard containing overall metrics and lists of changes.
    """
    sources = Source.query.all()
    
    # Calculate overview stats
    total_updates = ReleaseNote.query.count()
    critical_updates = ReleaseNote.query.join(AIAnalysis).filter(AIAnalysis.severity == 'Critical').count()
    
    # New updates in past 7 days
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    new_this_week = ReleaseNote.query.filter(ReleaseNote.published_date >= one_week_ago).count()
    
    sources_monitored = Source.query.filter_by(is_active=True).count()
    
    return render_template(
        'dashboard.html',
        sources=sources,
        total_updates=total_updates,
        critical_updates=critical_updates,
        new_this_week=new_this_week,
        sources_monitored=sources_monitored
    )

@web_bp.route('/release/<int:release_id>')
def detail(release_id):
    """
    Renders details of a specific cloud update and its AI analytical breakdown.
    """
    note = ReleaseNote.query.get_or_404(release_id)
    return render_template('detail.html', release=note)

@web_bp.route('/analytics')
def analytics():
    """
    Renders the Trend Analytics visualization page.
    """
    return render_template('analytics.html')

@web_bp.route('/settings')
def settings():
    """
    Renders settings page for managing RSS source ingestion feeds and Slack/email alerts.
    """
    return render_template('settings.html')

@web_bp.route('/search')
def search_page():
    """
    Renders the AI-powered search interface page.
    """
    return render_template('search.html')
