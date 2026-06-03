from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import fetch_homepage, extract_text_from_html
from utils.text_utils import find_keywords

class CustomerTypeAgent:
    def __init__(self):
        self.b2b_keywords = [
            "enterprise", "business", "organizations", "teams", 
            "platform", "solutions", "demo", "contact sales", 
            "partners", "clients", "industries", "cloud", "saas"
        ]
        self.b2c_keywords = [
            "consumer", "customers", "shop", "buy", "personal", 
            "individual", "retail", "family", "home", "app store", "download", "cart", "checkout"
        ]
        
    async def run(self, company: CompanyInput) -> ModifierResult:
        html, status, final_url = await fetch_homepage(company.domain)
        
        if not html:
            reason = "Site unavailable, could not evaluate customer type."
            return ModifierResult(
                modifier_name="Customer Type",
                score=3.0,
                risk_category="Unknown",
                confidence=0.2,
                findings=[reason],
                evidence=[],
                recommendation="Validate customer profile through annual reports or product pages.",
                reason_for_score=reason
            )
            
        text = extract_text_from_html(html)
        b2b_found = find_keywords(text, self.b2b_keywords)
        b2c_found = find_keywords(text, self.b2c_keywords)
        
        b2b_score = len(b2b_found)
        b2c_score = len(b2c_found)
        
        evidence = [Evidence(url=final_url, description="Analyzed homepage text for B2B/B2C keywords", status_code=status)]
        
        reason_for_score = ""
        findings = []
        if b2c_score > b2b_score * 2 and ("cart" in b2c_found or "checkout" in b2c_found or "buy" in b2c_found):
            ctype = "B2C"
            score = 4.0
            risk_category = "Unfavorable"
            reason_for_score = f"Clearly B2C with payment/account exposure: {', '.join(b2c_found)}"
            findings.append(reason_for_score)
        elif b2c_score > b2b_score and b2c_score > 0:
            ctype = "Mixed"
            score = 3.0
            risk_category = "Partially Unfavorable"
            reason_for_score = f"Mixed B2B/B2C or consumer accounts detected. B2B: {b2b_score}, B2C: {b2c_score}"
            findings.append(reason_for_score)
        elif b2b_score > 0 and b2c_score > 0:
            ctype = "Mixed"
            score = 2.0
            risk_category = "Average"
            reason_for_score = f"B2B with some consumer/self-service signals. B2B: {b2b_score}, B2C: {b2c_score}"
            findings.append(reason_for_score)
        elif b2b_score > 0:
            ctype = "B2B"
            score = 1.0
            risk_category = "Favorable"
            reason_for_score = f"Clearly B2B, limited consumer data exposure: {', '.join(b2b_found)}"
            findings.append(reason_for_score)
        else:
            ctype = "Unknown"
            score = 2.0
            risk_category = "Average"
            reason_for_score = "Unknown customer type, but website is reachable."
            findings.append(reason_for_score)
            
        raw_data = {
            "customer_type": ctype,
            "b2b_keywords_found": b2b_found,
            "b2c_keywords_found": b2c_found,
            "b2b_score": b2b_score,
            "b2c_score": b2c_score
        }
            
        return ModifierResult(
            modifier_name="Customer Type",
            score=score,
            risk_category=risk_category,
            confidence=0.8 if ctype != "Unknown" else 0.4,
            findings=findings,
            evidence=evidence,
            raw_data=raw_data,
            recommendation="Validate customer profile through annual reports or product pages.",
            reason_for_score=reason_for_score
        )
