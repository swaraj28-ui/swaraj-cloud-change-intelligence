from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import threading
from app.database import db
from app.models import ReleaseNote, AIAnalysis, Source, NotificationRule
from app.services.feed_service import sync_feeds
from app.services.ai_service import analyze_release_note, generate_social_posts, semantic_search_releases
from app.services.impact_engine import calculate_impact

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/releases', methods=['GET'])
def get_releases():
    """
    Fetches filtered, sorted release notes.
    Params: source_id, category, severity, sort_by (date or impact_score), order (asc or desc)
    """
    source_id = request.args.get('source_id')
    category = request.args.get('category')
    severity = request.args.get('severity')
    sort_by = request.args.get('sort_by', 'date')
    order = request.args.get('order', 'desc')
    
    # We join with AIAnalysis to guarantee analysis details are loaded and enable filtering/sorting on those keys
    query = ReleaseNote.query.join(AIAnalysis)
    
    if source_id:
        query = query.filter(ReleaseNote.source_id == source_id)
    if category:
        query = query.filter(AIAnalysis.category == category)
    if severity:
        query = query.filter(AIAnalysis.severity == severity)
        
    if sort_by == 'impact_score':
        if order == 'asc':
            query = query.order_by(AIAnalysis.impact_score.asc(), ReleaseNote.published_date.desc())
        else:
            query = query.order_by(AIAnalysis.impact_score.desc(), ReleaseNote.published_date.desc())
    else: # default by date
        if order == 'asc':
            query = query.order_by(ReleaseNote.published_date.asc())
        else:
            query = query.order_by(ReleaseNote.published_date.desc())
            
    releases = query.all()
    return jsonify([r.to_dict() for r in releases])

@api_bp.route('/releases/<int:release_id>', methods=['GET'])
def get_release(release_id):
    """
    Gets details of a single release note.
    """
    note = ReleaseNote.query.get_or_404(release_id)
    return jsonify(note.to_dict())

@api_bp.route('/search', methods=['GET'])
def search_releases():
    """
    Handles natural language queries using AI semantic search or keyword search fallbacks.
    """
    query_text = request.args.get('q', '').strip()
    if not query_text:
        return jsonify([])
        
    all_notes = ReleaseNote.query.join(AIAnalysis).all()
    results = semantic_search_releases(query_text, all_notes)
    return jsonify([r.to_dict() for r in results])

@api_bp.route('/analyze', methods=['POST'])
def trigger_analysis():
    """
    Triggers manual re-analysis of an existing release note.
    """
    data = request.json or {}
    release_id = data.get('release_id')
    if not release_id:
        return jsonify({"error": "Missing release_id param"}), 400
        
    note = ReleaseNote.query.get_or_404(release_id)
    
    try:
        analysis_data = analyze_release_note(note)
        analysis_data = calculate_impact(note, analysis_data)
        
        # Locate or initialize analysis record
        analysis = AIAnalysis.query.filter_by(release_note_id=note.id).first()
        if not analysis:
            analysis = AIAnalysis(release_note_id=note.id)
            db.session.add(analysis)
            
        analysis.executive_summary = analysis_data.get('executive_summary', '')
        analysis.category = analysis_data.get('category', 'Infrastructure')
        analysis.impact_score = analysis_data.get('impact_score', 5)
        analysis.recommended_action = analysis_data.get('recommended_action', '')
        analysis.risk_level = analysis_data.get('risk_level', 'Low')
        analysis.why_it_matters = analysis_data.get('why_it_matters', '')
        analysis.severity = analysis_data.get('severity', 'Low')
        analysis.analyzed_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({"success": True, "analysis": analysis.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/generate-post', methods=['POST'])
def generate_social_content():
    """
    Generates tailored social posts for selected releases.
    """
    data = request.json or {}
    release_id = data.get('release_id')
    if not release_id:
        return jsonify({"error": "Missing release_id param"}), 400
        
    note = ReleaseNote.query.get_or_404(release_id)
    if not note.ai_analysis:
        return jsonify({"error": "This release note has not been analyzed yet."}), 400
        
    try:
        posts = generate_social_posts(
            note.title,
            note.ai_analysis.executive_summary,
            note.ai_analysis.recommended_action
        )
        return jsonify(posts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/refresh', methods=['POST'])
def trigger_refresh():
    """
    Triggers an asynchronous feed pull and analysis sync execution.
    """
    app = current_app._get_current_object()
    
    # Run sync in background thread
    thread = threading.Thread(target=sync_feeds, args=(app,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "success": True,
        "message": "Feed synchronization has been triggered in the background."
    })

@api_bp.route('/settings/sources', methods=['GET', 'POST'])
def manage_sources():
    """
    Retrieves sources or adds/edits a source.
    """
    if request.method == 'GET':
        sources = Source.query.all()
        return jsonify([s.to_dict() for s in sources])
        
    data = request.json or {}
    source_id = data.get('id')
    
    if source_id:
        # Edit existing source
        source = Source.query.get_or_404(source_id)
        if 'is_active' in data:
            source.is_active = bool(data['is_active'])
        if 'name' in data:
            source.name = data['name']
        if 'feed_url' in data:
            source.feed_url = data['feed_url']
        db.session.commit()
        return jsonify({"success": True, "source": source.to_dict()})
        
    # Add new source
    name = data.get('name')
    feed_url = data.get('feed_url')
    if not name or not feed_url:
        return jsonify({"error": "Missing name or feed_url fields"}), 400
        
    source = Source(name=name, feed_url=feed_url, is_active=True)
    db.session.add(source)
    db.session.commit()
    return jsonify({"success": True, "source": source.to_dict()})

@api_bp.route('/settings/sources/<int:source_id>', methods=['DELETE'])
def delete_source(source_id):
    """
    Removes a source configuration.
    """
    source = Source.query.get_or_404(source_id)
    db.session.delete(source)
    db.session.commit()
    return jsonify({"success": True, "message": "Source removed successfully"})

@api_bp.route('/settings/notifications', methods=['GET', 'POST'])
def manage_notifications():
    """
    Retrieves notification rules or adds/updates rules.
    """
    if request.method == 'GET':
        rules = NotificationRule.query.all()
        return jsonify([r.to_dict() for r in rules])
        
    data = request.json or {}
    rule_id = data.get('id')
    
    if rule_id:
        # Edit existing rule
        rule = NotificationRule.query.get_or_404(rule_id)
        if 'is_active' in data:
            rule.is_active = bool(data['is_active'])
        if 'rule_name' in data:
            rule.rule_name = data['rule_name']
        if 'condition_type' in data:
            rule.condition_type = data['condition_type']
        if 'condition_value' in data:
            rule.condition_value = data['condition_value']
        if 'delivery_channel' in data:
            rule.delivery_channel = data['delivery_channel']
        if 'recipient' in data:
            rule.recipient = data['recipient']
        db.session.commit()
        return jsonify({"success": True, "rule": rule.to_dict()})
        
    # Create new rule
    rule_name = data.get('rule_name')
    condition_type = data.get('condition_type')
    condition_value = data.get('condition_value')
    delivery_channel = data.get('delivery_channel')
    recipient = data.get('recipient')
    
    if not all([rule_name, condition_type, condition_value, delivery_channel, recipient]):
        return jsonify({"error": "Missing configuration details"}), 400
        
    rule = NotificationRule(
        rule_name=rule_name,
        condition_type=condition_type,
        condition_value=condition_value,
        delivery_channel=delivery_channel,
        recipient=recipient,
        is_active=True
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify({"success": True, "rule": rule.to_dict()})

@api_bp.route('/settings/notifications/<int:rule_id>', methods=['DELETE'])
def delete_notification(rule_id):
    """
    Deletes an alert delivery rule.
    """
    rule = NotificationRule.query.get_or_404(rule_id)
    db.session.delete(rule)
    db.session.commit()
    return jsonify({"success": True, "message": "Notification rule deleted successfully"})
