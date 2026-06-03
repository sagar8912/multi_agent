import os

base_path = r"C:\Users\HP\3D Objects\multi-agent-cyber-rating-modifer"
backend_path = os.path.join(base_path, "cyber_risk_tool")
frontend_path = os.path.join(base_path, "frontend")

files = {}

# 1. Scraper
files[os.path.join(backend_path, "utils", "scraper.py")] = """\
import httpx
from bs4 import BeautifulSoup
from typing import Tuple, List, Optional
from urllib.parse import urlparse, urljoin
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

def normalize_domain(domain: str) -> str:
    domain = domain.strip().lower()
    if not domain.startswith("http://") and not domain.startswith("https://"):
        domain = "http://" + domain
    
    parsed = urlparse(domain)
    netloc = parsed.netloc
    
    if netloc.startswith("www."):
        netloc = netloc[4:]
        
    return netloc

def build_url(domain: str, scheme: str = "https") -> str:
    return f"{scheme}://{normalize_domain(domain)}"

async def fetch_url(url: str, timeout: int = 10) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=timeout, headers=headers) as client:
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

# 2. Domain Agent
files[os.path.join(backend_path, "agents", "research", "domain_agent.py")] = """\
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
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with httpx.AsyncClient(verify=True, follow_redirects=True, timeout=10, headers=headers) as client:
            # Test HTTPS
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
                    else:
                        evidence.append(Evidence(url=url, description="HTTPS returned error code", status_code=resp.status_code))
                except Exception as e:
                    errors.append(f"{url}: {e}")
                    evidence.append(Evidence(url=url, description=f"HTTPS failed: {e}", status_code=None))
            
            # Test HTTP
            for url in urls_to_test[2:]:
                tested_urls.append(url)
                try:
                    resp = await client.get(url)
                    if 200 <= resp.status_code < 400:
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

        # Scoring Logic
        if https_working and redirects_to_https:
            score = 1.0
            risk_category = "Favorable"
            confidence = 0.95
            findings.append("Valid HTTPS and HTTP redirects to HTTPS.")
        elif https_working and not redirects_to_https:
            score = 2.0
            risk_category = "Average"
            confidence = 0.80
            findings.append("HTTPS is available, but HTTP-to-HTTPS redirect could not be fully confirmed.")
        elif not https_working and http_working:
            score = 4.0
            risk_category = "Unfavorable"
            confidence = 0.70
            findings.append("HTTPS could not be verified but HTTP is reachable.")
        else:
            score = 3.0
            risk_category = "Unknown"
            confidence = 0.30
            findings.append("Website could not be reached.")

        raw_data = {
            "input_domain": original_domain,
            "normalized_domain": domain,
            "tested_urls": tested_urls,
            "https_working": https_working,
            "http_working": http_working,
            "redirects_to_https": redirects_to_https,
            "final_https_url": final_https_url,
            "final_http_url": final_http_url,
            "https_status_code": https_status,
            "http_status_code": http_status,
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
            recommendation="Ensure HTTPS is enforced and all HTTP traffic redirects to HTTPS." if score > 1.0 else "Maintain current encryption standards."
        )
"""

# 3. Privacy Agent
files[os.path.join(backend_path, "agents", "research", "privacy_agent.py")] = """\
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult, Evidence
from utils.scraper import build_url, fetch_url, extract_text_from_html, extract_links
from utils.text_utils import find_keywords
import asyncio

class PrivacyAgent:
    def __init__(self):
        self.privacy_paths = [
            "/policies/privacy-policy", "/policies/row-privacy-policy", "/policies",
            "/privacy", "/privacy-policy", "/privacy-notice", 
            "/legal/privacy", "/privacy.html", "/legal", "/terms", "/cookie-policy"
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

# 4. Report Generator
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
    
    elements.append(Paragraph("Cyber Risk Underwriting Intelligence Report", title_style))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph(f"<b>Company:</b> {report_data.get('company_name', 'N/A')}", normal))
    elements.append(Paragraph(f"<b>Domain:</b> {report_data.get('domain', 'N/A')}", normal))
    elements.append(Paragraph(f"<b>Country:</b> {report_data.get('country', 'N/A')} | <b>Revenue:</b> {report_data.get('revenue_band', 'N/A')}", normal))
    elements.append(Paragraph(f"<b>Generated At:</b> {report_data.get('generated_at', 'N/A')}", normal))
    elements.append(Spacer(1, 20))
    
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
    
    elements.append(Paragraph("Underwriter Summary", heading2))
    elements.append(Paragraph(report_data.get('underwriter_summary', 'N/A').replace("\\n", "<br/>"), normal))
    elements.append(Spacer(1, 20))
    
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
            
        if mod.get('modifier_name') == "Domain Encryption" and mod.get('raw_data'):
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("<b>Domain Encryption Details:</b>", normal))
            raw = mod.get('raw_data')
            details = [
                f"- Normalized Domain: {raw.get('normalized_domain')}",
                f"- HTTPS Working: {raw.get('https_working')}",
                f"- HTTP Redirects to HTTPS: {raw.get('redirects_to_https')}",
                f"- Final HTTPS URL: {raw.get('final_https_url')}",
                f"- HTTPS Status Code: {raw.get('https_status_code')}"
            ]
            for d in details:
                elements.append(Paragraph(d, normal))
            
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>Recommendation:</b>", normal))
        elements.append(Paragraph(mod.get('recommendation', 'None'), normal))
        elements.append(Spacer(1, 15))

    doc.build(elements)
    return output_path
"""

# 5. Frontend RiskSummary
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
  
  const domainMod = report.modifiers.find(m => m.modifier_name === 'Domain Encryption');

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
      
      <div style={{fontSize:'0.9rem', color:'var(--text-muted)', margin:'1rem 0'}}>
        <strong>Input Domain:</strong> {report.domain} <br/>
        {domainMod?.raw_data?.normalized_domain && (
          <><strong>Normalized Domain:</strong> {domainMod.raw_data.normalized_domain}</>
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


def apply():
    for fpath, content in files.items():
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    apply()
