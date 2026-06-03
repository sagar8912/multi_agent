import urllib.request
import json
import time

companies = [
    {"company_name": "Microsoft", "domain": "microsoft.com", "country": "USA", "revenue_band": "> $1B", "industry": "Technology"},
    {"company_name": "Apple", "domain": "apple.com", "country": "USA", "revenue_band": "> $1B", "industry": "Technology"},
    {"company_name": "OpenAI", "domain": "openai.com", "country": "USA", "revenue_band": "Unknown", "industry": "Artificial Intelligence"},
    {"company_name": "Example", "domain": "example.com", "country": "USA", "revenue_band": "Unknown", "industry": "Other"},
    {"company_name": "Fake", "domain": "abcxyznotreal12345.com", "country": "USA", "revenue_band": "Unknown", "industry": "Other"}
]

for c in companies:
    print(f"\nTesting {c['domain']}...")
    try:
        req = urllib.request.Request('http://127.0.0.1:8000/analyze-company', data=json.dumps(c).encode('utf-8'), headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req, timeout=120)
        res = json.loads(response.read())
        print(f"Category: {res['overall_risk_category']}, Score: {res['overall_score']}, Evidence: {res['evidence_quality']}, Manual Review: {res['manual_review_required']}")
        
        # print specific e-commerce score for Apple
        if c['domain'] == 'apple.com':
            for m in res['modifiers']:
                if m['modifier_name'] == 'E-Commerce Presence':
                    print(f"  Apple E-Commerce Risk: {m['risk_category']} (Score {m['score']})")
                    
    except Exception as e:
        print(f"Error fetching {c['domain']}: {e}")
