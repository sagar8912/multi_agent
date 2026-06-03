from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import build_url, fetch_url, extract_text_from_html, extract_links
from utils.text_utils import find_keywords
import asyncio

class PrivacyAgent:
    def __init__(self):
        self.privacy_paths = [
            "/privacy", "/privacy-policy", "/privacy-notice", "/privacy.html",
            "/privacy/privacystatement", "/en-us/privacy/privacystatement", 
            "/privacy/statement", "/legal/privacy", "/en-us/privacy",
            "/policies/privacy-policy", "/policies/row-privacy-policy",
            "/cookie-policy", "/policies", "/legal", "/terms"
        ]
        self.compliance_terms = [
            "GDPR", "CCPA", "HIPAA", "SOC 2", "ISO 27001",
            "personal data", "data protection", "privacy notice",
            "cookie policy", "data subject rights", "DPO", "security", "compliance"
        ]
        self.link_keywords = ["privacy", "policy", "legal", "terms", "cookie", "data", "compliance"]

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
                if any(kw in text.lower() for kw in ["privacy", "policy", "terms", "legal"]):
                    terms = find_keywords(text, self.compliance_terms)
                    return final_url or url, status, terms
            return None, status, None

        urls_to_check = [f"{base_url}{path}" for path in self.privacy_paths]
        
        homepage_works = False
        html, status, final_url = await fetch_url(base_url)
        if html and status and status < 400:
            homepage_works = True
            links = extract_links(html, base_url)
            for link in links:
                l_lower = link.lower()
                if any(kw in l_lower for kw in self.link_keywords):
                    if link not in urls_to_check and len(urls_to_check) < 20:
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
        
        reason_for_score = ""
        
        if not homepage_works and not found_policy:
            score = 3.0
            risk_category = "Manual Review Required"
            confidence = 0.2
            reason_for_score = "Website not reachable or blocked everywhere."
            findings.append(reason_for_score)
        elif homepage_works and not found_policy:
            score = 4.0
            risk_category = "Unfavorable"
            confidence = 0.6
            reason_for_score = "Website reachable, but no privacy/legal/cookie policy found."
            findings.append(reason_for_score)
        elif found_policy:
            # Determine if it's a generic terms page or privacy policy
            is_generic = False
            if evidence and evidence[0].url:
                url_lower = evidence[0].url.lower()
                if "terms" in url_lower or "legal" in url_lower and "privacy" not in url_lower:
                    is_generic = True
            
            if len(compliance_found) >= 2 and not is_generic:
                score = 1.0
                risk_category = "Favorable"
                confidence = 0.9
                reason_for_score = f"Privacy page found with strong regulatory keywords: {', '.join(compliance_found)}"
                findings.append(reason_for_score)
            elif len(compliance_found) > 0 and not is_generic:
                score = 2.0
                risk_category = "Average"
                confidence = 0.8
                reason_for_score = f"Privacy/legal page found with limited compliance keywords: {', '.join(compliance_found)}."
                findings.append(reason_for_score)
            else:
                score = 3.0
                risk_category = "Partially Unfavorable"
                confidence = 0.7
                reason_for_score = "Only generic legal/terms page found, weak privacy evidence."
                findings.append(reason_for_score)
        else:
            score = 3.0
            risk_category = "Unknown"
            confidence = 0.2
            reason_for_score = "Could not evaluate privacy regulation."
            findings.append(reason_for_score)
            
        return ModifierResult(
            modifier_name="Privacy Regulation",
            score=score,
            risk_category=risk_category,
            confidence=confidence,
            findings=findings,
            evidence=evidence,
            recommendation="Publish and maintain a clear privacy policy with GDPR/CCPA references where applicable.",
            reason_for_score=reason_for_score
        )
