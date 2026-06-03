import os
import json
import re
from datetime import datetime
import pathlib
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
    return re.sub(r"[^a-zA-Z0-9_]+", "_", str(value)).strip("_").lower()

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
            outputs_dir = pathlib.Path(get_outputs_dir())
            outputs_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s_company = safe_filename(company.company_name)
            s_domain = safe_filename(report.normalized_domain or company.domain)
            
            filename = f"{s_company}_{s_domain}_{timestamp}.json"
            filepath = outputs_dir / filename
            
            report_dict = report.model_dump()
            report_dict["report_filename"] = filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report_dict, f, indent=2, default=str)
            report.report_filename = filename
        except Exception as save_err:
            logger.exception(f"Failed to save report: {save_err}")
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
