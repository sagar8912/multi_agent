import os

files = {
"cyber_risk_tool/api/__init__.py": "",
"cyber_risk_tool/api/main.py": """\
from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Cyber Risk Underwriting Intelligence Tool",
    description="Agentic AI tool for cyber risk assessment.",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "message": "Cyber Risk Underwriting Intelligence Tool",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
""",
"cyber_risk_tool/api/routes.py": """\
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
""",
"cyber_risk_tool/api/dependencies.py": """\
# Dependencies for FastAPI (e.g., DB connections, authentication) could go here.
""",
"cyber_risk_tool/schemas/__init__.py": "",
"cyber_risk_tool/schemas/input_models.py": """\
from pydantic import BaseModel
from typing import Optional

class CompanyInput(BaseModel):
    company_name: str
    domain: str
    country: str
    revenue_band: str
    industry: Optional[str] = None
""",
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
"cyber_risk_tool/core/__init__.py": "",
"cyber_risk_tool/core/config.py": """\
import yaml
import os
from utils.logger import get_logger

logger = get_logger(__name__)

def load_rules():
    rule_file = os.path.join(os.path.dirname(__file__), '..', 'rules', 'modifiers.yaml')
    try:
        with open(rule_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning("modifiers.yaml not found, returning defaults.")
        return {}
    except Exception as e:
        logger.error(f"Error loading rules: {e}")
        return {}
""",
"cyber_risk_tool/core/scoring_engine.py": """\
from typing import List
from schemas.output_models import ModifierResult
from core.config import load_rules

class ScoringEngine:
    def __init__(self):
        self.rules = load_rules()
        
    def calculate_score(self, modifiers: List[ModifierResult]):
        total_weight = 0.0
        weighted_score = 0.0
        total_confidence = 0.0
        
        for mod in modifiers:
            # Map Python class modifier name to yaml key
            mod_key_map = {
                "Domain Encryption": "domain_encryption",
                "Privacy Regulation": "privacy_regulation",
                "E-Commerce Presence": "ecommerce_presence",
                "Customer Type": "customer_type",
                "Geographic Spread": "geographic_spread"
            }
            key = mod_key_map.get(mod.modifier_name, "")
            
            weight = 1.0
            if key in self.rules and "weight" in self.rules[key]:
                weight = float(self.rules[key]["weight"])
                
            weighted_score += mod.score * weight
            total_weight += weight
            total_confidence += mod.confidence
            
        overall_score = weighted_score / total_weight if total_weight > 0 else 0
        overall_confidence = total_confidence / len(modifiers) if modifiers else 0
        
        overall_risk_category = self._get_risk_category(overall_score)
        
        return overall_score, overall_risk_category, overall_confidence
        
    def _get_risk_category(self, score: float) -> str:
        if 1.0 <= score <= 1.5: return "Very Favorable"
        if 1.5 < score <= 2.2: return "Favorable"
        if 2.2 < score <= 3.0: return "Average"
        if 3.0 < score <= 3.6: return "Partially Unfavorable"
        if 3.6 < score <= 4.0: return "Unfavorable"
        return "Unknown"
""",
"cyber_risk_tool/core/llm_client.py": """\
# Placeholder for future LLM integration.
# TODO: Implement Azure OpenAI / LLM client here later.

class LLMClient:
    def __init__(self):
        pass
        
    def generate_summary(self, prompt: str) -> str:
        # Do not call any external LLM now.
        return "LLM integration pending."
""",
"cyber_risk_tool/utils/__init__.py": "",
"cyber_risk_tool/utils/logger.py": """\
import logging

def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
""",
"cyber_risk_tool/utils/text_utils.py": """\
from typing import List

def safe_lower(text: str) -> str:
    return text.lower() if text else ""

def count_keywords(text: str, keywords: List[str]) -> int:
    text_lower = safe_lower(text)
    return sum(1 for kw in keywords if kw.lower() in text_lower)

def find_keywords(text: str, keywords: List[str]) -> List[str]:
    text_lower = safe_lower(text)
    return [kw for kw in keywords if kw.lower() in text_lower]
""",
"cyber_risk_tool/utils/scraper.py": """\
import httpx
from bs4 import BeautifulSoup
from typing import Tuple, List, Optional
from urllib.parse import urljoin
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

def normalize_domain(domain: str) -> str:
    domain = domain.strip().lower()
    if domain.startswith("http://"): domain = domain[7:]
    if domain.startswith("https://"): domain = domain[8:]
    if domain.endswith("/"): domain = domain[:-1]
    return domain

def build_url(domain: str, scheme: str = "https") -> str:
    return f"{scheme}://{normalize_domain(domain)}"

async def fetch_url(url: str, timeout: int = 10) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    try:
        async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=timeout) as client:
            resp = await client.get(url)
            return resp.text, resp.status_code, str(resp.url)
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching {url}")
        return None, None, None
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None, None, None

async def fetch_homepage(domain: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    url = build_url(domain, "https")
    text, status, final_url = await fetch_url(url)
    if not text:
        url = build_url(domain, "http")
        text, status, final_url = await fetch_url(url)
    return text, status, final_url

def extract_text_from_html(html: str) -> str:
    if not html: return ""
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
    return soup.get_text(separator=' ', strip=True)

def extract_links(html: str, base_url: str) -> List[str]:
    if not html: return []
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        href = a.get('href')
        if href:
            links.append(urljoin(base_url, href))
    return list(set(links))

def find_candidate_pages(domain: str, keywords: List[str]) -> List[str]:
    # Placeholder for a function that might search for specific pages
    return []
""",
"cyber_risk_tool/agents/__init__.py": "",
"cyber_risk_tool/agents/supervisor.py": """\
from schemas.input_models import CompanyInput
from schemas.output_models import CyberRiskReport, ModifierResult
from agents.research.domain_agent import DomainAgent
from agents.research.privacy_agent import PrivacyAgent
from agents.research.ecommerce_agent import EcommerceAgent
from agents.research.customer_type_agent import CustomerTypeAgent
from agents.research.geo_agent import GeoAgent
from agents.fact_checker import FactCheckerAgent
from agents.underwriter import UnderwriterAgent
from core.scoring_engine import ScoringEngine
from datetime import datetime
import asyncio

class SupervisorAgent:
    def __init__(self):
        self.domain_agent = DomainAgent()
        self.privacy_agent = PrivacyAgent()
        self.ecommerce_agent = EcommerceAgent()
        self.customer_agent = CustomerTypeAgent()
        self.geo_agent = GeoAgent()
        self.fact_checker = FactCheckerAgent()
        self.underwriter = UnderwriterAgent()
        self.scoring_engine = ScoringEngine()

    async def run_analysis(self, company: CompanyInput) -> CyberRiskReport:
        # 1. Run Research Agents concurrently
        agents = [
            self.domain_agent,
            self.privacy_agent,
            self.ecommerce_agent,
            self.customer_agent,
            self.geo_agent
        ]
        
        tasks = [agent.run(company) for agent in agents]
        modifier_results = await asyncio.gather(*tasks)
        
        # 2. Run Fact Checker
        verified_results = self.fact_checker.verify(modifier_results)
        
        # 3. Calculate Score
        overall_score, risk_category, overall_confidence = self.scoring_engine.calculate_score(verified_results)
        
        # 4. Underwriter Summary
        summary = self.underwriter.generate_summary(company, verified_results, overall_score, risk_category)
        
        return CyberRiskReport(
            company_name=company.company_name,
            domain=company.domain,
            country=company.country,
            revenue_band=company.revenue_band,
            industry=company.industry,
            overall_score=overall_score,
            overall_risk_category=risk_category,
            overall_confidence=overall_confidence,
            modifiers=verified_results,
            underwriter_summary=summary,
            generated_at=datetime.utcnow()
        )
""",
"cyber_risk_tool/agents/fact_checker.py": """\
from typing import List
from schemas.output_models import ModifierResult

class FactCheckerAgent:
    def verify(self, modifiers: List[ModifierResult]) -> List[ModifierResult]:
        for mod in modifiers:
            has_evidence = len(mod.evidence) > 0
            if has_evidence:
                mod.verification_status = "verified"
            else:
                mod.verification_status = "not_verified"
                # Reduce confidence slightly if no evidence
                mod.confidence = max(0.1, mod.confidence - 0.2)
        return modifiers
""",
"cyber_risk_tool/agents/underwriter.py": """\
from typing import List
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult

class UnderwriterAgent:
    def generate_summary(self, company: CompanyInput, modifiers: List[ModifierResult], score: float, risk_category: str) -> str:
        # Template-based summary without LLM
        fav = [m.modifier_name for m in modifiers if m.risk_category in ("Favorable", "Very Favorable")]
        unfav = [m.modifier_name for m in modifiers if m.risk_category in ("Partially Unfavorable", "Unfavorable")]
        
        summary = f"{company.company_name} was assessed and classified as {risk_category} risk (score: {score:.2f}). "
        if fav:
            summary += f"The company shows strong posture in {', '.join(fav)}. "
        if unfav:
            summary += f"However, there are areas of concern regarding {', '.join(unfav)}. "
            
        summary += "Overall, the evidence suggests an underwriting approach consistent with the assessed risk category."
        return summary
""",
"cyber_risk_tool/agents/research/__init__.py": "",
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
        score = 3
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
                score = 1
                risk_category = "Favorable"
                confidence = 0.9
                findings.append("Valid HTTPS and HTTP redirects to HTTPS.")
            elif https_works and not redirects_to_https:
                score = 2
                risk_category = "Average"
                confidence = 0.8
                findings.append("HTTPS works, but HTTP does not redirect.")
            elif not https_works and http_works:
                score = 4
                risk_category = "Unfavorable"
                confidence = 0.8
                findings.append("HTTPS fails but HTTP works (insecure).")
            else:
                score = 3
                risk_category = "Unknown"
                confidence = 0.5
                findings.append("Website appears unavailable.")
                
        except Exception as e:
            findings.append(f"Error during domain check: {e}")
            
        return ModifierResult(
            modifier_name="Domain Encryption",
            score=score,
            risk_category=risk_category,
            confidence=confidence,
            findings=findings,
            evidence=evidence
        )
""",
"cyber_risk_tool/agents/research/privacy_agent.py": """\
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import build_url, fetch_url, extract_text_from_html
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
        async def check_path(path):
            url = f"{base_url}{path}"
            html, status, final_url = await fetch_url(url)
            if html and status and status < 400:
                text = extract_text_from_html(html)
                # Ensure it's not a generic 404 page that returns 200
                if "privacy" in text.lower() or "policy" in text.lower():
                    terms = find_keywords(text, self.compliance_terms)
                    return url, status, terms
            return None, None, None

        tasks = [check_path(path) for path in self.privacy_paths]
        results = await asyncio.gather(*tasks)
        
        for url, status, terms in results:
            if url:
                found_policy = True
                compliance_found.extend(terms)
                evidence.append(Evidence(url=url, description="Privacy policy found", status_code=status))
                break
                
        compliance_found = list(set(compliance_found))
        
        if found_policy and len(compliance_found) > 0:
            score = 1
            risk_category = "Favorable"
            confidence = 0.9
            findings.append(f"Privacy policy found with compliance terms: {', '.join(compliance_found)}")
        elif found_policy:
            score = 2
            risk_category = "Average"
            confidence = 0.8
            findings.append("Privacy policy found but few compliance terms identified.")
        else:
            score = 3
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
                score=3,
                risk_category="Unknown",
                confidence=0.2,
                findings=["Site unavailable, could not evaluate e-commerce presence."],
                evidence=[]
            )
            
        evidence.append(Evidence(url=final_url, description="Homepage analyzed for e-commerce signals", status_code=status))
        text = extract_text_from_html(html)
        found_keywords = find_keywords(text, self.ecommerce_keywords)
        
        # Simple heuristic
        strong_signals = [k for k in found_keywords if k in ["cart", "checkout", "payment", "buy now", "add to cart"]]
        med_signals = [k for k in found_keywords if k in ["pricing", "subscription", "login", "sign up", "account", "billing"]]
        
        if len(strong_signals) > 0 and len(med_signals) > 0:
            score = 4
            risk_category = "Unfavorable"
            findings.append(f"Strong e-commerce and account signals found: {', '.join(strong_signals + med_signals)}")
        elif len(strong_signals) > 0:
            score = 3
            risk_category = "Partially Unfavorable"
            findings.append(f"E-commerce transaction signals found: {', '.join(strong_signals)}")
        elif len(med_signals) > 0:
            score = 2
            risk_category = "Average"
            findings.append(f"Pricing/subscription/account signals found: {', '.join(med_signals)}")
        else:
            score = 1
            risk_category = "Favorable"
            findings.append("No active e-commerce or account signals found.")
            
        return ModifierResult(
            modifier_name="E-Commerce Presence",
            score=score,
            risk_category=risk_category,
            confidence=0.8,
            findings=findings,
            evidence=evidence
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
                score=2,
                risk_category="Average",
                confidence=0.2,
                findings=["Site unavailable, defaulting to Unknown."],
                evidence=[]
            )
            
        text = extract_text_from_html(html)
        b2b_found = find_keywords(text, self.b2b_keywords)
        b2c_found = find_keywords(text, self.b2c_keywords)
        
        b2b_count = len(b2b_found)
        b2c_count = len(b2c_found)
        
        evidence = [Evidence(url=final_url, description="Analyzed homepage text for B2B/B2C keywords", status_code=status)]
        
        if b2b_count > 0 and b2c_count == 0:
            ctype = "B2B"
            score = 1
            risk_category = "Favorable"
            findings = [f"B2B signals strongly present: {', '.join(b2b_found)}"]
        elif b2c_count > 0 and b2b_count == 0:
            ctype = "B2C"
            score = 3
            risk_category = "Partially Unfavorable"
            findings = [f"B2C signals strongly present: {', '.join(b2c_found)}"]
        elif b2b_count > 0 and b2c_count > 0:
            ctype = "Mixed"
            score = 2
            risk_category = "Average"
            findings = [f"Mixed signals found. B2B: {', '.join(b2b_found)}. B2C: {', '.join(b2c_found)}"]
        else:
            ctype = "Unknown"
            score = 2
            risk_category = "Average"
            findings = ["No clear B2B or B2C signals found."]
            
        return ModifierResult(
            modifier_name="Customer Type",
            score=score,
            risk_category=risk_category,
            confidence=0.8 if ctype != "Unknown" else 0.4,
            findings=findings,
            evidence=evidence,
            raw_data={"inferred_type": ctype}
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
                score=2,
                risk_category="Average",
                confidence=0.2,
                findings=["Site unavailable."],
                evidence=[]
            )
            
        text = extract_text_from_html(html)
        found_countries = set(find_keywords(text, self.countries))
        # ensure provided country is in the count
        if company.country and company.country in self.countries:
            found_countries.add(company.country)
            
        global_found = find_keywords(text, self.global_keywords)
        
        evidence = [Evidence(url=final_url, description="Analyzed for geo footprint", status_code=status)]
        findings = []
        
        num_countries = len(found_countries)
        
        if num_countries <= 2 and not global_found:
            score = 1
            risk_category = "Favorable"
            findings.append(f"Limited geographic spread ({num_countries} countries).")
        elif (3 <= num_countries <= 5) or global_found:
            score = 2
            risk_category = "Average"
            findings.append(f"Moderate geographic spread ({num_countries} countries). Global signals: {', '.join(global_found)}")
        else:
            score = 3
            risk_category = "Partially Unfavorable"
            findings.append(f"Wide geographic spread (>5 countries: {', '.join(found_countries)}).")
            
        # Revenue adjustment
        if company.revenue_band == "> $1B":
            score = max(1, score - 1)
            findings.append("Severity reduced due to >$1B revenue (expected broader spread).")
            if score == 1: risk_category = "Favorable"
            elif score == 2: risk_category = "Average"
            
        return ModifierResult(
            modifier_name="Geographic Spread",
            score=score,
            risk_category=risk_category,
            confidence=0.8,
            findings=findings,
            evidence=evidence
        )
""",
"cyber_risk_tool/rules/modifiers.yaml": """\
domain_encryption:
  name: Domain Encryption
  enabled: true
  weight: 1.0
  description: Evaluates HTTPS and domain encryption posture.

privacy_regulation:
  name: Privacy Regulation
  enabled: true
  weight: 1.0
  description: Evaluates privacy policy and regulatory signals.

ecommerce_presence:
  name: E-Commerce Presence
  enabled: true
  weight: 1.0
  description: Evaluates online transaction and customer data exposure.

customer_type:
  name: Customer Type
  enabled: true
  weight: 1.0
  description: Identifies whether the company is B2B, B2C, mixed, or unknown.

geographic_spread:
  name: Geographic Spread
  enabled: true
  weight: 1.0
  description: Evaluates geographic concentration and international exposure.
""",
"cyber_risk_tool/tests/__init__.py": "",
"cyber_risk_tool/tests/test_sample_requests.py": """\
import httpx
import time

def test_api():
    base_url = "http://127.0.0.1:8000"
    try:
        httpx.get(f"{base_url}/health")
    except Exception:
        print("API not running. Please start it using 'python run.py'.")
        return
        
    domains = ["microsoft.com", "apple.com", "example.com"]
    for domain in domains:
        print(f"\\nTesting {domain}...")
        payload = {
            "company_name": domain.split('.')[0].capitalize(),
            "domain": domain,
            "country": "USA",
            "revenue_band": "> $1B",
            "industry": "Technology"
        }
        resp = httpx.post(f"{base_url}/analyze-company", json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Result for {domain}:")
            print(f"  Overall Score: {data['overall_score']:.2f}")
            print(f"  Risk Category: {data['overall_risk_category']}")
            for mod in data['modifiers']:
                print(f"    - {mod['modifier_name']}: {mod['score']} ({mod['risk_category']})")
        else:
            print(f"Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    test_api()
""",
"cyber_risk_tool/outputs/sample_report.json": "{}",
"cyber_risk_tool/requirements.txt": """\
fastapi
uvicorn
pydantic
httpx
beautifulsoup4
PyYAML
python-dotenv
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

## 7. How to run FastAPI
```bash
uvicorn api.main:app --reload
# OR
python run.py
```

## 8. How to open Swagger UI
Go to: http://127.0.0.1:8000/docs

## 9. Sample request
```json
{
  "company_name": "Microsoft",
  "domain": "microsoft.com",
  "country": "USA",
  "revenue_band": "> $1B",
  "industry": "Technology"
}
```

## 10. Sample response
(See Swagger UI for the full JSON schema of CyberRiskReport)

## 11. How to test
```bash
python -m tests.test_sample_requests
```

## 12. Future enhancements
- Azure OpenAI integration for Underwriter summaries
- LangGraph orchestration
- Dark Web checks and paid API integrations

## 13. Troubleshooting
- If website parsing fails, ensure you have an active internet connection.
- Timeout errors can be resolved by increasing httpx timeout in `utils/scraper.py`.
""",
"cyber_risk_tool/Dockerfile": """\
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
"cyber_risk_tool/.env.example": """\
# Placeholder for future keys
AZURE_OPENAI_API_KEY=
LLM_MODEL=gpt-4
""",
"cyber_risk_tool/sample_request.json": """\
{
  "company_name": "Example Corp",
  "domain": "example.com",
  "country": "USA",
  "revenue_band": "< $50M",
  "industry": "Retail"
}
""",
"cyber_risk_tool/run.py": """\
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
"""
}

def create_project():
    for filepath, content in files.items():
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    create_project()
    print("Project cyber_risk_tool created successfully.")
