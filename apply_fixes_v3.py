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
    normalized_domain: Optional[str] = None
    country: str
    revenue_band: str
    industry: Optional[str]
    overall_score: float
    overall_risk_category: str
    overall_confidence: float
    modifiers: List[ModifierResult]
    underwriter_summary: str
    generated_at: Optional[str] = None
    generated_at_utc: Optional[str] = None
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
from utils.scraper import normalize_domain
import asyncio

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

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
        
        if ZoneInfo:
            utc_now = datetime.now(ZoneInfo("UTC"))
            ist_now = utc_now.astimezone(ZoneInfo("Asia/Kolkata"))
            generated_at_utc = utc_now.isoformat()
            formatted_local = ist_now.strftime("%d-%b-%Y %I:%M %p IST")
        else:
            now = datetime.now()
            generated_at_utc = now.isoformat()
            formatted_local = now.strftime("%d-%b-%Y %I:%M %p")

        norm_domain = normalize_domain(company.domain)
        
        return CyberRiskReport(
            company_name=company.company_name,
            domain=company.domain,
            normalized_domain=norm_domain,
            country=company.country,
            revenue_band=company.revenue_band,
            industry=company.industry,
            overall_score=overall_score,
            overall_risk_category=risk_category,
            overall_confidence=overall_confidence,
            modifiers=verified_results,
            underwriter_summary=summary,
            generated_at=formatted_local,
            generated_at_utc=generated_at_utc,
            generated_at_local=formatted_local,
            timezone="IST"
        )
"""

# 3. API Routes
files[os.path.join(backend_path, "api", "routes.py")] = """\
import os
import json
import re
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
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

def get_outputs_dir():
    d = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(d, exist_ok=True)
    return d

def safe_filename(value):
    return re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_").lower()

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
        
        try:
            outputs_dir = get_outputs_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s_company = safe_filename(company.company_name)
            s_domain = safe_filename(report.normalized_domain or company.domain)
            
            filename = f"{s_company}_{s_domain}_{timestamp}.json"
            report.report_filename = filename
            
            filepath = os.path.join(outputs_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report.model_dump_json(indent=2))
        except Exception as save_err:
            logger.error(f"Failed to save report: {save_err}")
            report.report_filename = None
            
        return report
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
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

# 4. Frontend API Handle
files[os.path.join(frontend_path, "src", "api", "cyberRiskApi.js")] = """\
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const checkHealth = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/health`);
        return response.data;
    } catch (error) {
        console.error("Health check failed:", error);
        throw error;
    }
};

export const analyzeCompany = async (companyData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/analyze-company`, companyData);
        return response.data;
    } catch (error) {
        console.error("Analyze company failed:", error.response?.data || error.message);
        throw error;
    }
};

export const getModifiers = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/modifiers`);
        return response.data;
    } catch (error) {
        console.error("Get modifiers failed:", error);
        throw error;
    }
};

export const getReports = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/reports`);
        return response.data;
    } catch (error) {
        console.error("Get reports failed:", error);
        throw error;
    }
};

export const getReportByFilename = async (filename) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/reports/${filename}`);
        return response.data;
    } catch (error) {
        console.error("Get report failed:", error);
        throw error;
    }
};

export const downloadJsonUrl = (filename) => {
    return `${API_BASE_URL}/reports/${filename}/download-json`;
};

export const downloadPdfUrl = (filename) => {
    return `${API_BASE_URL}/reports/${filename}/download-pdf`;
};
"""


def apply():
    for fpath, content in files.items():
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    apply()
