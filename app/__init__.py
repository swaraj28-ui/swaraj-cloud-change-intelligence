import os
from flask import Flask
from app.config import Config
from app.database import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Database
    db.init_app(app)
    
    # Register blueprints
    from app.routes.web import web_bp
    from app.routes.api import api_bp
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    
    # Initialize background scheduler (only in production or main thread to avoid duplicates in reloader)
    if not app.testing and os.environ.get('DISABLE_SCHEDULER') != 'true':
        if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            init_scheduler(app)

        
    return app

def init_scheduler(app):
    from apscheduler.schedulers.background import BackgroundScheduler
    from app.services.feed_service import sync_feeds
    
    scheduler = BackgroundScheduler()
    # Run feed aggregation and analysis job hourly
    scheduler.add_job(
        func=lambda: sync_feeds(app),
        trigger="interval",
        hours=1,
        id="sync_feeds_job",
        replace_existing=True
    )
    
    # Run once at startup to populate initial data in background
    scheduler.add_job(
        func=lambda: sync_feeds(app),
        trigger="date",
        id="initial_sync_job"
    )
    
    scheduler.start()
    app.logger.info("Background scheduler started successfully.")
