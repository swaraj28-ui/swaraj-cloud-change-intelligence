# 🧠 Cloud Change Intelligence (CCI)

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/tests-passed-success.svg)](tests/)

An enterprise-ready, AI-augmented cloud provider release note aggregator, semantic search, and notification alerting engine. CCI continuously aggregates and translates platform updates across cloud systems into actionable engineering summaries before they impact production workloads.

---

## 📖 Table of Contents
* [Problem Statement](#-problem-statement)
* [Project Overview](#-project-overview)
* [Core Features](#-core-features)
* [Architecture & Tech Stack](#-architecture--tech-stack)
* [Installation & Setup](#-installation--setup)
* [Environment Configuration](#-environment-configuration)
* [Running Locally](#-running-locally)
* [Screenshots & UI Walkthrough](#-screenshots--ui-walkthrough)
* [Future Improvements](#-future-improvements)

---

## 🚨 Problem Statement
Engineering teams struggle to keep pace with the hundreds of cloud provider updates released monthly across services like BigQuery, Vertex AI, GKE, AWS, and Azure. High-priority updates—such as critical API deprecations, breaking billing model adjustments, or high-urgency security vulnerabilities—often go unnoticed in unified RSS streams. This causes silent build pipeline breaks, unexpected cloud bills, or exposed attack vectors.

## 💡 Project Overview
**Cloud Change Intelligence (CCI)** solves this by building an automated, AI-driven aggregation pipeline. The tool fetches, parses, and logs raw release notes from cloud providers. Using Google's Gemini API, it summarizes descriptions, categorizes updates, scores their urgency, outlines mitigation procedures, and evaluates developer risk. The system then displays updates on a responsive dark-themed dashboard, enables natural-language semantic searches, and routes critical updates to Slack or email.

---

## ✨ Core Features

### 1. Multi-Source Ingestion & Deduplication
* Continuous ingestion from RSS/Atom XML feeds including Google Cloud Platform, BigQuery, Vertex AI, and Cloud Run release feeds.
* High-performance database hashing to prevent duplicate note ingestion.

### 2. AI-Augmented Analytics (Gemini API)
* **Executive Summary:** Generates concise 1-2 sentence descriptions of complex technical changes.
* **Smart Categorization:** Automatically maps updates to tags such as `Security`, `Deprecation`, `Breaking Change`, `Cost Optimization`, `AI/ML`, `Data Engineering`, and `Infrastructure`.
* **Heuristics Fallback:** Works fully out of the box. If no Gemini API Key is configured, the system uses a regex-driven local heuristic engine.

### 3. Impact Detection Engine
* Calculates operational risk scoring (1-10) using Gemini and deterministic keyword weights.
* Bumps scores if keywords like `vulnerability`, `deprecated`, `removal`, or `breaking change` are matched.
* Formats clear visual severity badges: `Low`, `Medium`, `High`, and `Critical`.

### 4. Interactive Dashboard
* Sleek responsive dark-mode SaaS UI with flex grids.
* Filters by Cloud Feed, Category Class, and Severity.
* Client-side search for instant results and server-side sorting (by date or impact score).

### 5. AI Semantic Search
* Supports natural conversational English search terms (e.g., *"Which updates impact data pipelines?"* or *"Tell me about Vertex AI cost optimizations"*).
* Resolves intent semantically using Gemini or falls back to an prioritized keyword ranking engine.

### 6. Alert Routing & Notifications
* Allows custom notification trigger parameters (e.g., *Impact Score >= 8*, *Category = Security*, or *Severity = Critical*).
* Dispatches formatted rich Slack block notifications or secure SMTP emails.

### 7. Social Content Generator
* Instantly drafts developer blog summaries, LinkedIn posts, and Twitter/X updates for any release note to aid internal developer relations or engineering alignment.

---

## 🏗️ Architecture & Tech Stack

The application employs a modular, domain-driven service architecture structured via Flask Blueprints:

```text
swaraj-cloud-change-intelligence/
├── app/
│   ├── __init__.py          # Flask app instantiation & scheduler bootstrapper
│   ├── config.py            # Environment configurations loader
│   ├── models.py            # SQLAlchemy schema models definitions
│   ├── database.py          # SQLAlchemy session setup
│   ├── routes/
│   │   ├── api.py           # REST endpoints (JSON API services)
│   │   └── web.py           # Server-side HTML template routers
│   ├── services/
│   │   ├── feed_service.py  # RSS aggregator fetch & deduplication logic
│   │   ├── ai_service.py    # Gemini API wrapper & heuristics classifier
│   │   ├── impact_engine.py # Severity rank scoring modifiers
│   │   └── notification.py  # Slack incoming webhook & SMTP email alerts
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css   # Custom CSS theme Variables & Layout
│   │   └── js/
│   │       ├── dashboard.js  # Live filters dashboard controller
│   │       ├── detail.js     # Detail page actions & social draft tabs
│   │       ├── search.js     # Semantic search panel interface
│   │       └── analytics.js  # Chart.js visualization charts
│   └── templates/
│       ├── base.html        # Shell shell layout
│       ├── dashboard.html   # Main feed metrics page
│       ├── detail.html      # Specific release note detail analysis page
│       ├── analytics.html   # Charts statistics dashboard
│       ├── search.html      # Conversational search view
│       └── settings.html    # Feeds config & notification routing rules
├── tests/
│   ├── test_feed.py         # SQLAlchemy unit tests
│   ├── test_ai.py           # Heuristics classifiers unit tests
│   └── test_impact.py       # Severity boundary unit tests
```

### Backend Tech Stack
* **Language:** Python 3.12+
* **Framework:** Flask
* **Database ORM:** SQLAlchemy (SQLite fallback / PostgreSQL support)
* **Background Runner:** APScheduler (triggers hourly feed runs)
* **Feed Parser:** Feedparser

### Frontend Tech Stack
* **Design system:** Pure Vanilla CSS (Variables, HSL palettes, Responsive grids)
* **Scripting:** Pure Vanilla JavaScript (Fetch API, DOM injection)
* **Charts:** Chart.js

---

## 🛠️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/swaraj-cloud-change-intelligence.git
cd swaraj-cloud-change-intelligence
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy the example template file to create `.env`:
```bash
cp .env.example .env
```

---

## 🔒 Environment Configuration

Edit your local `.env` file to customize parameters:

| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `SECRET_KEY` | No | `dev-secret-key-1293847` | Salt used by Flask for cookie signing. |
| `DATABASE_URL` | No | SQLite file | DB Connection string (e.g. `postgresql://...`). |
| `GEMINI_API_KEY` | No | `None` | API Key from Google AI Studio. |
| `SLACK_WEBHOOK_URL` | No | `None` | Webhook URL for real-time Slack notifications. |
| `EMAIL_SMTP_SERVER` | No | `None` | SMTP Host (e.g., `smtp.gmail.com`). |
| `EMAIL_SMTP_PORT` | No | `587` | SMTP outgoing port. |
| `EMAIL_SENDER` | No | `None` | Sending email account address. |
| `EMAIL_PASSWORD` | No | `None` | App-specific password for SMTP login. |

> [!NOTE]
> If `GEMINI_API_KEY` is empty, the system runs with local heuristic classifiers.

---

## 💻 Running Locally

### 1. Database Migrations & Seeding
Prepare your database tables and seed mock updates for an immediate visualization:
```bash
python setup_db.py
```

### 2. Execute Tests
Validate code components using pytest:
```bash
python -m pytest
```

### 3. Run Server
Launch the Flask server:
```bash
python run.py
```
Open **[http://localhost:5000](http://localhost:5000)** in your browser.

---

## 🖼️ Screenshots & UI Walkthrough

The following sections illustrate the user interface layout:

### 1. Unified Dashboard
A complete overview of aggregated updates showing cards for total notifications, critical warnings, and weekly volume statistics. It contains dynamic filters and an interactive status table.

### 2. Analytical Intelligence Page
A detailed page splitting raw provider documentation alongside executive summaries, recommendations, "Why this matters" blocks, and the social post generator.

### 3. Chart Analytics Dashboard
Real-time Chart.js graphs mapping ingestion frequencies, service volumes, and category classification percentages.

### 4. Alerting & Routing Rules
Settings to configure custom notification triggers (Slack Webhooks or email alerts) and toggle live RSS links.

---

## 🚀 Future Improvements
* **Provider Expansion:** Add support for AWS RSS updates feeds and Azure Service Health alerts.
* **OAuth Authentication:** Protect configuration and dashboard settings with corporate Google/GitHub OAuth logins.
* **Email Template Customization:** Build responsive HTML templates for email alerts.
* **Advanced Vector Embeddings:** Integrate vector indexing (like PGVector) for high-performance offline semantic matching.
