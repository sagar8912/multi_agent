import os
import re

base_path = r"C:\Users\HP\3D Objects\multi-agent-cyber-rating-modifer"
backend_path = os.path.join(base_path, "cyber_risk_tool")
frontend_path = os.path.join(base_path, "frontend")

files = {}

# 1. Backend Core Logic
files[os.path.join(backend_path, "utils", "scraper.py")] = """\
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
    if domain.startswith("www."): domain = domain[4:]
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
    return []
"""

files[os.path.join(backend_path, "schemas", "output_models.py")] = """\
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
    report_filename: Optional[str] = None
"""

files[os.path.join(backend_path, "agents", "research", "domain_agent.py")] = """\
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
        
        https_works = False
        http_works = False
        redirects_to_https = False
        https_status = None
        http_status = None
        final_url = None
        
        try:
            async with httpx.AsyncClient(verify=True, follow_redirects=False, timeout=10) as client:
                try:
                    resp_https = await client.get(https_url)
                    https_works = (resp_https.status_code < 400)
                    https_status = resp_https.status_code
                    final_url = str(resp_https.url)
                    evidence.append(Evidence(url=https_url, description="HTTPS check", status_code=https_status))
                except Exception as e:
                    evidence.append(Evidence(url=https_url, description=f"HTTPS failed: {e}", status_code=None))
                
                try:
                    resp_http = await client.get(http_url)
                    http_works = (resp_http.status_code < 400)
                    http_status = resp_http.status_code
                    redirects_to_https = (http_status in (301, 302, 307, 308) and "https" in resp_http.headers.get("location", ""))
                    evidence.append(Evidence(url=http_url, description=f"HTTP check, redirect: {redirects_to_https}", status_code=http_status))
                except Exception as e:
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
            
        raw_data = {
            "normalized_domain": domain,
            "https_url": https_url,
            "http_url": http_url,
            "https_status_code": https_status,
            "http_status_code": http_status,
            "redirects_to_https": redirects_to_https,
            "final_url": final_url
        }
            
        return ModifierResult(
            modifier_name="Domain Encryption",
            score=score,
            risk_category=risk_category,
            confidence=confidence,
            findings=findings,
            evidence=evidence,
            raw_data=raw_data,
            recommendation="Maintain HTTPS and ensure all HTTP traffic redirects to HTTPS."
        )
"""

files[os.path.join(backend_path, "agents", "research", "privacy_agent.py")] = """\
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import build_url, fetch_url, extract_text_from_html, extract_links
from utils.text_utils import find_keywords
import asyncio

class PrivacyAgent:
    def __init__(self):
        self.privacy_paths = [
            "/privacy", "/privacy-policy", "/privacy-notice", 
            "/legal/privacy", "/privacy.html", "/legal", "/terms", "/cookie-policy"
        ]
        self.compliance_terms = [
            "GDPR", "CCPA", "HIPAA", "SOC 2", "ISO 27001",
            "personal data", "data protection", "privacy notice",
            "cookie policy", "data subject rights", "DPO", "security", "compliance"
        ]
        self.link_keywords = ["privacy", "legal", "cookie", "data protection", "terms"]

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
                if any(kw in text.lower() for kw in ["privacy", "policy", "terms"]):
                    terms = find_keywords(text, self.compliance_terms)
                    return final_url or url, status, terms
            return None, status, None

        urls_to_check = [f"{base_url}{path}" for path in self.privacy_paths]
        
        homepage_works = False
        html, status, final_url = await fetch_url(base_url)
        if html:
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
        
        if not homepage_works and not found_policy:
            score = 3.0
            risk_category = "Unknown"
            confidence = 0.2
            findings.append("Site unavailable, could not evaluate privacy regulation.")
        elif homepage_works and not found_policy:
            score = 3.0
            risk_category = "Partially Unfavorable"
            confidence = 0.6
            findings.append("Homepage available but no privacy policy could be verified.")
        elif found_policy and len(compliance_found) >= 2:
            score = 1.0
            risk_category = "Favorable"
            confidence = 0.9
            findings.append(f"Privacy policy found with compliance terms: {', '.join(compliance_found)}")
        elif found_policy:
            score = 2.0
            risk_category = "Average"
            confidence = 0.8
            findings.append(f"Privacy policy found but few compliance terms identified: {', '.join(compliance_found) if compliance_found else 'none'}.")
        else:
            score = 3.0
            risk_category = "Unknown"
            confidence = 0.2
            
        return ModifierResult(
            modifier_name="Privacy Regulation",
            score=score,
            risk_category=risk_category,
            confidence=confidence,
            findings=findings,
            evidence=evidence,
            recommendation="Publish and maintain a clear privacy policy with GDPR/CCPA references where applicable."
        )
"""

files[os.path.join(backend_path, "agents", "research", "ecommerce_agent.py")] = """\
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import fetch_homepage, extract_text_from_html
from utils.text_utils import find_keywords

class EcommerceAgent:
    def __init__(self):
        self.strong_keywords = [
            "checkout", "cart", "add to cart", "payment", 
            "billing", "order now", "buy now"
        ]
        self.medium_keywords = [
            "pricing", "subscription", "plan", "login", 
            "sign up", "account", "customer portal"
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
        
        strong_signals = find_keywords(text, self.strong_keywords)
        medium_signals = find_keywords(text, self.medium_keywords)
        
        s_count = len(strong_signals)
        m_count = len(medium_signals)
        
        if s_count >= 3:
            score = 4.0
            risk_category = "Unfavorable"
            findings.append(f"Strong e-commerce signals (>=3) found: {', '.join(strong_signals)}")
        elif 1 <= s_count <= 2:
            score = 3.0
            risk_category = "Partially Unfavorable"
            findings.append(f"Some strong e-commerce signals found: {', '.join(strong_signals)}")
        elif m_count > 0:
            score = 2.0
            risk_category = "Average"
            findings.append(f"Only medium signals (pricing/login) found: {', '.join(medium_signals)}")
        else:
            score = 1.0
            risk_category = "Favorable"
            findings.append("No active e-commerce or account signals found.")
            
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
            recommendation="Review customer data collection and payment security controls."
        )
"""

files[os.path.join(backend_path, "agents", "research", "customer_type_agent.py")] = """\
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
            "consumers", "customers", "shop", "buy", "personal", 
            "individual", "retail", "family", "home", "app store", "download"
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
        
        b2b_score = len(b2b_found)
        b2c_score = len(b2c_found)
        
        evidence = [Evidence(url=final_url, description="Analyzed homepage text for B2B/B2C keywords", status_code=status)]
        
        if b2b_score > b2c_score * 2 and b2b_score > 0:
            ctype = "B2B"
            score = 1.0
            risk_category = "Favorable"
            findings = [f"Strong B2B profile detected: {', '.join(b2b_found)}"]
        elif b2c_score > b2b_score * 2 and b2c_score > 0:
            ctype = "B2C"
            score = 3.0
            risk_category = "Partially Unfavorable"
            findings = [f"Strong B2C profile detected: {', '.join(b2c_found)}"]
        elif b2b_score > 0 and b2c_score > 0:
            ctype = "Mixed"
            score = 2.0
            risk_category = "Average"
            findings = [f"Mixed signals found. B2B: {b2b_score}, B2C: {b2c_score}"]
        else:
            ctype = "Unknown"
            score = 2.0
            risk_category = "Average"
            findings = ["No clear B2B or B2C signals found."]
            
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
            recommendation="Validate customer profile through annual reports or product pages."
        )
"""

files[os.path.join(backend_path, "agents", "research", "geo_agent.py")] = """\
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
        self.global_keywords = [
            "global", "worldwide", "offices", "locations", "regions",
            "countries", "international", "across the world", "global presence"
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
"""

files[os.path.join(backend_path, "core", "report_generator.py")] = """\
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(report_data: dict, output_path: str) -> str:
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = styles['Title']
    heading1 = styles['Heading1']
    heading2 = styles['Heading2']
    normal = styles['Normal']
    
    elements = []
    
    # Title
    elements.append(Paragraph("Cyber Risk Underwriting Intelligence Report", title_style))
    elements.append(Spacer(1, 12))
    
    # Company Info
    elements.append(Paragraph(f"<b>Company:</b> {report_data.get('company_name', 'N/A')}", normal))
    elements.append(Paragraph(f"<b>Domain:</b> {report_data.get('domain', 'N/A')}", normal))
    elements.append(Paragraph(f"<b>Country:</b> {report_data.get('country', 'N/A')} | <b>Revenue:</b> {report_data.get('revenue_band', 'N/A')}", normal))
    elements.append(Paragraph(f"<b>Generated At:</b> {report_data.get('generated_at', 'N/A')}", normal))
    elements.append(Spacer(1, 20))
    
    # Risk Summary
    elements.append(Paragraph("Overall Risk Profile", heading1))
    data = [
        ["Overall Score", f"{report_data.get('overall_score', 0):.2f}"],
        ["Risk Category", report_data.get('overall_risk_category', 'Unknown')],
        ["Confidence", f"{report_data.get('overall_confidence', 0)*100:.0f}%"]
    ]
    t = Table(data, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))
    
    # Underwriter Summary
    elements.append(Paragraph("Underwriter Summary", heading2))
    elements.append(Paragraph(report_data.get('underwriter_summary', 'N/A').replace("\\n", "<br/>"), normal))
    elements.append(Spacer(1, 20))
    
    # Modifiers
    elements.append(Paragraph("Detailed Findings by Modifier", heading1))
    
    for mod in report_data.get('modifiers', []):
        elements.append(Paragraph(f"<b>{mod.get('modifier_name')}</b>", heading2))
        
        mod_data = [
            ["Score", str(mod.get('score'))],
            ["Category", mod.get('risk_category')],
            ["Verified", mod.get('verification_status')]
        ]
        t_mod = Table(mod_data, colWidths=[100, 350])
        t_mod.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(t_mod)
        elements.append(Spacer(1, 10))
        
        elements.append(Paragraph("<b>Findings:</b>", normal))
        for f in mod.get('findings', []):
            elements.append(Paragraph(f"- {f}", normal))
            
        elements.append(Paragraph("<b>Recommendation:</b>", normal))
        elements.append(Paragraph(mod.get('recommendation', 'None'), normal))
        elements.append(Spacer(1, 15))

    doc.build(elements)
    return output_path
"""

files[os.path.join(backend_path, "api", "routes.py")] = """\
import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from schemas.input_models import CompanyInput
from schemas.output_models import CyberRiskReport, ModifierResult
from agents.supervisor import SupervisorAgent
from agents.research.domain_agent import DomainAgent
from agents.research.privacy_agent import PrivacyAgent
from agents.research.ecommerce_agent import EcommerceAgent
from agents.research.customer_type_agent import CustomerTypeAgent
from agents.research.geo_agent import GeoAgent
from core.config import load_rules
from core.report_generator import generate_pdf_report
from utils.scraper import normalize_domain
import asyncio

router = APIRouter()

def get_outputs_dir():
    d = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(d, exist_ok=True)
    return d

@router.get("/modifiers")
def get_modifiers():
    rules = load_rules()
    enabled = [m for m, config in rules.items() if config.get("enabled", False)]
    return {"enabled_modifiers": enabled}

@router.post("/analyze-company", response_model=CyberRiskReport)
async def analyze_company(company: CompanyInput):
    supervisor = SupervisorAgent()
    try:
        company.domain = normalize_domain(company.domain)
        report = await supervisor.run_analysis(company)
        
        outputs_dir = get_outputs_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company = "".join([c if c.isalnum() else "_" for c in company.company_name]).lower()
        safe_domain = "".join([c if c.isalnum() else "_" for c in company.domain]).lower()
        
        filename = f"{safe_company}_{safe_domain}_{timestamp}.json"
        report.report_filename = filename
        
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
    company.domain = normalize_domain(company.domain)
    try:
        return await agents[modifier_name].run(company)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
def get_reports():
    outputs_dir = get_outputs_dir()
    files = [f for f in os.listdir(outputs_dir) if f.endswith(".json") and f != "sample_report.json"]
    return {"saved_reports": files}

@router.get("/reports/{filename}")
def get_report(filename: str):
    outputs_dir = get_outputs_dir()
    filepath = os.path.join(outputs_dir, filename)
    if not os.path.exists(filepath) or not filename.endswith(".json"):
        raise HTTPException(status_code=404, detail="Report not found")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/reports/{filename}/download-json")
def download_json(filename: str):
    outputs_dir = get_outputs_dir()
    filepath = os.path.join(outputs_dir, filename)
    if not os.path.exists(filepath) or not filename.endswith(".json"):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(filepath, filename=filename, media_type="application/json")

@router.get("/reports/{filename}/download-pdf")
def download_pdf(filename: str):
    outputs_dir = get_outputs_dir()
    filepath = os.path.join(outputs_dir, filename)
    if not os.path.exists(filepath) or not filename.endswith(".json"):
        raise HTTPException(status_code=404, detail="Report not found")
    
    pdf_filename = filename.replace(".json", ".pdf")
    pdf_filepath = os.path.join(outputs_dir, pdf_filename)
    
    if not os.path.exists(pdf_filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        try:
            generate_pdf_report(data, pdf_filepath)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {e}")
            
    return FileResponse(pdf_filepath, filename=pdf_filename, media_type="application/pdf")
"""

# Frontend Files
files[os.path.join(frontend_path, "src", "api", "cyberRiskApi.js")] = """\
import axios from 'axios';

const API_BASE_URL = "http://127.0.0.1:8000";
const api = axios.create({ baseURL: API_BASE_URL });

export const checkHealth = async () => (await api.get('/health')).data;
export const getModifiers = async () => (await api.get('/modifiers')).data;
export const analyzeCompany = async (payload) => (await api.post('/analyze-company', payload)).data;
export const runModifier = async (modifierName, payload) => (await api.post(`/run-modifier/${modifierName}`, payload)).data;
export const getReports = async () => (await api.get('/reports')).data;
export const getReportByFilename = async (filename) => (await api.get(`/reports/${filename}`)).data;

export const downloadJsonUrl = (filename) => `${API_BASE_URL}/reports/${filename}/download-json`;
export const downloadPdfUrl = (filename) => `${API_BASE_URL}/reports/${filename}/download-pdf`;
"""

files[os.path.join(frontend_path, "src", "styles", "App.css")] = """\
:root {
  --bg-color: #f8fafc;
  --header-bg: #1e293b;
  --header-text: #ffffff;
  --card-bg: #ffffff;
  --text-main: #1e293b;
  --text-muted: #64748b;
  --accent-blue: #2563eb;
  --accent-hover: #1d4ed8;
  --border-color: #e2e8f0;
  
  --risk-very-fav: #10b981;
  --risk-fav: #3b82f6;
  --risk-avg: #eab308;
  --risk-part-unfav: #f97316;
  --risk-unfav: #ef4444;
  --risk-unknown: #94a3b8;
}

body {
  margin: 0;
  font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-main);
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  background-color: var(--header-bg);
  color: var(--header-text);
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
}

.header p {
  margin: 0;
  color: #cbd5e1;
  font-size: 1.1rem;
}

.main-content {
  padding: 2rem;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
  border: 1px solid var(--border-color);
}

.card h2 {
  margin-top: 0;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0.75rem;
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  color: var(--text-main);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.form-group label {
  font-weight: 600;
  font-size: 0.9rem;
}
.form-group input, .form-group select {
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 1rem;
}

.btn {
  background-color: var(--accent-blue);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}
.btn:hover:not(:disabled) { background-color: var(--accent-hover); color: white; }
.btn:disabled { background-color: #cbd5e1; cursor: not-allowed; }
.btn-outline {
  background-color: transparent;
  color: var(--accent-blue);
  border: 1px solid var(--accent-blue);
}
.btn-outline:hover:not(:disabled) {
  background-color: #eff6ff;
  color: var(--accent-hover);
}

.demo-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}
.demo-btn {
  background: #f1f5f9;
  border: 1px solid var(--border-color);
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  cursor: pointer;
  color: var(--text-muted);
}
.demo-btn:hover { background: #e2e8f0; color: var(--text-main); }

.error-banner {
  background-color: #fef2f2;
  color: #991b1b;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #f87171;
  font-weight: 600;
  text-align: center;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.85rem;
  color: white;
  display: inline-block;
}

.risk-meter {
  display: flex;
  gap: 2px;
  margin: 1rem 0;
  border-radius: 8px;
  overflow: hidden;
}
.risk-meter-block {
  flex: 1;
  text-align: center;
  padding: 0.5rem;
  font-size: 0.75rem;
  font-weight: bold;
  color: white;
  opacity: 0.3;
  transition: opacity 0.3s;
}
.risk-meter-block.active { opacity: 1; transform: scale(1.05); }

.risk-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-stat {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  text-align: center;
}

table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  text-align: left;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}
th { background-color: #f8fafc; font-weight: 600; }

.modifier-details {
  background: #f8fafc;
  padding: 1.5rem;
  margin: 1rem 0;
  border-radius: 8px;
  border-left: 4px solid var(--accent-blue);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}
.loading-steps {
  margin-top: 1.5rem;
  text-align: left;
  color: var(--text-muted);
  list-style: none;
  padding: 0;
}
.loading-steps li { margin: 0.5rem 0; }

.report-item {
  background: #f8fafc;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.report-actions {
  display: flex;
  gap: 0.5rem;
}
"""

files[os.path.join(frontend_path, "src", "components", "Header.jsx")] = """\
import React from 'react';

export default function Header() {
  return (
    <header className="header">
      <h1>Emerging Risk Identifier</h1>
      <p>Cyber Risk Underwriting Intelligence Module</p>
      <p style={{fontSize: '0.9rem', marginTop: '0.5rem'}}>Agentic AI-powered cyber risk assessment with evidence-backed scoring.</p>
    </header>
  );
}
"""

files[os.path.join(frontend_path, "src", "components", "CompanyForm.jsx")] = """\
import React, { useState } from 'react';

export default function CompanyForm({ onSubmit, loading, disabled }) {
  const [formData, setFormData] = useState({
    company_name: '',
    domain: '',
    country: '',
    revenue_band: '> $1B',
    industry: ''
  });
  const [error, setError] = useState('');

  const demos = [
    { label: "Microsoft", data: { company_name: "Microsoft", domain: "microsoft.com", country: "USA", revenue_band: "> $1B", industry: "Technology" } },
    { label: "Apple", data: { company_name: "Apple", domain: "apple.com", country: "USA", revenue_band: "> $1B", industry: "Technology" } },
    { label: "Example.com", data: { company_name: "Example", domain: "example.com", country: "USA", revenue_band: "< $50M", industry: "Other" } },
    { label: "OpenAI", data: { company_name: "OpenAI", domain: "openai.com", country: "USA", revenue_band: "Unknown", industry: "Artificial Intelligence" } }
  ];

  const fillDemo = (data) => {
    setFormData(data);
    setError('');
  };

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.company_name || !formData.domain || !formData.country) {
      setError('Company Name, Domain, and Country are required.');
      return;
    }
    setError('');
    onSubmit(formData);
  };

  return (
    <div className="card">
      <h2>Analyze Company</h2>
      
      <div className="demo-buttons">
        <span style={{fontSize:'0.85rem', color:'#64748b', alignSelf:'center'}}>Demo:</span>
        {demos.map(d => (
          <button key={d.label} type="button" className="demo-btn" onClick={() => fillDemo(d.data)}>{d.label}</button>
        ))}
      </div>

      {error && <p style={{color: '#dc2626', fontSize: '0.9rem'}}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Company Name *</label>
          <input name="company_name" value={formData.company_name} onChange={handleChange} placeholder="e.g. Acme Corp" />
        </div>
        <div className="form-group">
          <label>Domain *</label>
          <input name="domain" value={formData.domain} onChange={handleChange} placeholder="e.g. acme.com or https://acme.com" />
        </div>
        <div className="form-group">
          <label>Country *</label>
          <input name="country" value={formData.country} onChange={handleChange} placeholder="e.g. USA" />
        </div>
        <div className="form-group">
          <label>Revenue Band</label>
          <select name="revenue_band" value={formData.revenue_band} onChange={handleChange}>
            <option>&gt; $1B</option>
            <option>$250M - $1B</option>
            <option>$50M - $250M</option>
            <option>&lt; $50M</option>
            <option>Unknown</option>
          </select>
        </div>
        <div className="form-group">
          <label>Industry</label>
          <input name="industry" value={formData.industry} onChange={handleChange} />
        </div>
        
        <button type="submit" className="btn" disabled={disabled || loading}>
          {loading ? 'Analyzing...' : 'Analyze Company'}
        </button>
      </form>
    </div>
  );
}
"""

files[os.path.join(frontend_path, "src", "components", "RiskSummary.jsx")] = """\
import React from 'react';
import { downloadJsonUrl, downloadPdfUrl } from '../api/cyberRiskApi';

export const getBadgeColor = (category) => {
  switch(category) {
    case 'Very Favorable': return 'var(--risk-very-fav)';
    case 'Favorable': return 'var(--risk-fav)';
    case 'Average': return 'var(--risk-avg)';
    case 'Partially Unfavorable': return 'var(--risk-part-unfav)';
    case 'Unfavorable': return 'var(--risk-unfav)';
    default: return 'var(--risk-unknown)';
  }
};

export const Badge = ({ category }) => (
  <span className="badge" style={{ backgroundColor: getBadgeColor(category) }}>
    {category}
  </span>
);

export default function RiskSummary({ report }) {
  if (!report) return null;

  const categories = [
    { label: "Very Favorable", val: "Very Favorable", color: "var(--risk-very-fav)" },
    { label: "Favorable", val: "Favorable", color: "var(--risk-fav)" },
    { label: "Average", val: "Average", color: "var(--risk-avg)" },
    { label: "Partially Unfav", val: "Partially Unfavorable", color: "var(--risk-part-unfav)" },
    { label: "Unfavorable", val: "Unfavorable", color: "var(--risk-unfav)" }
  ];

  return (
    <div className="card">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <h2 style={{border:'none', margin:0}}>Overall Cyber Risk Profile</h2>
        {report.report_filename && (
          <div style={{display:'flex', gap:'0.5rem'}}>
            <a href={downloadJsonUrl(report.report_filename)} className="btn btn-outline" download>Download JSON</a>
            <a href={downloadPdfUrl(report.report_filename)} className="btn btn-outline" target="_blank" rel="noreferrer">Download PDF</a>
          </div>
        )}
      </div>

      <div className="risk-meter">
        {categories.map(c => (
          <div key={c.label} 
               className={`risk-meter-block ${report.overall_risk_category === c.val ? 'active' : ''}`}
               style={{ backgroundColor: c.color }}>
            {c.label}
          </div>
        ))}
      </div>
      
      <div className="risk-summary-grid">
        <div className="summary-stat">
          <span style={{color:'var(--text-muted)', fontSize:'0.9rem'}}>Overall Score</span>
          <div style={{fontSize:'2rem', fontWeight:'bold'}}>{report.overall_score?.toFixed(2)}</div>
        </div>
        <div className="summary-stat">
          <span style={{color:'var(--text-muted)', fontSize:'0.9rem'}}>Confidence</span>
          <div style={{fontSize:'2rem', fontWeight:'bold'}}>{(report.overall_confidence * 100).toFixed(0)}%</div>
        </div>
        <div className="summary-stat" style={{gridColumn: 'span 2', textAlign:'left'}}>
          <h3 style={{margin:'0 0 0.5rem 0', fontSize:'1rem'}}>Underwriter Summary</h3>
          <p style={{margin:0, whiteSpace:'pre-wrap', lineHeight:1.5, color:'var(--text-main)'}}>{report.underwriter_summary}</p>
        </div>
      </div>
    </div>
  );
}
"""

files[os.path.join(frontend_path, "src", "components", "ModifierDetails.jsx")] = """\
import React from 'react';

export default function ModifierDetails({ mod }) {
  return (
    <div className="modifier-details">
      <h4 style={{marginTop:0}}>Findings</h4>
      <ul>{mod.findings.map((f, i) => <li key={i}>{f}</li>)}</ul>
      
      {mod.evidence && mod.evidence.length > 0 && (
        <>
          <h4>Evidence</h4>
          <ul>
            {mod.evidence.map((ev, i) => (
              <li key={i}>
                {ev.description}
                {ev.url && <> - <a href={ev.url} target="_blank" rel="noreferrer" style={{color:'var(--accent-blue)'}}>{ev.url}</a></>}
                {ev.status_code && ` (Status: ${ev.status_code})`}
              </li>
            ))}
          </ul>
        </>
      )}

      {mod.recommendation && (
        <>
          <h4>Recommendation</h4>
          <p style={{background:'#fef3c7', padding:'0.75rem', borderRadius:'6px', color:'#92400e', margin:0}}>
            {mod.recommendation}
          </p>
        </>
      )}
      
      {mod.raw_data && (
        <>
          <h4>Raw Data</h4>
          <pre style={{background:'#e2e8f0', padding:'1rem', borderRadius:'6px', fontSize:'0.85rem', overflowX:'auto'}}>
            {JSON.stringify(mod.raw_data, null, 2)}
          </pre>
        </>
      )}
    </div>
  );
}
"""

files[os.path.join(frontend_path, "src", "components", "ReportsList.jsx")] = """\
import React, { useState, useEffect } from 'react';
import { getReports, downloadJsonUrl, downloadPdfUrl } from '../api/cyberRiskApi';

export default function ReportsList({ onSelectReport }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const data = await getReports();
      setReports(data.saved_reports || []);
    } catch (err) {} finally { setLoading(false); }
  };

  useEffect(() => { fetchReports(); }, []);

  return (
    <div className="card">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1rem'}}>
        <h2 style={{border:'none', margin:0}}>Saved Reports</h2>
        <button onClick={fetchReports} className="btn btn-outline" style={{padding:'0.4rem 0.8rem', fontSize:'0.85rem'}}>Refresh</button>
      </div>
      
      {loading && <p>Loading...</p>}
      {!loading && reports.length === 0 && <p>No reports found.</p>}
      
      <div style={{display:'flex', flexDirection:'column', gap:'0.5rem'}}>
        {reports.map((filename, i) => (
          <div key={i} className="report-item">
            <span style={{fontWeight:600}}>{filename}</span>
            <div className="report-actions">
              <button onClick={() => onSelectReport(filename)} className="btn" style={{padding:'0.4rem 0.8rem', fontSize:'0.85rem'}}>View</button>
              <a href={downloadJsonUrl(filename)} className="btn btn-outline" style={{padding:'0.4rem 0.8rem', fontSize:'0.85rem'}} download>JSON</a>
              <a href={downloadPdfUrl(filename)} className="btn btn-outline" style={{padding:'0.4rem 0.8rem', fontSize:'0.85rem'}} target="_blank" rel="noreferrer">PDF</a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
"""

files[os.path.join(frontend_path, "src", "App.jsx")] = """\
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import CompanyForm from './components/CompanyForm';
import RiskSummary, { Badge } from './components/RiskSummary';
import ModifierDetails from './components/ModifierDetails';
import ReportsList from './components/ReportsList';
import { checkHealth, analyzeCompany, getReportByFilename } from './api/cyberRiskApi';

function App() {
  const [isHealthy, setIsHealthy] = useState(true);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [expandedMod, setExpandedMod] = useState({});

  useEffect(() => {
    checkHealth().then(() => setIsHealthy(true)).catch(() => setIsHealthy(false));
  }, []);

  const handleAnalyze = async (formData) => {
    setLoading(true); setReport(null);
    try {
      const data = await analyzeCompany(formData);
      setReport(data);
    } catch (err) {
      alert("Analysis failed. See console.");
    } finally { setLoading(false); }
  };

  const handleSelectReport = async (filename) => {
    setLoading(true); setReport(null);
    try {
      const data = await getReportByFilename(filename);
      setReport(data);
    } catch (err) {} finally { setLoading(false); }
  };

  const toggleMod = (name) => setExpandedMod(p => ({...p, [name]: !p[name]}));

  return (
    <div className="app-container">
      <Header />
      
      {!isHealthy && (
        <div style={{padding: '1rem 2rem'}}>
          <div className="error-banner">Backend is not reachable. Please start FastAPI server using python run.py.</div>
        </div>
      )}

      <main className="main-content">
        <div style={{display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) minmax(300px, 1.5fr)', gap: '2rem', alignItems: 'start'}}>
          <CompanyForm onSubmit={handleAnalyze} loading={loading} disabled={!isHealthy} />
          <ReportsList onSelectReport={handleSelectReport} />
        </div>

        {loading && (
          <div className="card loading-container">
            <h2 style={{border:'none', margin:0}}>Running cyber risk agents...</h2>
            <ul className="loading-steps">
              <li>🔍 Checking domain encryption...</li>
              <li>🛡️ Reviewing privacy posture...</li>
              <li>🛒 Detecting e-commerce signals...</li>
              <li>🏢 Identifying customer type...</li>
              <li>🌍 Estimating geographic spread...</li>
            </ul>
          </div>
        )}

        {report && !loading && (
          <div style={{display:'flex', flexDirection:'column', gap:'2rem', animation: 'fadeIn 0.5s ease'}}>
            <RiskSummary report={report} />
            
            <div className="card" style={{overflowX: 'auto'}}>
              <h2 style={{borderBottom:'none'}}>Modifier Assessments</h2>
              <table>
                <thead>
                  <tr>
                    <th>Modifier</th>
                    <th>Score</th>
                    <th>Category</th>
                    <th>Verified</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {report.modifiers.map((mod, idx) => (
                    <React.Fragment key={idx}>
                      <tr>
                        <td><strong>{mod.modifier_name}</strong></td>
                        <td>{mod.score}</td>
                        <td><Badge category={mod.risk_category} /></td>
                        <td style={{color: mod.verification_status==='verified'?'green': mod.verification_status==='partially_verified'?'orange':'red', fontWeight:600}}>
                          {mod.verification_status}
                        </td>
                        <td>
                          <button onClick={() => toggleMod(mod.modifier_name)} className="btn btn-outline" style={{padding:'0.4rem 0.8rem'}}>
                            {expandedMod[mod.modifier_name] ? 'Hide' : 'Details'}
                          </button>
                        </td>
                      </tr>
                      {expandedMod[mod.modifier_name] && (
                        <tr>
                          <td colSpan="5" style={{padding:0, borderBottom:'none'}}>
                            <ModifierDetails mod={mod} />
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
"""

def apply():
    for fpath, content in files.items():
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
            
    # requirements.txt update
    req_file = os.path.join(backend_path, "requirements.txt")
    if os.path.exists(req_file):
        with open(req_file, "r") as f:
            reqs = f.read()
        if "reportlab" not in reqs:
            with open(req_file, "a") as f:
                f.write("\\nreportlab==4.1.0\\n")

if __name__ == "__main__":
    apply()
