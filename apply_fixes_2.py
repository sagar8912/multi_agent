import os

fixes = {
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
        
        # We try concurrent requests to the paths
        async def check_url(url):
            html, status, final_url = await fetch_url(url)
            if html and status and status < 400:
                text = extract_text_from_html(html)
                if "privacy" in text.lower() or "policy" in text.lower():
                    terms = find_keywords(text, self.compliance_terms)
                    return final_url or url, status, terms
            return None, status, None

        urls_to_check = [f"{base_url}{path}" for path in self.privacy_paths]
        
        # Search homepage for additional privacy links
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
            evidence=evidence
        )
""",

    "cyber_risk_tool/agents/fact_checker.py": """\
from typing import List
from schemas.output_models import ModifierResult

class FactCheckerAgent:
    def verify(self, modifiers: List[ModifierResult]) -> List[ModifierResult]:
        for mod in modifiers:
            has_evidence = len(mod.evidence) > 0
            
            if not has_evidence or mod.risk_category == "Unknown":
                mod.verification_status = "not_verified"
                mod.confidence = max(0.1, mod.confidence - 0.2)
            else:
                is_weak = False
                if len(mod.evidence) == 1:
                    url = mod.evidence[0].url
                    # Weak if the evidence URL is just the homepage root
                    if url and url.rstrip('/').count('/') <= 2:
                        # For privacy, the homepage is weak evidence
                        if mod.modifier_name == "Privacy Regulation":
                            is_weak = True
                
                if is_weak:
                    mod.verification_status = "partially_verified"
                else:
                    mod.verification_status = "verified"
                    
        return modifiers
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
        
        sentences = []
        if fav:
            sentences.append(f"The company shows favorable controls in {', '.join(fav)}.")
        if mod_risk:
            sentences.append(f"Moderate risk is observed in {', '.join(mod_risk)}.")
        if unfav:
            sentences.append(f"Unfavorable risk indicators are present in {', '.join(unfav)}.")
            
        if not sentences:
            sentences.append("There is insufficient clear evidence to definitively assess individual risk controls.")
            
        sentences.append(f"Overall risk category is {risk_category}.")
        return " ".join(sentences)
""",

    "cyber_risk_tool/sample_request.json": """\
{
  "company_name": "Microsoft",
  "domain": "microsoft.com",
  "country": "USA",
  "revenue_band": "> $1B",
  "industry": "Technology"
}
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
            print(f"  Summary: {data['underwriter_summary']}")
            for mod in data['modifiers']:
                print(f"    - {mod['modifier_name']}: {mod['score']} ({mod['risk_category']}) [Verified: {mod['verification_status']}]")
        else:
            print(f"Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    test_api()
"""
}

def apply_fixes():
    for filepath, content in fixes.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    apply_fixes()
