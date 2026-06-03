import os

fixes = {
    "cyber_risk_tool/schemas/output_models.py": """\
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Evidence(BaseModel):
    url: Optional[str] = None
    description: str
    source_type: str = "web"
    status_code: Optional[int] = None

class ModifierResult(BaseModel):
    modifier_name: str
    score: float
    risk_category: str
    confidence: float
    findings: List[str]
    evidence: List[Evidence]
    verification_status: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    recommendation: Optional[str] = None

class CyberRiskReport(BaseModel):
    company_name: str
    domain: str
    country: str
    revenue_band: str
    industry: Optional[str]
    overall_score: float
    overall_risk_category: str
    overall_confidence: float
    modifiers: List[ModifierResult]
    underwriter_summary: str
    generated_at: datetime
""",

    "cyber_risk_tool/agents/research/domain_agent.py": """\
import httpx
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import normalize_domain, build_url

class DomainAgent:
    async def run(self, company: CompanyInput) -> ModifierResult:
        domain = normalize_domain(company.domain)
        https_url = build_url(domain, "https")
        http_url = build_url(domain, "http")
        
        evidence = []
        findings = []
        score = 3.0
        risk_category = "Unknown"
        confidence = 0.2
        
        try:
            async with httpx.AsyncClient(verify=True, follow_redirects=False, timeout=10) as client:
                try:
                    resp_https = await client.get(https_url)
                    https_works = (resp_https.status_code < 400)
                    evidence.append(Evidence(url=https_url, description="HTTPS works", status_code=resp_https.status_code))
                except Exception as e:
                    https_works = False
                    evidence.append(Evidence(url=https_url, description=f"HTTPS failed: {e}", status_code=None))
                
                try:
                    resp_http = await client.get(http_url)
                    http_works = (resp_http.status_code < 400)
                    redirects_to_https = (resp_http.status_code in (301, 302, 307, 308) and "https" in resp_http.headers.get("location", ""))
                    evidence.append(Evidence(url=http_url, description=f"HTTP works, redirect: {redirects_to_https}", status_code=resp_http.status_code))
                except Exception as e:
                    http_works = False
                    redirects_to_https = False
                    evidence.append(Evidence(url=http_url, description=f"HTTP failed: {e}", status_code=None))

            if https_works and redirects_to_https:
                score = 1.0
                risk_category = "Favorable"
                confidence = 0.9
                findings.append("Valid HTTPS and HTTP redirects to HTTPS.")
            elif https_works and not redirects_to_https:
                score = 2.0
                risk_category = "Average"
                confidence = 0.8
                findings.append("HTTPS works, but HTTP does not redirect.")
            elif not https_works and http_works:
                score = 4.0
                risk_category = "Unfavorable"
                confidence = 0.8
                findings.append("HTTPS fails but HTTP works (insecure).")
            else:
                score = 3.0
                risk_category = "Unknown"
                confidence = 0.2
                findings.append("Website appears unavailable.")
                
        except Exception as e:
            findings.append(f"Error during domain check: {e}")
            score = 3.0
            risk_category = "Unknown"
            confidence = 0.2
            
        return ModifierResult(
            modifier_name="Domain Encryption",
            score=score,
            risk_category=risk_category,
            confidence=confidence,
            findings=findings,
            evidence=evidence,
            recommendation="Maintain HTTPS and ensure all HTTP traffic redirects to HTTPS."
        )
""",

    "cyber_risk_tool/agents/research/privacy_agent.py": """\
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import build_url, fetch_url, extract_text_from_html, extract_links
from utils.text_utils import find_keywords
import asyncio

class PrivacyAgent:
    def __init__(self):
        self.privacy_paths = [
            "/privacy", "/privacy-policy", "/privacy-notice", 
            "/legal/privacy", "/privacy.html"
        ]
        self.compliance_terms = [
            "GDPR", "CCPA", "HIPAA", "SOC 2", "ISO 27001",
            "data subject rights", "DPO", "cookie policy", 
            "personal data", "privacy notice"
        ]

    async def run(self, company: CompanyInput) -> ModifierResult:
        domain = company.domain
        base_url = build_url(domain)
        
        findings = []
        evidence = []
        found_policy = False
        compliance_found = []
        
        async def check_url(url):
            html, status, final_url = await fetch_url(url)
            if html and status and status < 400:
                text = extract_text_from_html(html)
                if "privacy" in text.lower() or "policy" in text.lower():
                    terms = find_keywords(text, self.compliance_terms)
                    return final_url or url, status, terms
            return None, status, None

        urls_to_check = [f"{base_url}{path}" for path in self.privacy_paths]
        
        html, status, final_url = await fetch_url(base_url)
        if html:
            links = extract_links(html, base_url)
            for link in links:
                l_lower = link.lower()
                if "privacy" in l_lower or "policy" in l_lower or "legal" in l_lower:
                    if link not in urls_to_check and len(urls_to_check) < 15:
                        urls_to_check.append(link)

        tasks = [check_url(url) for url in urls_to_check]
        results = await asyncio.gather(*tasks)
        
        for url, status, terms in results:
            if url:
                found_policy = True
                compliance_found.extend(terms)
                evidence.append(Evidence(url=url, description="Privacy policy found", status_code=status))
                break
                
        compliance_found = list(set(compliance_found))
        
        all_failed = all(status is None for _, status, _ in results)
        
        if all_failed:
            score = 3.0
            risk_category = "Unknown"
            confidence = 0.2
            findings.append("Site unavailable, could not evaluate privacy regulation.")
        elif found_policy and len(compliance_found) > 0:
            score = 1.0
            risk_category = "Favorable"
            confidence = 0.9
            findings.append(f"Privacy policy found with compliance terms: {', '.join(compliance_found)}")
        elif found_policy:
            score = 2.0
            risk_category = "Average"
            confidence = 0.8
            findings.append("Privacy policy found but few compliance terms identified.")
        else:
            score = 3.0
            risk_category = "Partially Unfavorable"
            confidence = 0.5
            findings.append("No clear privacy policy found at common paths.")
            
        return ModifierResult(
            modifier_name="Privacy Regulation",
            score=score,
            risk_category=risk_category,
            confidence=confidence,
            findings=findings,
            evidence=evidence,
            recommendation="Publish and maintain a clear privacy policy with GDPR/CCPA references where applicable."
        )
""",

    "cyber_risk_tool/agents/research/ecommerce_agent.py": """\
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import fetch_homepage, extract_text_from_html
from utils.text_utils import find_keywords

class EcommerceAgent:
    def __init__(self):
        self.ecommerce_keywords = [
            "cart", "checkout", "payment", "buy now", "add to cart",
            "order", "billing", "subscription", "pricing", 
            "login", "sign up", "account", "customer portal"
        ]
        
    async def run(self, company: CompanyInput) -> ModifierResult:
        html, status, final_url = await fetch_homepage(company.domain)
        
        evidence = []
        findings = []
        
        if not html:
            return ModifierResult(
                modifier_name="E-Commerce Presence",
                score=3.0,
                risk_category="Unknown",
                confidence=0.2,
                findings=["Site unavailable, could not evaluate e-commerce presence."],
                evidence=[],
                recommendation="Review customer data collection and payment security controls."
            )
            
        evidence.append(Evidence(url=final_url, description="Homepage analyzed for e-commerce signals", status_code=status))
        text = extract_text_from_html(html)
        found_keywords = find_keywords(text, self.ecommerce_keywords)
        
        strong_signals = [k for k in found_keywords if k in ["cart", "checkout", "payment", "buy now", "add to cart"]]
        med_signals = [k for k in found_keywords if k in ["pricing", "subscription", "login", "sign up", "account", "billing"]]
        
        if len(strong_signals) > 0 and len(med_signals) > 0:
            score = 4.0
            risk_category = "Unfavorable"
            findings.append(f"Strong e-commerce and account signals found: {', '.join(strong_signals + med_signals)}")
        elif len(strong_signals) > 0:
            score = 3.0
            risk_category = "Partially Unfavorable"
            findings.append(f"E-commerce transaction signals found: {', '.join(strong_signals)}")
        elif len(med_signals) > 0:
            score = 2.0
            risk_category = "Average"
            findings.append(f"Pricing/subscription/account signals found: {', '.join(med_signals)}")
        else:
            score = 1.0
            risk_category = "Favorable"
            findings.append("No active e-commerce or account signals found.")
            
        return ModifierResult(
            modifier_name="E-Commerce Presence",
            score=score,
            risk_category=risk_category,
            confidence=0.8,
            findings=findings,
            evidence=evidence,
            recommendation="Review customer data collection and payment security controls."
        )
""",

    "cyber_risk_tool/agents/research/customer_type_agent.py": """\
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import fetch_homepage, extract_text_from_html
from utils.text_utils import find_keywords

class CustomerTypeAgent:
    def __init__(self):
        self.b2b_keywords = [
            "enterprise", "business", "companies", "organizations",
            "teams", "platform", "solutions", "demo", "contact sales",
            "partners", "clients"
        ]
        self.b2c_keywords = [
            "consumers", "customers", "shop", "buy", "personal",
            "individual", "retail", "family", "home users"
        ]
        
    async def run(self, company: CompanyInput) -> ModifierResult:
        html, status, final_url = await fetch_homepage(company.domain)
        
        if not html:
            return ModifierResult(
                modifier_name="Customer Type",
                score=3.0,
                risk_category="Unknown",
                confidence=0.2,
                findings=["Site unavailable, defaulting to Unknown."],
                evidence=[],
                recommendation="Validate customer profile through annual reports or product pages."
            )
            
        text = extract_text_from_html(html)
        b2b_found = find_keywords(text, self.b2b_keywords)
        b2c_found = find_keywords(text, self.b2c_keywords)
        
        b2b_count = len(b2b_found)
        b2c_count = len(b2c_found)
        
        evidence = [Evidence(url=final_url, description="Analyzed homepage text for B2B/B2C keywords", status_code=status)]
        
        if b2b_count > 0 and b2c_count == 0:
            ctype = "B2B"
            score = 1.0
            risk_category = "Favorable"
            findings = [f"B2B signals strongly present: {', '.join(b2b_found)}"]
        elif b2c_count > 0 and b2b_count == 0:
            ctype = "B2C"
            score = 3.0
            risk_category = "Partially Unfavorable"
            findings = [f"B2C signals strongly present: {', '.join(b2c_found)}"]
        elif b2b_count > 0 and b2c_count > 0:
            ctype = "Mixed"
            score = 2.0
            risk_category = "Average"
            findings = [f"Mixed signals found. B2B: {', '.join(b2b_found)}. B2C: {', '.join(b2c_found)}"]
        else:
            ctype = "Unknown"
            score = 2.0
            risk_category = "Average"
            findings = ["No clear B2B or B2C signals found."]
            
        return ModifierResult(
            modifier_name="Customer Type",
            score=score,
            risk_category=risk_category,
            confidence=0.8 if ctype != "Unknown" else 0.4,
            findings=findings,
            evidence=evidence,
            raw_data={"inferred_type": ctype},
            recommendation="Validate customer profile through annual reports or product pages."
        )
""",

    "cyber_risk_tool/agents/research/geo_agent.py": """\
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import fetch_homepage, extract_text_from_html
from utils.text_utils import find_keywords

class GeoAgent:
    def __init__(self):
        self.countries = [
            "USA", "United States", "India", "UK", "United Kingdom",
            "Canada", "Germany", "France", "Australia", "Singapore",
            "Japan", "China", "Brazil", "Mexico", "UAE"
        ]
        self.global_keywords = [
            "global", "worldwide", "offices", "locations", "regions",
            "countries", "international", "presence"
        ]
        
    async def run(self, company: CompanyInput) -> ModifierResult:
        html, status, final_url = await fetch_homepage(company.domain)
        
        if not html:
            return ModifierResult(
                modifier_name="Geographic Spread",
                score=3.0,
                risk_category="Unknown",
                confidence=0.2,
                findings=["Site unavailable, defaulting to Unknown."],
                evidence=[],
                recommendation="Validate global operations using official office/location pages."
            )
            
        text = extract_text_from_html(html)
        found_countries = set(find_keywords(text, self.countries))
        if company.country and company.country in self.countries:
            found_countries.add(company.country)
            
        global_found = find_keywords(text, self.global_keywords)
        
        evidence = [Evidence(url=final_url, description="Analyzed for geo footprint", status_code=status)]
        findings = []
        
        num_countries = len(found_countries)
        
        if num_countries <= 2 and not global_found:
            score = 1.0
            risk_category = "Favorable"
            findings.append(f"Limited geographic spread ({num_countries} countries).")
        elif (3 <= num_countries <= 5) or global_found:
            score = 2.0
            risk_category = "Average"
            findings.append(f"Moderate geographic spread ({num_countries} countries). Global signals: {', '.join(global_found)}")
        else:
            score = 3.0
            risk_category = "Partially Unfavorable"
            findings.append(f"Wide geographic spread (>5 countries: {', '.join(found_countries)}).")
            
        if company.revenue_band == "> $1B":
            score = max(1.0, score - 1.0)
            findings.append("Severity reduced due to >$1B revenue (expected broader spread).")
            if score == 1.0: risk_category = "Favorable"
            elif score == 2.0: risk_category = "Average"
            
        return ModifierResult(
            modifier_name="Geographic Spread",
            score=score,
            risk_category=risk_category,
            confidence=0.8,
            findings=findings,
            evidence=evidence,
            recommendation="Validate global operations using official office/location pages."
        )
""",

    "cyber_risk_tool/agents/underwriter.py": """\
from typing import List
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult

class UnderwriterAgent:
    def generate_summary(self, company: CompanyInput, modifiers: List[ModifierResult], score: float, risk_category: str) -> str:
        fav = [m.modifier_name for m in modifiers if m.risk_category in ("Favorable", "Very Favorable")]
        mod_risk = [m.modifier_name for m in modifiers if m.risk_category == "Average"]
        unfav = [m.modifier_name for m in modifiers if m.risk_category in ("Partially Unfavorable", "Unfavorable")]
        
        review_points = unfav if unfav else (mod_risk if mod_risk else fav)
        
        summary = (
            f"Overall Risk Category: {risk_category}\\n"
            f"Key Favorable Indicators: {', '.join(fav) if fav else 'None'}\\n"
            f"Key Risk Indicators: {', '.join(unfav) if unfav else 'None'}\\n"
            f"Recommended Underwriting Review Points: Focus on validating {', '.join(review_points)}."
        )
        return summary
""",

    "cyber_risk_tool/api/routes.py": """\
import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from schemas.input_models import CompanyInput
from schemas.output_models import CyberRiskReport, ModifierResult
from agents.supervisor import SupervisorAgent
from agents.research.domain_agent import DomainAgent
from agents.research.privacy_agent import PrivacyAgent
from agents.research.ecommerce_agent import EcommerceAgent
from agents.research.customer_type_agent import CustomerTypeAgent
from agents.research.geo_agent import GeoAgent
from core.config import load_rules
import asyncio

router = APIRouter()

@router.get("/modifiers")
def get_modifiers():
    rules = load_rules()
    enabled = [m for m, config in rules.items() if config.get("enabled", False)]
    return {"enabled_modifiers": enabled}

@router.post("/analyze-company", response_model=CyberRiskReport)
async def analyze_company(company: CompanyInput):
    supervisor = SupervisorAgent()
    try:
        report = await supervisor.run_analysis(company)
        
        outputs_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company = "".join([c if c.isalnum() else "_" for c in company.company_name]).lower()
        safe_domain = "".join([c if c.isalnum() else "_" for c in company.domain]).lower()
        
        filename = f"{safe_company}_{safe_domain}_{timestamp}.json"
        filepath = os.path.join(outputs_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))
            
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-modifier/{modifier_name}", response_model=ModifierResult)
async def run_modifier(modifier_name: str, company: CompanyInput):
    agents = {
        "domain_encryption": DomainAgent(),
        "privacy_regulation": PrivacyAgent(),
        "ecommerce_presence": EcommerceAgent(),
        "customer_type": CustomerTypeAgent(),
        "geographic_spread": GeoAgent()
    }
    
    if modifier_name not in agents:
        raise HTTPException(status_code=400, detail=f"Modifier {modifier_name} not found.")
        
    agent = agents[modifier_name]
    try:
        result = await agent.run(company)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
def get_reports():
    outputs_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    files = [f for f in os.listdir(outputs_dir) if f.endswith(".json") and f != "sample_report.json"]
    return {"saved_reports": files}

@router.get("/reports/{filename}")
def get_report(filename: str):
    outputs_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    filepath = os.path.join(outputs_dir, filename)
    if not os.path.exists(filepath) or not filename.endswith(".json"):
        raise HTTPException(status_code=404, detail="Report not found")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
""",

    "cyber_risk_tool/tests/test_sample_requests.py": """\
import httpx
import time

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing GET /health...")
    try:
        resp = httpx.get(f"{base_url}/health")
        print(f"Health check: {resp.json()}")
    except Exception as e:
        print(f"API not running or unreachable: {e}. Please start it using 'python run.py'.")
        return

    print("\\nTesting GET /modifiers...")
    try:
        resp = httpx.get(f"{base_url}/modifiers")
        print(f"Modifiers: {resp.json()}")
    except Exception as e:
        print(f"Failed to get modifiers: {e}")

    domains = ["microsoft.com", "apple.com", "example.com"]
    for domain in domains:
        print(f"\\nTesting POST /analyze-company for {domain}...")
        payload = {
            "company_name": domain.split('.')[0].capitalize(),
            "domain": domain,
            "country": "USA",
            "revenue_band": "> $1B",
            "industry": "Technology"
        }
        resp = httpx.post(f"{base_url}/analyze-company", json=payload, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Result for {domain}:")
            print(f"  Overall Score: {data['overall_score']:.2f}")
            print(f"  Risk Category: {data['overall_risk_category']}")
            print(f"  Confidence: {data['overall_confidence']:.2f}")
            print("  Summary:")
            print(data['underwriter_summary'])
            for mod in data['modifiers']:
                print(f"    - {mod['modifier_name']}: {mod['score']} ({mod['risk_category']}) [Verified: {mod['verification_status']}] -> {mod.get('recommendation', '')}")
        else:
            print(f"Error {resp.status_code}: {resp.text}")

    print("\\nTesting GET /reports...")
    try:
        resp = httpx.get(f"{base_url}/reports")
        if resp.status_code == 200:
            reports = resp.json().get("saved_reports", [])
            print(f"Found {len(reports)} saved reports:")
            for r in reports:
                print(f"  - {r}")
        else:
            print(f"Failed to get reports. Status: {resp.status_code}")
    except Exception as e:
        print(f"Failed to get reports: {e}")

if __name__ == "__main__":
    test_api()
""",

    "cyber_risk_tool/README.md": """\
# Agentic AI Cyber Risk Underwriting Intelligence Tool

## 1. Project Overview
This tool is an Agentic AI-based backend built to assist cyber insurance underwriters. It autonomously researches target companies, evaluates predefined risk modifiers, verifies facts, and compiles a comprehensive Cyber Risk Report.

## 2. Why this tool is being built
Manual underwriting research is time-consuming and inconsistent. This tool accelerates the process, standardizes the scoring based on verifiable evidence, and produces underwriter-friendly summaries.

## 3. Agentic Workflow
Company Input -> Supervisor Agent -> Research Agents -> Fact Checker Agent -> Underwriter Agent -> Scoring Engine -> JSON Report.

## 4. MVP Modifiers
- Domain Encryption
- Privacy Regulation
- E-Commerce Presence
- Customer Type
- Geographic Spread

## 5. Folder Structure
```text
cyber_risk_tool/
├── api/          # FastAPI routes and main app
├── agents/       # AI agents (Supervisor, Research, FactChecker, Underwriter)
├── core/         # Config and Scoring logic
├── schemas/      # Pydantic models for Input/Output
├── rules/        # YAML configuration for modifiers
├── utils/        # Web scraping and text processing utilities
├── tests/        # API tests
├── outputs/      # Saved JSON reports
└── ...
```

## 6. Setup Commands
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

## 7. Demo Steps
1. **Start server:** `python run.py` (or `uvicorn api.main:app --reload`)
2. **Open Swagger UI:** Navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
3. **Run /health:** Test if the API is up.
4. **Run /modifiers:** Ensure the rules engine is correctly loaded.
5. **Run /analyze-company:** Submit a company profile to generate a full cyber risk report.
6. **View saved reports:** Use the `GET /reports` endpoint to view dynamically saved JSON reports.

## 8. Sample Commands
**Curl:**
```bash
curl -X 'POST' \\
  'http://127.0.0.1:8000/analyze-company' \\
  -H 'accept: application/json' \\
  -H 'Content-Type: application/json' \\
  -d '{
  "company_name": "Microsoft",
  "domain": "microsoft.com",
  "country": "USA",
  "revenue_band": "> $1B",
  "industry": "Technology"
}'
```

**PowerShell:**
```powershell
$body = @{
    company_name = "Microsoft"
    domain = "microsoft.com"
    country = "USA"
    revenue_band = "> `$1B"
    industry = "Technology"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/analyze-company" -Method Post -ContentType "application/json" -Body $body
```

## 9. How to test
```bash
python -m tests.test_sample_requests
```

## 10. Future enhancements
- Azure OpenAI integration for Underwriter summaries
- LangGraph orchestration
- Dark Web checks and paid API integrations

## 11. Troubleshooting
- If website parsing fails, ensure you have an active internet connection.
- Timeout errors can be resolved by increasing httpx timeout in `utils/scraper.py`.
"""
}

def apply_demo_fixes():
    for filepath, content in fixes.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    apply_demo_fixes()
