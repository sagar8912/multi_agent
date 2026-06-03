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
        
        active_modifiers = [m for m in modifiers if m.status != "not_implemented_phase_2"]
        
        for mod in active_modifiers:
            key = mod.modifier_name.lower().replace(" ", "_").replace("/", "").replace("__", "_")
            if key == "amount_of_sensitive_information": key = "amount_of_sensitive_information"
            
            weight = 1.0
            if key in self.rules and "weight" in self.rules[key]:
                weight = float(self.rules[key]["weight"])
                
            weighted_score += mod.score * weight
            total_weight += weight
            total_confidence += mod.confidence
            
            # Penalize overall confidence if partial MVP has low confidence
            if mod.status == "partial_mvp" and mod.confidence < 0.6:
                total_confidence -= 0.1
            
        overall_score = weighted_score / total_weight if total_weight > 0 else 0
        overall_confidence = max(0, total_confidence / len(active_modifiers) if active_modifiers else 0)
        
        overall_risk_category = self._get_risk_category(overall_score)
        
        return overall_score, overall_risk_category, overall_confidence
        
    def _get_risk_category(self, score: float) -> str:
        if 1.0 <= score < 1.50: return "Very Favorable"
        if 1.50 <= score < 2.25: return "Favorable"
        if 2.25 <= score <= 3.00: return "Average"
        if 3.00 < score <= 3.60: return "Partially Unfavorable"
        if 3.60 < score <= 4.00: return "Unfavorable"
        return "Unknown"

    def apply_overrides(self, risk_category: str, manual_review_required: bool, evidence_quality: str, modifiers: List[ModifierResult], overall_confidence: float) -> str:
        if manual_review_required:
            return "Manual Review Required"
            
        domain_unreachable = any(m.modifier_name == "Domain Encryption" and m.risk_category == "Unknown" for m in modifiers)
        if domain_unreachable:
            return "Manual Review Required"
            
        if overall_confidence < 0.40:
            if risk_category in ["Very Favorable", "Favorable"]:
                return "Average"

        if evidence_quality == "Low":
            if risk_category in ["Very Favorable", "Favorable"]:
                return "Average"

        privacy_score = next((m.score for m in modifiers if m.modifier_name == "Privacy Regulation"), 0)
        sensitive_cat = next((m.risk_category for m in modifiers if m.modifier_name == "Amount of Sensitive Information"), "Unknown")
        
        if privacy_score >= 4.0 and sensitive_cat == "Unknown":
            if risk_category in ["Very Favorable", "Favorable"]:
                return "Average"
                
        return risk_category
