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
    reason_for_score: Optional[str] = None
    status: Optional[str] = None
    phase: Optional[str] = None
    description: Optional[str] = None
    target_parameter: Optional[str] = None
    research_needed: Optional[str] = None

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
    category_reason: Optional[str] = None
    top_positive_drivers: List[str] = []
    top_negative_drivers: List[str] = []
    manual_review_required: bool = False
    evidence_quality: str = "Medium"
    is_valid_domain: bool = True
    validation_error: Optional[str] = None
    placeholder_detected: Optional[bool] = None
    business_validity_status: Optional[str] = None
    modifiers: List[ModifierResult]
    underwriter_summary: str
    generated_at: Optional[str] = None
    generated_at_utc: Optional[str] = None
    generated_at_local: Optional[str] = None
    timezone: Optional[str] = "IST"
    report_filename: Optional[str] = None
