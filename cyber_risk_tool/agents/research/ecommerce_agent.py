from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import fetch_homepage, extract_text_from_html
from utils.text_utils import find_keywords

class EcommerceAgent:
    def __init__(self):
        self.strong_keywords = [
            "checkout", "cart", "add to cart", "payment", 
            "billing", "order now", "buy now", "shipping", "refund", "invoice"
        ]
        self.medium_keywords = [
            "pricing", "subscription", "plan", "login", 
            "sign up", "account", "customer portal", "free trial"
        ]
        
    async def run(self, company: CompanyInput) -> ModifierResult:
        html, status, final_url = await fetch_homepage(company.domain)
        
        evidence = []
        findings = []
        
        if not html:
            reason = "Site unavailable, could not evaluate e-commerce presence."
            return ModifierResult(
                modifier_name="E-Commerce Presence",
                score=3.0,
                risk_category="Unknown",
                confidence=0.2,
                findings=[reason],
                evidence=[],
                recommendation="Review customer data collection and payment security controls.",
                reason_for_score=reason
            )
            
        evidence.append(Evidence(url=final_url, description="Homepage analyzed for e-commerce signals", status_code=status))
        text = extract_text_from_html(html)
        
        strong_signals = find_keywords(text, self.strong_keywords)
        medium_signals = find_keywords(text, self.medium_keywords)
        
        s_count = len(strong_signals)
        m_count = len(medium_signals)
        
        reason_for_score = ""
        if s_count >= 3:
            score = 4.0
            risk_category = "Unfavorable"
            reason_for_score = f"3 or more strong e-commerce signals found: {', '.join(strong_signals)}"
            findings.append(reason_for_score)
        elif 1 <= s_count <= 2:
            score = 3.0
            risk_category = "Partially Unfavorable"
            reason_for_score = f"1-2 strong e-commerce signals found: {', '.join(strong_signals)}"
            findings.append(reason_for_score)
        elif m_count > 0:
            score = 2.0
            risk_category = "Average"
            reason_for_score = f"Only medium signals found (no checkout/cart): {', '.join(medium_signals)}"
            findings.append(reason_for_score)
        else:
            score = 1.0
            risk_category = "Favorable"
            reason_for_score = "No strong or customer transaction signals found; mostly informational."
            findings.append(reason_for_score)
            
        raw_data = {
            "strong_signals": strong_signals,
            "medium_signals": medium_signals,
            "signal_count": s_count + m_count
        }
            
        return ModifierResult(
            modifier_name="E-Commerce Presence",
            score=score,
            risk_category=risk_category,
            confidence=0.8,
            findings=findings,
            evidence=evidence,
            raw_data=raw_data,
            recommendation="Review customer data collection and payment security controls.",
            reason_for_score=reason_for_score
        )
