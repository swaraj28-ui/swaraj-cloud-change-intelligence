import os
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from app.models import NotificationRule

def dispatch_notifications(note, analysis):
    """
    Evaluates active notification rules and dispatches alerts accordingly.
    """
    try:
        active_rules = NotificationRule.query.filter_by(is_active=True).all()
        for rule in active_rules:
            should_alert = False
            
            # Check condition type
            if rule.condition_type == 'impact_score':
                try:
                    threshold = int(rule.condition_value)
                    if analysis.impact_score >= threshold:
                        should_alert = True
                except ValueError:
                    pass
            elif rule.condition_type == 'category':
                if rule.condition_value.lower() == analysis.category.lower():
                    should_alert = True
            elif rule.condition_type == 'severity':
                if rule.condition_value.lower() == analysis.severity.lower():
                    should_alert = True
            
            if should_alert:
                if rule.delivery_channel == 'slack':
                    send_slack_notification(rule.recipient, note, analysis)
                elif rule.delivery_channel == 'email':
                    send_email_notification(rule.recipient, note, analysis)
    except Exception as e:
        print(f"Notification dispatch general error: {e}")

def send_slack_notification(webhook_url, note, analysis):
    """
    Formulates a formatted rich attachments block and posts to the Slack webhook.
    """
    color_map = {
        "Critical": "#E02424", # Red
        "High": "#F97316",     # Orange
        "Medium": "#EAB308",   # Yellow
        "Low": "#10B981"       # Green
    }
    color = color_map.get(analysis.severity, "#6B7280")
    
    payload = {
        "text": f"🚨 *Cloud Update Alert ({analysis.severity})*",
        "attachments": [
            {
                "color": color,
                "title": note.title,
                "title_link": note.link,
                "text": f"*Category:* {analysis.category} | *Impact:* {analysis.impact_score}/10\n\n*Summary:*\n{analysis.executive_summary}\n\n*Action:*\n{analysis.recommended_action}",
                "fields": [
                    {
                        "title": "Why It Matters",
                        "value": analysis.why_it_matters,
                        "short": False
                    }
                ],
                "footer": "Cloud Change Intelligence API",
                "ts": int(datetime.utcnow().timestamp())
            }
        ]
    }
    
    try:
        # Only issue POST if URL appears valid (not default placeholder)
        if "hooks.slack.com" in webhook_url:
            response = requests.post(webhook_url, json=payload, timeout=5)
            response.raise_for_status()
            print(f"Slack webhook alert dispatched successfully.")
        else:
            print(f"[SLACK ALERT (MOCK)] Webhook target: {webhook_url}\nPayload: {payload}")
    except Exception as e:
        print(f"Slack delivery failed: {e}")

def send_email_notification(recipient, note, analysis):
    """
    Constructs and dispatches email alert via SMTP or logs the output.
    """
    subject = f"[CCI Alert] {analysis.severity} Update: {note.title}"
    body = f"""
Cloud Change Intelligence Alert
================================
Severity: {analysis.severity}
Impact Score: {analysis.impact_score}/10
Category: {analysis.category}
Source: {note.source.name if note.source else 'Unknown'}

Title: {note.title}
Link: {note.link}

Executive Summary:
------------------
{analysis.executive_summary}

Why This Matters:
-----------------
{analysis.why_it_matters}

Recommended Action:
-------------------
{analysis.recommended_action}

--------------------------------
This is an automated notification from Cloud Change Intelligence.
"""
    smtp_server = os.environ.get('EMAIL_SMTP_SERVER')
    smtp_port = int(os.environ.get('EMAIL_SMTP_PORT', 587))
    sender = os.environ.get('EMAIL_SENDER')
    password = os.environ.get('EMAIL_PASSWORD')
    
    if smtp_server and sender and password:
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = recipient
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, [recipient], msg.as_string())
            print(f"SMTP email notification dispatched to {recipient}")
        except Exception as e:
            print(f"SMTP email delivery failed: {e}")
    else:
        print(f"[EMAIL ALERT (MOCK)] To: {recipient} | Subject: {subject}\n{body}")
