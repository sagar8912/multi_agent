from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import fetch_homepage, extract_text_from_html, extract_links
from utils.text_utils import find_keywords
import urllib.parse

class InternetFootprintAgent:
    def __init__(self):
        self.scale_keywords = [
            "customers", "users", "millions", "active users", 
            "subscribers", "clients", "enterprises", "global users"
        ]

    async def run(self, company: CompanyInput) -> ModifierResult:
        html, status, final_url = await fetch_homepage(company.domain)
        
        if not html:
            reason = "Site unavailable, could not evaluate internet footprint."
            return ModifierResult(
                modifier_name="Internet Footprint",
                score=3.0,
                risk_category="Manual Review Required",
                confidence=0.2,
                findings=[reason],
                evidence=[],
                recommendation="Review footprint using paid external intelligence sources.",
                reason_for_score=reason
            )
            
        text = extract_text_from_html(html)
        scale_found = find_keywords(text, self.scale_keywords)
        
        links = extract_links(html, final_url or f"https://{company.domain}")
        
        base_domain = company.domain.replace("www.", "").lower()
        subdomains = set()
        external_links = 0
        internal_links = 0
        
        for link in links:
            try:
                parsed = urllib.parse.urlparse(link)
                netloc = parsed.netloc.lower()
                if not netloc:
                    internal_links += 1
                elif base_domain in netloc:
                    internal_links += 1
                    if netloc != base_domain and netloc != f"www.{base_domain}":
                        subdomains.add(netloc)
                else:
                    external_links += 1
            except:
                pass
                
        subdomain_count = len(subdomains)
        has_scale_signals = len(scale_found) > 0
        
        # Scoring logic
        if subdomain_count > 5 and has_scale_signals:
            score = 4.0
            risk_category = "Unfavorable"
            reason_for_score = "Very broad footprint (many subdomains) and high user/customer scale."
        elif subdomain_count >= 2 and has_scale_signals:
            score = 3.0
            risk_category = "Partially Unfavorable"
            reason_for_score = "Many external links/subdomains with detected user scale."
        elif subdomain_count >= 2 or has_scale_signals:
            score = 2.0
            risk_category = "Average"
            reason_for_score = "Moderate footprint or scale signals detected."
        else:
            score = 1.0
            risk_category = "Favorable"
            reason_for_score = "Low footprint with no major scale signals detected."
            
        findings = [reason_for_score]
        if subdomains:
            findings.append(f"Subdomains discovered: {', '.join(list(subdomains)[:5])}")
        if scale_found:
            findings.append(f"Scale indicators: {', '.join(scale_found)}")
            
        evidence = [Evidence(url=final_url, description="Analyzed for footprint scale and subdomains", status_code=status)]
        
        raw_data = {
            "scale_signals_found": scale_found,
            "subdomain_count": subdomain_count,
            "subdomains": list(subdomains),
            "internal_links_count": internal_links,
            "external_links_count": external_links
        }

        return ModifierResult(
            modifier_name="Internet Footprint",
            score=score,
            risk_category=risk_category,
            confidence=0.7,
            findings=findings,
            evidence=evidence,
            raw_data=raw_data,
            recommendation="Manage attack surface by monitoring all active subdomains and enforcing security policies globally.",
            reason_for_score=reason_for_score
        )
