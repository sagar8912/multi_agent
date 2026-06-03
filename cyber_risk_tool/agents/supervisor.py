from schemas.input_models import CompanyInput
from schemas.output_models import CyberRiskReport, ModifierResult
from agents.research.domain_agent import DomainAgent
from agents.research.privacy_agent import PrivacyAgent
from agents.research.geo_agent import GeoAgent
from agents.research.amount_sensitive_information_agent import AmountSensitiveInformationAgent
from agents.research.internet_footprint_agent import InternetFootprintAgent
from agents.research.nature_of_services_agent import NatureOfServicesAgent
from agents.research.mergers_acquisitions_agent import MergersAcquisitionsAgent
from agents.research.organizational_complexity_agent import OrganizationalComplexityAgent
from agents.research.seasonality_sales_agent import SeasonalitySalesAgent
from agents.research.volatility_recovery_sales_agent import VolatilityRecoverySalesAgent
from agents.fact_checker import FactCheckerAgent
from agents.underwriter import UnderwriterAgent
from core.scoring_engine import ScoringEngine
from core.config import load_rules
from datetime import datetime
from utils.scraper import normalize_domain, fetch_homepage
from utils.business_validator import check_business_validity
from utils.domain_validator import validate_domain
import asyncio

from zoneinfo import ZoneInfo

def get_generated_timestamps():
    try:
        utc_now = datetime.now(ZoneInfo("UTC"))
        ist_now = utc_now.astimezone(ZoneInfo("Asia/Kolkata"))
        return {
            "generated_at": ist_now.strftime("%d-%b-%Y %I:%M %p IST"),
            "generated_at_utc": utc_now.isoformat(),
            "generated_at_local": ist_now.strftime("%d-%b-%Y %I:%M %p IST"),
            "timezone": "IST"
        }
    except Exception:
        now = datetime.now()
        return {
            "generated_at": now.strftime("%d-%b-%Y %I:%M %p"),
            "generated_at_utc": now.isoformat(),
            "generated_at_local": now.strftime("%d-%b-%Y %I:%M %p"),
            "timezone": "Local"
        }

class SupervisorAgent:
    def __init__(self):
        self.domain_agent = DomainAgent()
        self.privacy_agent = PrivacyAgent()
        self.geo_agent = GeoAgent()
        self.amount_sensitive_info_agent = AmountSensitiveInformationAgent()
        self.internet_footprint_agent = InternetFootprintAgent()
        self.nature_of_services_agent = NatureOfServicesAgent()
        self.mergers_agent = MergersAcquisitionsAgent()
        self.org_complexity_agent = OrganizationalComplexityAgent()
        self.seasonality_agent = SeasonalitySalesAgent()
        self.volatility_agent = VolatilityRecoverySalesAgent()
        
        self.fact_checker = FactCheckerAgent()
        self.underwriter = UnderwriterAgent()
        self.scoring_engine = ScoringEngine()
        self.rules = load_rules()

    async def run_analysis(self, company: CompanyInput) -> CyberRiskReport:
        if company.demo_mode and company.demo_profile:
            return self._get_demo_report(company)
            
        is_valid, validation_error = validate_domain(company.domain)
        if not is_valid:
            return self._get_invalid_domain_report(company, validation_error)
            
        html_text, status, final_url = await fetch_homepage(company.domain)
        is_placeholder, placeholder_reason = check_business_validity(html_text)

        agents = [
            self.domain_agent,
            self.privacy_agent,
            self.geo_agent,
            self.amount_sensitive_info_agent,
            self.internet_footprint_agent,
            self.nature_of_services_agent,
            self.mergers_agent,
            self.org_complexity_agent,
            self.seasonality_agent,
            self.volatility_agent
        ]
        
        tasks = [agent.run(company) for agent in agents]
        modifier_results = await asyncio.gather(*tasks)
        
        verified_results = self.fact_checker.verify(modifier_results)
        
        # Inject metadata
        for res in verified_results:
            # map name to key
            key = res.modifier_name.lower().replace(" ", "_").replace("/", "").replace("__", "_")
            if key == "amount_of_sensitive_information": key = "amount_of_sensitive_information"
            elif key == "volatility__recovery_in_sales": key = "volatility_recovery_in_sales"
            elif key == "volatility_recovery_in_sales": key = "volatility_recovery_in_sales"
            elif key == "mergers_and_acquisitions": key = "mergers_and_acquisitions"
            
            rule = self.rules.get(key, {})
            res.phase = rule.get("phase", "Active")
            res.description = rule.get("description", "")
            res.target_parameter = rule.get("target_parameter", "")
            res.research_needed = rule.get("research_needed", "")
            if not res.status:
                if res.phase == "Phase 2": res.status = "not_implemented_phase_2"
                elif res.phase == "Partial MVP": res.status = "partial_mvp"
                else: res.status = "active"
        
        overall_score, risk_category, overall_confidence = self.scoring_engine.calculate_score(verified_results)
        
        manual_review_required = False
        unknown_count = sum(1 for m in verified_results if m.risk_category == "Unknown" or m.verification_status == "not_verified")
        
        # Calculate Evidence Quality (only active modifiers)
        active_results = [m for m in verified_results if m.status == "active"]
        verified_count = sum(1 for m in active_results if m.risk_category != "Unknown" and m.verification_status != "not_verified")
        
        domain_reachable = status is not None and status < 400
        privacy_found = any(m.modifier_name == "Privacy Regulation" and m.risk_category != "Unknown" for m in active_results)
        sensitive_known = any(m.modifier_name == "Amount of Sensitive Information" and m.risk_category != "Unknown" for m in active_results)
        
        if is_placeholder:
            evidence_quality = "Low"
            manual_review_required = True
        elif not domain_reachable or (not privacy_found and not sensitive_known):
            evidence_quality = "Low"
        elif verified_count >= 3 and privacy_found and sensitive_known:
            evidence_quality = "High"
        elif verified_count >= 2:
            evidence_quality = "Medium"
        else:
            evidence_quality = "Low"
            
        if overall_confidence < 0.25 or unknown_count > len(verified_results) / 2:
            manual_review_required = True
            
        # Apply Overrides
        risk_category = self.scoring_engine.apply_overrides(
            risk_category=risk_category,
            manual_review_required=manual_review_required,
            evidence_quality=evidence_quality,
            modifiers=verified_results,
            overall_confidence=overall_confidence
        )
        if is_placeholder:
            risk_category = "Manual Review Required"
            
        top_positive_drivers = [m.modifier_name for m in verified_results if m.score <= 2.0 and m.risk_category != "Unknown" and m.status != "not_implemented_phase_2"]
        top_negative_drivers = [m.modifier_name for m in verified_results if m.score >= 3.0 and m.risk_category != "Unknown" and m.status != "not_implemented_phase_2"]
        
        summary = self.underwriter.generate_summary(company, verified_results, overall_score, risk_category)
        
        if is_placeholder:
            summary = "The website appears to be a placeholder or lacks sufficient business-specific evidence. Manual underwriting validation is required."
        
        timestamps = get_generated_timestamps()
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
            category_reason=f"Overall score {overall_score:.2f} falls into {risk_category} category.",
            top_positive_drivers=top_positive_drivers,
            top_negative_drivers=top_negative_drivers,
            manual_review_required=manual_review_required,
            evidence_quality=evidence_quality,
            placeholder_detected=is_placeholder,
            business_validity_status=placeholder_reason,
            modifiers=verified_results,
            underwriter_summary=summary,
            generated_at=timestamps["generated_at"],
            generated_at_utc=timestamps["generated_at_utc"],
            generated_at_local=timestamps["generated_at_local"],
            timezone=timestamps["timezone"]
        )

    def _get_demo_report(self, company: CompanyInput) -> CyberRiskReport:
        timestamps = get_generated_timestamps()
        norm_domain = normalize_domain(company.domain)
        
        profiles = {
            "very_favorable": {"score": 1.20, "cat": "Very Favorable"},
            "favorable": {"score": 1.80, "cat": "Favorable"},
            "average": {"score": 2.60, "cat": "Average"},
            "partially_unfavorable": {"score": 3.30, "cat": "Partially Unfavorable"},
            "unfavorable": {"score": 3.80, "cat": "Unfavorable"},
        }
        
        profile = profiles.get(company.demo_profile, profiles["average"])
        score = profile["score"]
        cat = profile["cat"]
        
        demo_mod = ModifierResult(
            modifier_name="Demo Modifier",
            score=score,
            risk_category=cat,
            confidence=0.99,
            findings=["Demo findings generated automatically."],
            evidence=[],
            verification_status="verified",
            recommendation="Review real signals by running a non-demo analysis.",
            reason_for_score="Static demo mode score."
        )
        
        summary = f"Overall Risk Category: {cat}\nKey Favorable Indicators: None (Demo)\nKey Risk Indicators: None (Demo)\nEvidence Quality: High (Demo)\nRecommended Underwriting Review Points: Perform a real analysis."

        return CyberRiskReport(
            company_name=company.company_name + " (DEMO)",
            domain=company.domain,
            normalized_domain=norm_domain,
            country=company.country,
            revenue_band=company.revenue_band,
            industry=company.industry,
            overall_score=score,
            overall_risk_category=cat,
            overall_confidence=0.99,
            category_reason=f"Demo profile {company.demo_profile} requested.",
            top_positive_drivers=[],
            top_negative_drivers=[],
            manual_review_required=False,
            modifiers=[demo_mod],
            underwriter_summary=summary,
            generated_at=timestamps["generated_at"],
            generated_at_utc=timestamps["generated_at_utc"],
            generated_at_local=timestamps["generated_at_local"],
            timezone=timestamps["timezone"]
        )

    def _get_invalid_domain_report(self, company: CompanyInput, validation_error: str) -> CyberRiskReport:
        timestamps = get_generated_timestamps()
        
        raw_data = {
            "input_domain": company.domain,
            "normalized_domain": None,
            "is_valid_domain": False,
            "validation_error": validation_error
        }
        
        modifiers = []
        for name, msg in [
            ("Domain Encryption", "Invalid domain format. HTTPS validation was not performed."),
            ("Privacy Regulation", "Invalid domain format. Privacy validation was not performed."),
            ("E-Commerce Presence", "Invalid domain format."),
            ("Customer Type", "Invalid domain format."),
            ("Geographic Spread", "Invalid domain format.")
        ]:
            modifiers.append(ModifierResult(
                modifier_name=name,
                score=3.0,
                risk_category="Unknown",
                confidence=0.10,
                findings=[msg],
                evidence=[],
                verification_status="not_verified",
                raw_data=raw_data if name == "Domain Encryption" else None
            ))
            
        summary = "The website appears to be an invalid domain. Manual underwriting validation is required."

        return CyberRiskReport(
            company_name=company.company_name,
            domain=company.domain,
            normalized_domain=None,
            country=company.country,
            revenue_band=company.revenue_band,
            industry=company.industry,
            overall_score=3.0,
            overall_risk_category="Manual Review Required",
            overall_confidence=0.10,
            category_reason="Invalid domain format. Automated evidence collection cannot be performed.",
            top_positive_drivers=[],
            top_negative_drivers=[],
            manual_review_required=True,
            evidence_quality="Low",
            is_valid_domain=False,
            validation_error=validation_error,
            modifiers=modifiers,
            underwriter_summary=summary,
            generated_at=timestamps["generated_at"],
            generated_at_utc=timestamps["generated_at_utc"],
            generated_at_local=timestamps["generated_at_local"],
            timezone=timestamps["timezone"]
        )
