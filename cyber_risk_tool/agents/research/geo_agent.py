from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import fetch_homepage, extract_text_from_html
from utils.text_utils import find_keywords

class GeoAgent:
    def __init__(self):
        self.countries = [
            "USA", "United States", "India", "UK", "United Kingdom", 
            "Canada", "Germany", "France", "Australia", "Singapore", 
            "Japan", "China", "Brazil", "Mexico", "UAE", "Netherlands",
            "Ireland", "Spain", "Italy", "Switzerland", "Sweden", 
            "Norway", "South Korea"
        ]
        self.regions = ["Europe", "Asia", "Americas", "Middle East", "Africa", "Global"]
        self.global_keywords = [
            "global", "worldwide", "offices", "locations", "regions",
            "countries", "international", "across the world", "global presence"
        ]
        
    async def run(self, company: CompanyInput) -> ModifierResult:
        html, status, final_url = await fetch_homepage(company.domain)
        
        if not html:
            reason = "Site unavailable, could not evaluate geographic spread."
            return ModifierResult(
                modifier_name="Geographic Spread",
                score=3.0,
                risk_category="Unknown",
                confidence=0.2,
                findings=[reason],
                evidence=[],
                recommendation="Validate global operations using official office/location pages.",
                reason_for_score=reason
            )
            
        text = extract_text_from_html(html)
        found_countries = set(find_keywords(text, self.countries))
        if company.country and company.country in self.countries:
            found_countries.add(company.country)
            
        global_found = find_keywords(text, self.global_keywords)
        regions_found = set(find_keywords(text, self.regions))
        
        evidence = [Evidence(url=final_url, description="Analyzed for geo footprint", status_code=status)]
        findings = []
        
        num_countries = len(found_countries)
        num_regions = len(regions_found)
        usa_presence = "USA" in found_countries or "United States" in found_countries
        
        score = 2.0
        risk_category = "Average"
        reason_for_score = ""
        
        revenue = company.revenue_band or "Unknown"
        
        if "> $1B" in revenue:
            if num_countries <= 10 and num_regions <= 1:
                score, risk_category = 1.0, "Favorable"
                reason_for_score = "10 or fewer countries on same continent for >$1B company."
            elif num_countries <= 10:
                score, risk_category = 2.0, "Average"
                reason_for_score = "10 or fewer countries regardless of continent for >$1B company."
            else:
                score, risk_category = 3.0, "Partially Unfavorable"
                reason_for_score = "More than 10 countries for >$1B company."
        elif "$250M" in revenue and "$1B" in revenue:
            if num_countries <= 5:
                score, risk_category = 1.0, "Favorable"
                reason_for_score = "5 or fewer countries for $250M-$1B company."
            elif num_countries <= 7:
                score, risk_category = 3.0, "Partially Unfavorable"
                reason_for_score = "Up to 7 countries for $250M-$1B company."
            else:
                score, risk_category = 4.0, "Unfavorable"
                reason_for_score = "More than 7 countries for $250M-$1B company."
        elif "$50M" in revenue and "$250M" in revenue:
            if num_countries <= 3:
                score, risk_category = 1.0, "Favorable"
                reason_for_score = "3 or fewer countries for $50M-$250M company."
            elif num_countries <= 5:
                score, risk_category = 3.0, "Partially Unfavorable"
                reason_for_score = "Up to 5 countries for $50M-$250M company."
            else:
                score, risk_category = 4.0, "Unfavorable"
                reason_for_score = "More than 5 countries for $50M-$250M company."
        elif "< $50M" in revenue:
            if num_countries <= 2:
                score, risk_category = 1.0, "Favorable"
                reason_for_score = "1-2 countries for <$50M company."
            else:
                score, risk_category = 4.0, "Unfavorable"
                reason_for_score = "More than 2 countries for <$50M company."
        else: # Unknown
            if num_countries <= 2:
                score, risk_category = 1.0, "Favorable"
                reason_for_score = "Limited geographic spread (<=2) for unknown revenue."
            elif num_countries <= 5:
                score, risk_category = 2.0, "Average"
                reason_for_score = "Moderate geographic spread for unknown revenue."
            else:
                score, risk_category = 3.0, "Partially Unfavorable"
                reason_for_score = "Broad geographic spread for unknown revenue."
                
        if usa_presence and score > 1.0:
            findings.append("USA operations presence detected (could offset some risks depending on jurisdiction).")
            
        if global_found and num_countries <= 2:
            score = max(score, 2.0)
            if risk_category == "Favorable": risk_category = "Average"
            reason_for_score += " Global keywords detected, increasing risk."
            
        findings.append(reason_for_score)

        raw_data = {
            "countries_found": list(found_countries),
            "country_count": num_countries,
            "usa_presence": usa_presence,
            "global_signals": list(global_found),
            "revenue_band": revenue,
            "revenue_adjustment_applied": True
        }

        return ModifierResult(
            modifier_name="Geographic Spread",
            score=score,
            risk_category=risk_category,
            confidence=0.8,
            findings=findings,
            evidence=evidence,
            raw_data=raw_data,
            recommendation="Validate global operations using official office/location pages.",
            reason_for_score=reason_for_score
        )
