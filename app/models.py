from datetime import datetime
from app.database import db

class Source(db.Model):
    __tablename__ = 'sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    feed_url = db.Column(db.String(255), unique=True, nullable=False)
    last_fetched_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationship: 1 source can have many release notes
    release_notes = db.relationship('ReleaseNote', backref='source', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'feed_url': self.feed_url,
            'last_fetched_at': self.last_fetched_at.isoformat() if self.last_fetched_at else None,
            'is_active': self.is_active
        }

class ReleaseNote(db.Model):
    __tablename__ = 'release_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(512), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    published_date = db.Column(db.DateTime, nullable=False)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship: 1 release note has exactly 1 AI analysis
    ai_analysis = db.relationship('AIAnalysis', backref='release_note', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'source_name': self.source.name if self.source else None,
            'title': self.title,
            'link': self.link,
            'content': self.content,
            'published_date': self.published_date.isoformat(),
            'fetched_at': self.fetched_at.isoformat(),
            'analysis': self.ai_analysis.to_dict() if self.ai_analysis else None
        }

class AIAnalysis(db.Model):
    __tablename__ = 'ai_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    release_note_id = db.Column(db.Integer, db.ForeignKey('release_notes.id', ondelete='CASCADE'), unique=True, nullable=False)
    executive_summary = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., Security, Cost Optimization, breaking change, AI/ML
    impact_score = db.Column(db.Integer, nullable=False)  # 1 to 10
    recommended_action = db.Column(db.Text, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)  # e.g., Low, Medium, High, Critical
    why_it_matters = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False)   # Visual badge representation: Low, Medium, High, Critical
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'release_note_id': self.release_note_id,
            'executive_summary': self.executive_summary,
            'category': self.category,
            'impact_score': self.impact_score,
            'recommended_action': self.recommended_action,
            'risk_level': self.risk_level,
            'why_it_matters': self.why_it_matters,
            'severity': self.severity,
            'analyzed_at': self.analyzed_at.isoformat()
        }

class NotificationRule(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), nullable=False)
    condition_type = db.Column(db.String(50), nullable=False)   # 'impact_score', 'category', 'severity'
    condition_value = db.Column(db.String(100), nullable=False) # e.g. '8', 'Security', 'Critical'
    delivery_channel = db.Column(db.String(20), nullable=False)  # 'email', 'slack'
    recipient = db.Column(db.String(255), nullable=False)        # Webhook URL or Email Address
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'rule_name': self.rule_name,
            'condition_type': self.condition_type,
            'condition_value': self.condition_value,
            'delivery_channel': self.delivery_channel,
            'recipient': self.recipient,
            'is_active': self.is_active
        }

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value
        }
