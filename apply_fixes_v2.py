import os

base_path = r"C:\Users\HP\3D Objects\multi-agent-cyber-rating-modifer"
backend_path = os.path.join(base_path, "cyber_risk_tool")
frontend_path = os.path.join(base_path, "frontend")

files = {}

# 1. Output Models
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
    generated_at: Optional[datetime] = None
    generated_at_utc: Optional[datetime] = None
    generated_at_local: Optional[str] = None
    timezone: Optional[str] = "IST"
    report_filename: Optional[str] = None
"""

# 2. Supervisor Agent
files[os.path.join(backend_path, "agents", "supervisor.py")] = """\
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
from zoneinfo import ZoneInfo
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
        agents = [
            self.domain_agent,
            self.privacy_agent,
            self.ecommerce_agent,
            self.customer_agent,
            self.geo_agent
        ]
        
        tasks = [agent.run(company) for agent in agents]
        modifier_results = await asyncio.gather(*tasks)
        
        verified_results = self.fact_checker.verify(modifier_results)
        
        overall_score, risk_category, overall_confidence = self.scoring_engine.calculate_score(verified_results)
        
        all_unknown = all(m.risk_category == "Unknown" or m.verification_status == "not_verified" for m in verified_results)
        if all_unknown or overall_confidence < 0.25:
            risk_category = "Manual Review Required"
        
        summary = self.underwriter.generate_summary(company, verified_results, overall_score, risk_category)
        
        generated_at_utc = datetime.now(ZoneInfo("UTC"))
        generated_at_local = generated_at_utc.astimezone(ZoneInfo("Asia/Kolkata"))
        formatted_local = generated_at_local.strftime("%d-%b-%Y %I:%M %p IST")
        
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
            generated_at_utc=generated_at_utc,
            generated_at_local=formatted_local,
            timezone="IST"
        )
"""

# 3. Underwriter Agent
files[os.path.join(backend_path, "agents", "underwriter.py")] = """\
from typing import List
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult

class UnderwriterAgent:
    def generate_summary(self, company: CompanyInput, modifiers: List[ModifierResult], score: float, risk_category: str) -> str:
        if risk_category == "Manual Review Required":
            return (
                "Overall Risk Category: Manual Review Required\n"
                "Key Favorable Indicators: None verified\n"
                "Key Risk Indicators: Website/domain could not be reached\n"
                "Recommended Underwriting Review Points: Validate the company domain manually, confirm website availability, and collect alternative evidence before underwriting decision."
            )
            
        fav = [m.modifier_name for m in modifiers if m.risk_category in ("Favorable", "Very Favorable")]
        mod_risk = [m.modifier_name for m in modifiers if m.risk_category == "Average"]
        unfav = [m.modifier_name for m in modifiers if m.risk_category in ("Partially Unfavorable", "Unfavorable")]
        
        review_points = unfav if unfav else (mod_risk if mod_risk else fav)
        
        summary = (
            f"Overall Risk Category: {risk_category}\n"
            f"Key Favorable Indicators: {', '.join(fav) if fav else 'None'}\n"
            f"Key Risk Indicators: {', '.join(unfav) if unfav else 'None'}\n"
            f"Recommended Underwriting Review Points: Focus on validating {', '.join(review_points)}."
        )
        return summary
"""

# 4. Domain Agent
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

        if access_restricted:
            score = 2.0
            risk_category = "Average"
            confidence = 0.60
            findings.append("HTTPS endpoint appears reachable but automated access was restricted.")
        elif https_working and redirects_to_https:
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
            recommendation="Ensure HTTPS is enforced and all HTTP traffic redirects to HTTPS." if score > 1.0 and not access_restricted else "Maintain current encryption standards."
        )
"""

# 5. Privacy Agent
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
            "/legal", "/terms", "/privacy", "/privacy-policy", "/privacy-notice", 
            "/legal/privacy", "/privacy.html", "/cookie-policy"
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

# 6. Report Generator
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
    
    gen_time = report_data.get('generated_at_local')
    if not gen_time:
        gen_time = report_data.get('generated_at', 'N/A')
    elements.append(Paragraph(f"<b>Generated At:</b> {gen_time}", normal))
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
            if raw.get('access_restricted'):
                details.append(f"- Access Restricted: Yes")
                details.append(f"- Blocked Status Code: {raw.get('blocked_status_code')}")
                details.append(f"- Manual Verification Required: Yes")
                
            for d in details:
                elements.append(Paragraph(d, normal))
            
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>Recommendation:</b>", normal))
        elements.append(Paragraph(mod.get('recommendation', 'None'), normal))
        elements.append(Spacer(1, 15))

    doc.build(elements)
    return output_path
"""

# 7. RiskSummary Frontend
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
    case 'Manual Review Required': return '#475569'; // slate-600
    case 'Unknown': return 'var(--risk-unknown)';
    default: return 'var(--risk-unknown)';
  }
};

export const Badge = ({ category }) => (
  <span className="badge" style={{ backgroundColor: getBadgeColor(category) }}>
    {category}
  </span>
);

export default function RiskSummary({ report, addToast }) {
  if (!report) return null;

  const categories = [
    { label: "Very Favorable", val: "Very Favorable", color: "var(--risk-very-fav)" },
    { label: "Favorable", val: "Favorable", color: "var(--risk-fav)" },
    { label: "Average", val: "Average", color: "var(--risk-avg)" },
    { label: "Partially Unfav", val: "Partially Unfavorable", color: "var(--risk-part-unfav)" },
    { label: "Unfavorable", val: "Unfavorable", color: "var(--risk-unfav)" }
  ];
  
  const domainMod = report.modifiers.find(m => m.modifier_name === 'Domain Encryption');
  const normalizedDomain = domainMod?.raw_data?.normalized_domain || report.domain;
  
  const genTime = report.generated_at_local || (report.generated_at ? new Date(report.generated_at).toLocaleString() : 'Unknown');

  return (
    <div>
      <div className="card" style={{marginBottom: '2rem'}}>
        <h2 style={{borderBottom:'none', margin:0, marginBottom:'1rem'}}>Company Details</h2>
        <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(250px, 1fr))', gap:'1.5rem', fontSize:'0.95rem'}}>
          <div><strong style={{color:'var(--text-muted)'}}>Company</strong><br/><span style={{fontSize:'1.1rem', fontWeight:600}}>{report.company_name}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Input Domain</strong><br/><span style={{fontSize:'1.1rem'}}>{report.domain}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Normalized Domain</strong><br/><span style={{fontSize:'1.1rem', color:'var(--accent-blue)', fontWeight:600}}>{normalizedDomain}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Country</strong><br/><span style={{fontSize:'1.1rem'}}>{report.country}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Revenue Band</strong><br/><span style={{fontSize:'1.1rem'}}>{report.revenue_band}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Industry</strong><br/><span style={{fontSize:'1.1rem'}}>{report.industry || 'N/A'}</span></div>
          <div><strong style={{color:'var(--text-muted)'}}>Report Generated At</strong><br/><span>{genTime}</span></div>
        </div>
      </div>

      <div className="card">
        <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:'1rem'}}>
          <h2 style={{border:'none', margin:0}}>Overall Cyber Risk Profile</h2>
          {report.report_filename && (
            <div style={{display:'flex', gap:'0.5rem'}}>
              <a href={downloadJsonUrl(report.report_filename)} className="btn btn-outline" download onClick={() => addToast('JSON downloaded successfully')}>Download JSON</a>
              <a href={downloadPdfUrl(report.report_filename)} className="btn" target="_blank" rel="noreferrer" onClick={() => addToast('PDF downloaded successfully')}>Download PDF</a>
            </div>
          )}
        </div>
        
        {report.overall_confidence < 0.25 && (
            <div style={{background: '#fffbeb', border: '1px solid #fde68a', color: '#b45309', padding: '1rem', borderRadius: '8px', marginTop: '1rem', fontWeight: 600}}>
                ⚠️ Low confidence result. Manual validation is recommended.
            </div>
        )}

        <div style={{textAlign:'center', marginTop:'2rem', marginBottom:'0.5rem', fontWeight:600, fontSize:'1.1rem'}}>
          Current Position: <span style={{color: getBadgeColor(report.overall_risk_category)}}>{report.overall_risk_category}</span>
        </div>
        
        <div className="risk-meter" style={{height:'40px', borderRadius:'8px', overflow:'hidden', position:'relative'}}>
          {categories.map(c => (
            <div key={c.label} 
                 className={`risk-meter-block ${report.overall_risk_category === c.val ? 'active' : ''}`}
                 style={{ 
                   backgroundColor: c.color, 
                   opacity: report.overall_risk_category === c.val ? 1 : 0.4,
                   display: 'flex', flexDirection: 'column', alignItems:'center', justifyContent:'center',
                 }}>
              {c.label}
            </div>
          ))}
        </div>
        <div style={{display:'flex', height:'10px'}}>
          {categories.map(c => (
            <div key={c.label} style={{flex:1, display:'flex', justifyContent:'center'}}>
              {report.overall_risk_category === c.val && (
                 <div style={{width:0, height:0, borderLeft:'10px solid transparent', borderRight:'10px solid transparent', borderTop:`10px solid ${c.color}`}}></div>
              )}
            </div>
          ))}
        </div>
        
        <div className="risk-summary-grid" style={{marginTop:'2rem'}}>
          <div className="summary-stat">
            <span style={{color:'var(--text-muted)', fontSize:'0.9rem', textTransform:'uppercase', letterSpacing:'1px', fontWeight:600}}>Overall Score</span>
            <div style={{fontSize:'3rem', fontWeight:'800', color: 'var(--text-main)'}}>{report.overall_score?.toFixed(2)}</div>
          </div>
          
          <div className="summary-stat" style={{backgroundColor: getBadgeColor(report.overall_risk_category), color:'white', border:'none', display:'flex', flexDirection:'column', justifyContent:'center'}}>
            <span style={{fontSize:'0.9rem', opacity:0.9, textTransform:'uppercase', letterSpacing:'1px', fontWeight:600}}>Risk Category</span>
            <div style={{fontSize: report.overall_risk_category === 'Manual Review Required' ? '1.8rem' : '2.2rem', fontWeight:'800', marginTop:'0.5rem', lineHeight:1.2}}>{report.overall_risk_category}</div>
          </div>

          <div className="summary-stat">
            <span style={{color:'var(--text-muted)', fontSize:'0.9rem', textTransform:'uppercase', letterSpacing:'1px', fontWeight:600}}>Confidence</span>
            <div style={{fontSize:'3rem', fontWeight:'800', color: 'var(--text-main)'}}>{(report.overall_confidence * 100).toFixed(0)}%</div>
          </div>
          
          <div className="summary-stat" style={{gridColumn: '1 / -1', textAlign:'left', padding:'2rem'}}>
            <h3 style={{margin:'0 0 1rem 0', fontSize:'1.2rem', color:'var(--text-main)'}}>Underwriter Summary</h3>
            <p style={{margin:0, whiteSpace:'pre-wrap', lineHeight:1.6, color:'var(--text-main)', fontSize:'1.05rem'}}>{report.underwriter_summary}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
"""

# 8. App Frontend (table view badge status colors)
files[os.path.join(frontend_path, "src", "App.jsx")] = """\
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import CompanyForm from './components/CompanyForm';
import RiskSummary, { Badge, getBadgeColor } from './components/RiskSummary';
import ModifierDetails from './components/ModifierDetails';
import ReportsList from './components/ReportsList';
import { checkHealth, analyzeCompany, getReportByFilename } from './api/cyberRiskApi';

function App() {
  const [isHealthy, setIsHealthy] = useState(true);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [selectedMod, setSelectedMod] = useState(null);
  const [toasts, setToasts] = useState([]);

  const addToast = (msg, type='success') => {
    const id = Date.now();
    setToasts(p => [...p, {id, msg, type}]);
    setTimeout(() => setToasts(p => p.filter(t => t.id !== id)), 3000);
  };

  useEffect(() => {
    checkHealth().then(() => setIsHealthy(true)).catch(() => {
      setIsHealthy(false);
      addToast('Backend not reachable', 'error');
    });
  }, []);

  const handleAnalyze = async (formData) => {
    setLoading(true); setReport(null);
    try {
      const data = await analyzeCompany(formData);
      setReport(data);
      addToast('Report generated successfully');
    } catch (err) {
      addToast('Something went wrong generating report', 'error');
    } finally { setLoading(false); }
  };

  const handleSelectReport = async (filename) => {
    setLoading(true); setReport(null);
    try {
      const data = await getReportByFilename(filename);
      setReport(data);
      addToast('Report loaded successfully');
    } catch (err) {
      addToast('Something went wrong loading report', 'error');
    } finally { setLoading(false); }
  };

  return (
    <div className="app-container">
      <Header />
      
      {!isHealthy && (
        <div style={{padding: '1rem 2rem'}}>
          <div className="error-banner">Backend is not reachable. Please start FastAPI server using python run.py.</div>
        </div>
      )}

      <main className="main-content">
        <div style={{display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) minmax(300px, 1fr)', gap: '2rem', alignItems: 'start'}}>
          <CompanyForm onSubmit={handleAnalyze} loading={loading} disabled={!isHealthy} />
          <ReportsList onSelectReport={handleSelectReport} addToast={addToast} />
        </div>

        {loading && (
          <div className="card loading-container">
            <h2 style={{border:'none', margin:0, fontSize:'1.8rem', color:'var(--accent-blue)'}}>Running Agentic Cyber Risk Workflow...</h2>
            <ul className="loading-steps">
              <li>⚙️ Normalizing domain and entity resolution</li>
              <li>🔍 Checking HTTPS encryption algorithms</li>
              <li>🛡️ Reviewing privacy policy and GDPR/CCPA presence</li>
              <li>🛒 Detecting e-commerce and checkout exposure</li>
              <li>🏢 Identifying B2B vs B2C customer profile</li>
              <li>🌍 Estimating global geographic spread</li>
              <li>📑 Validating evidence links securely</li>
              <li>🤖 Generating professional underwriter summary</li>
            </ul>
          </div>
        )}

        {report && !loading && (
          <div style={{display:'flex', flexDirection:'column', gap:'2rem', animation: 'fadeIn 0.5s ease'}}>
            <RiskSummary report={report} addToast={addToast} />
            
            <div className="card" style={{overflowX: 'auto'}}>
              <h2 style={{borderBottom:'none'}}>Modifier Assessments</h2>
              <table>
                <thead>
                  <tr>
                    <th>Modifier</th>
                    <th>Score</th>
                    <th>Risk Category</th>
                    <th>Verification</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {report.modifiers.map((mod, idx) => (
                    <tr key={idx}>
                      <td><strong>{mod.modifier_name}</strong></td>
                      <td><span style={{fontWeight:800, fontSize:'1.1rem'}}>{mod.score}</span></td>
                      <td>
                        <span style={{color: getBadgeColor(mod.risk_category), fontWeight:700, display:'flex', alignItems:'center', gap:'0.25rem'}}>
                          <div style={{width:'8px', height:'8px', borderRadius:'50%', background: getBadgeColor(mod.risk_category)}}></div>
                          {mod.risk_category}
                        </span>
                      </td>
                      <td>
                        <span style={{
                          padding:'0.2rem 0.6rem', borderRadius:'99px', fontSize:'0.8rem', fontWeight:700,
                          background: mod.verification_status==='verified' ? '#dcfce7' : mod.verification_status==='partially_verified' ? '#fef3c7' : '#fee2e2',
                          color: mod.verification_status==='verified' ? '#166534' : mod.verification_status==='partially_verified' ? '#92400e' : '#991b1b'
                        }}>
                          {mod.verification_status?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
                        </span>
                      </td>
                      <td>
                        <button onClick={() => setSelectedMod(mod)} className="btn btn-outline" style={{padding:'0.4rem 1rem', fontSize:'0.85rem'}}>
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        Emerging Risk Identifier | Cyber Risk Module | MVP Demo
      </footer>

      {selectedMod && (
        <div className="modal-overlay" onClick={() => setSelectedMod(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedMod(null)}>&times;</button>
            <ModifierDetails mod={selectedMod} />
          </div>
        </div>
      )}

      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast ${t.type}`}>{t.msg}</div>
        ))}
      </div>
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

if __name__ == "__main__":
    apply()
