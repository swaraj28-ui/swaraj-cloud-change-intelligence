import os
import json
import google.generativeai as genai

def analyze_release_note(note):
    """
    Leverages Gemini API to summarize and classify the release note.
    Falls back to a robust heuristic rule engine if the API is offline or missing credentials.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return get_heuristic_analysis(note)
        
    try:
        genai.configure(api_key=api_key)
        # Using Gemini Flash for fast response
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Analyze this cloud service release note and return a raw JSON object with these keys:
        - executive_summary (1-2 sentences summarizing the update)
        - category (MUST be exactly one of: Security, Cost Optimization, AI/ML, Data Engineering, Infrastructure, Deprecation, Breaking Change, Feature Launch, Compliance)
        - impact_score (integer from 1 to 10 measuring the operational urgency/criticality of this change)
        - recommended_action (actionable recommendation for engineers)
        - risk_level (one of: Low, Medium, High, Critical)
        - why_it_matters (why this update requires attention)
        
        Title: {note.title}
        Content: {note.content}
        
        Provide ONLY valid JSON. Do not include markdown code block formatting like ```json.
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Strip potential markdown formatting wrapper
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        return data
        
    except Exception as e:
        # Log error in fallback path
        print(f"Gemini API analysis failed: {e}. Falling back to rule heuristics.")
        return get_heuristic_analysis(note)

def generate_social_posts(title, summary, recommendation):
    """
    Generates promotional/educational social snippets based on the analysis.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Given this cloud release note update:
            Title: {title}
            Summary: {summary}
            Recommendation: {recommendation}
            
            Generate three promotional and educational items and return a JSON object with these keys:
            - twitter_post (max 280 characters with relevant hashtags)
            - linkedin_post (professional summary, 100-200 words, including bullet points)
            - blog_summary (developer blog snippet, 200-300 words, divided into Summary, Impact, and Steps)
            
            Provide ONLY raw JSON. No markdown code blocks.
            """
            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            return json.loads(text)
        except Exception as e:
            print(f"Gemini social post generation failed: {e}. Using fallback.")
            
    # Default fallback
    return {
        "twitter_post": f"📢 Cloud Update: {title} - {summary[:150]}... Read more to stay updated! #CloudDev #DevOps",
        "linkedin_post": f"💡 **Cloud Release Update: {title}**\n\n{summary}\n\n**Recommended Action:** {recommendation}\n\n#CloudEngineering #SoftwareArchitecture #DevOps",
        "blog_summary": f"### {title}\n\n**Summary**\n{summary}\n\n**Technical Impact**\nThis change could impact active cloud instances, pipelines, or authentication mechanisms. Reviewing codebases is recommended.\n\n**Next Steps**\n{recommendation}"
    }

def semantic_search_releases(query, releases):
    """
    Filters and sorts release notes using Gemini semantic matching, falling back to clean keyword ranking.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key and releases:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Package options for the model
            candidates = []
            for r in releases:
                candidates.append({
                    "id": r.id,
                    "title": r.title,
                    "category": r.ai_analysis.category if r.ai_analysis else "Infrastructure",
                    "summary": r.ai_analysis.executive_summary if r.ai_analysis else r.content[:100]
                })
            
            prompt = f"""
            You are a semantic search engine. Match the user query: "{query}" against these cloud release updates.
            Return a JSON array of matching update IDs in order of relevance. If none match, return [].
            
            Release Updates:
            {json.dumps(candidates, indent=2)}
            
            Provide ONLY raw JSON array. No markdown wraps.
            """
            
            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            matched_ids = json.loads(text)
            
            # Map back to models
            id_map = {r.id: r for r in releases}
            return [id_map[rid] for rid in matched_ids if rid in id_map]
            
        except Exception as e:
            print(f"Gemini semantic search failed: {e}. Falling back to keyword engine.")
            
    # Text-based keyword matching fallback
    query_words = [w.lower() for w in query.lower().split() if len(w) > 2]
    if not query_words:
        return releases
        
    scored_releases = []
    for r in releases:
        score = 0
        title_lower = r.title.lower()
        content_lower = r.content.lower()
        cat = r.ai_analysis.category.lower() if r.ai_analysis else "infrastructure"
        
        for word in query_words:
            if word in title_lower:
                score += 10
            if word in cat:
                score += 8
            if word in content_lower:
                score += 2
                
        if score > 0:
            scored_releases.append((score, r))
            
    scored_releases.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_releases]

def get_heuristic_analysis(note):
    """
    Locally parses the release note content to categorize and estimate impact metrics.
    """
    title_lower = note.title.lower()
    content_lower = note.content.lower()
    
    category = "Infrastructure"
    impact_score = 4
    risk_level = "Low"
    
    # Keyword detection rules
    if any(k in title_lower or k in content_lower for k in ["security", "cve-", "vulnerability", "patch", "exploit"]):
        category = "Security"
        impact_score = 9
        risk_level = "Critical"
    elif any(k in title_lower or k in content_lower for k in ["deprecated", "deprecation", "obsolete", "sunset"]):
        category = "Deprecation"
        impact_score = 6
        risk_level = "Medium"
    elif any(k in title_lower or k in content_lower for k in ["breaking change", "breaking", "incompatible", "removal"]):
        category = "Breaking Change"
        impact_score = 8
        risk_level = "High"
    elif any(k in title_lower or k in content_lower for k in ["cost", "billing", "price", "pricing", "charge"]):
        category = "Cost Optimization"
        impact_score = 5
        risk_level = "Low"
    elif any(k in title_lower or k in content_lower for k in ["vertex", "ai", "ml", "gpu", "tpu", "model", "training"]):
        category = "AI/ML"
        impact_score = 5
        risk_level = "Low"
    elif any(k in title_lower or k in content_lower for k in ["bigquery", "spark", "sql", "warehouse", "dataset"]):
        category = "Data Engineering"
        impact_score = 6
        risk_level = "Low"
    elif any(k in title_lower or k in content_lower for k in ["compliance", "soc2", "gdpr", "audit", "security standard"]):
        category = "Compliance"
        impact_score = 5
        risk_level = "Low"
    elif any(k in title_lower or k in content_lower for k in ["launch", "release", "preview", "new feature", "announcing"]):
        category = "Feature Launch"
        impact_score = 3
        risk_level = "Low"

    summary = f"Summarized: {note.title}. This update brings modifications under the {category} category."
    rec_action = f"Review cloud configurations and API hooks associated with {category} changes."
    why_matters = f"This update relates to your {category.lower()} setups. Ensure configurations match provider specifications."
    
    return {
        "executive_summary": summary,
        "category": category,
        "impact_score": impact_score,
        "recommended_action": rec_action,
        "risk_level": risk_level,
        "why_it_matters": why_matters
    }
