import httpx
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import normalize_domain

class DomainAgent:
    async def run(self, company: CompanyInput) -> ModifierResult:
        original_domain = company.domain
        domain = normalize_domain(original_domain)
        
        urls_to_test = [
            f"https://{domain}",
            f"https://www.{domain}",
            f"http://{domain}",
            f"http://www.{domain}"
        ]
        
        evidence = []
        findings = []
        
        https_working = False
        http_working = False
        redirects_to_https = False
        https_status = None
        http_status = None
        final_https_url = None
        final_http_url = None
        errors = []
        tested_urls = []
        access_restricted = False
        blocked_status_code = None
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with httpx.AsyncClient(verify=True, follow_redirects=True, timeout=15, headers=headers) as client:
            for url in urls_to_test[:2]:
                tested_urls.append(url)
                try:
                    resp = await client.get(url)
                    if 200 <= resp.status_code < 400:
                        https_working = True
                        https_status = resp.status_code
                        final_https_url = str(resp.url)
                        evidence.append(Evidence(url=url, description="HTTPS check succeeded", status_code=https_status))
                        break
                    elif resp.status_code in (401, 403, 429):
                        https_working = True
                        access_restricted = True
                        blocked_status_code = resp.status_code
                        https_status = resp.status_code
                        final_https_url = str(resp.url)
                        evidence.append(Evidence(url=url, description="HTTPS reachable but blocked", status_code=resp.status_code))
                        break
                    else:
                        evidence.append(Evidence(url=url, description="HTTPS returned error code", status_code=resp.status_code))
                except Exception as e:
                    errors.append(f"{url}: {e}")
                    evidence.append(Evidence(url=url, description=f"HTTPS failed: {e}", status_code=None))
            
            for url in urls_to_test[2:]:
                tested_urls.append(url)
                try:
                    resp = await client.get(url)
                    if 200 <= resp.status_code < 400 or resp.status_code in (401, 403, 429):
                        http_working = True
                        http_status = resp.status_code
                        final_http_url = str(resp.url)
                        if final_http_url.startswith("https://"):
                            redirects_to_https = True
                        evidence.append(Evidence(url=url, description="HTTP check succeeded", status_code=http_status))
                        break
                    else:
                        evidence.append(Evidence(url=url, description="HTTP returned error code", status_code=resp.status_code))
                except Exception as e:
                    errors.append(f"{url}: {e}")
                    evidence.append(Evidence(url=url, description=f"HTTP failed: {e}", status_code=None))

        reason_for_score = ""
        if access_restricted:
            score = 2.0
            risk_category = "Average"
            confidence = 0.60
            reason_for_score = "HTTPS endpoint appears reachable but automated access was restricted."
            findings.append(reason_for_score)
        elif https_working and redirects_to_https:
            score = 1.0
            risk_category = "Favorable"
            confidence = 0.95
            reason_for_score = "Valid HTTPS and HTTP redirects to HTTPS."
            findings.append(reason_for_score)
        elif https_working and not redirects_to_https:
            score = 2.0
            risk_category = "Average"
            confidence = 0.80
            reason_for_score = "HTTPS is available, but HTTP-to-HTTPS redirect could not be fully confirmed."
            findings.append(reason_for_score)
        elif not https_working and http_working:
            score = 4.0
            risk_category = "Unfavorable"
            confidence = 0.70
            reason_for_score = "HTTPS could not be verified but HTTP is reachable."
            findings.append(reason_for_score)
        else:
            score = 3.0
            risk_category = "Unknown"
            confidence = 0.30
            reason_for_score = "Website could not be reached or DNS failure."
            findings.append(reason_for_score)

        raw_data = {
            "input_domain": original_domain,
            "normalized_domain": domain,
            "domain_scope": "main_domain_only",
            "limitation": "Secondary company-owned domains not yet fully discovered in MVP",
            "tested_urls": tested_urls,
            "https_working": https_working,
            "http_working": http_working,
            "redirects_to_https": redirects_to_https,
            "final_https_url": final_https_url,
            "final_http_url": final_http_url,
            "https_status_code": https_status,
            "http_status_code": http_status,
            "access_restricted": access_restricted,
            "blocked_status_code": blocked_status_code,
            "errors": errors
        }

        return ModifierResult(
            modifier_name="Domain Encryption",
            score=score,
            risk_category=risk_category,
            confidence=confidence,
            findings=findings,
            evidence=evidence,
            raw_data=raw_data,
            recommendation="Ensure HTTPS is enforced and all HTTP traffic redirects to HTTPS." if score > 1.0 and not access_restricted else "Maintain current encryption standards.",
            reason_for_score=reason_for_score
        )
