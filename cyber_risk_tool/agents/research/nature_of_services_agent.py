from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import fetch_homepage, extract_text_from_html
from utils.text_utils import find_keywords

class NatureOfServicesAgent:
    def __init__(self):
        self.critical_keywords = [
            "payment gateway", "healthcare data", "identity verification", "crypto", "trading platform"
        ]
        self.high_keywords = [
            "saas", "cloud", "payment", "fintech", "marketplace", 
            "e-commerce", "ecommerce", "identity", "security", 
            "api", "platform", "data analytics", "ai", "artificial intelligence", "customer portal"
        ]
        self.moderate_keywords = [
            "consulting", "software services", "b2b services", 
            "professional services", "manufacturing", "logistics"
        ]

    async def run(self, company: CompanyInput) -> ModifierResult:
        html, status, final_url = await fetch_homepage(company.domain)
        
        if not html:
            reason = "Site unavailable, could not evaluate nature of services."
            return ModifierResult(
                modifier_name="Nature of Services",
                score=3.0,
                risk_category="Manual Review Required",
                confidence=0.2,
                findings=[reason],
                evidence=[],
                recommendation="Review services portfolio using external intelligence sources.",
                reason_for_score=reason
            )
            
        text = extract_text_from_html(html)
        
        critical_found = find_keywords(text, self.critical_keywords)
        high_found = find_keywords(text, self.high_keywords)
        mod_found = find_keywords(text, self.moderate_keywords)
        
        if critical_found:
            score = 4.0
            risk_category = "Unfavorable"
            reason_for_score = "Critical digital platform/payment/health/identity exposure detected."
            exposure_level = "Critical"
        elif len(high_found) >= 2:
            score = 3.0
            risk_category = "Partially Unfavorable"
            reason_for_score = "High digital/customer data exposure detected."
            exposure_level = "High"
        elif mod_found or len(high_found) == 1:
            score = 2.0
            risk_category = "Average"
            reason_for_score = "Moderate digital exposure detected."
            exposure_level = "Moderate"
        else:
            score = 1.0
            risk_category = "Favorable"
            reason_for_score = "Low digital exposure / likely offline services."
            exposure_level = "Low"
            
        findings = [reason_for_score]
        if critical_found: findings.append(f"Critical signals: {', '.join(critical_found)}")
        if high_found: findings.append(f"High risk signals: {', '.join(high_found)}")
        
        evidence = [Evidence(url=final_url, description="Analyzed for industry and service exposure", status_code=status)]
        
        raw_data = {
            "detected_services": critical_found + high_found + mod_found,
            "industry_keywords_found": critical_found + high_found + mod_found,
            "digital_exposure_level": exposure_level,
            "reason_for_score": reason_for_score
        }

        return ModifierResult(
            modifier_name="Nature of Services",
            score=score,
            risk_category=risk_category,
            confidence=0.75,
            findings=findings,
            evidence=evidence,
            raw_data=raw_data,
            recommendation="Review product portfolio against underwriting appetite guidelines.",
            reason_for_score=reason_for_score
        )
