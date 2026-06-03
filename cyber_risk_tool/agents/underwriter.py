from typing import List
from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult

class UnderwriterAgent:
    def generate_summary(self, company: CompanyInput, modifiers: List[ModifierResult], score: float, risk_category: str) -> str:
        if risk_category == "Manual Review Required":
            return (
                "Overall Risk Category: Manual Review Required\n"
                "Key Favorable Indicators: None verified\n"
                "Key Risk Indicators: Insufficient evidence\n"
                "Evidence Quality: Low/Unreachable\n"
                "Recommended Underwriting Review Points: Mention insufficient evidence and manual validation needed. Validate the company domain manually."
            )
            
        fav = [m.modifier_name for m in modifiers if m.score <= 2.0 and m.risk_category != "Unknown"]
        unfav = [m.modifier_name for m in modifiers if m.score >= 3.0 and m.risk_category != "Unknown"]
        
        confidence = sum(m.confidence for m in modifiers) / len(modifiers) if modifiers else 0
        quality = "High" if confidence >= 0.8 else "Medium" if confidence >= 0.5 else "Low"
        
        review_text = ""
        if risk_category == "Very Favorable":
            review_text = "Mention strong controls and low cyber exposure. Proceed with standard favorable terms."
        elif risk_category == "Favorable":
            review_text = "Mention mostly positive posture but some review points. Focus on validating " + (', '.join(unfav) if unfav else "any remaining unknowns") + "."
        elif risk_category == "Average":
            review_text = "Mention mixed risk signals. Validate " + (', '.join(unfav) if unfav else "moderate risk factors") + "."
        elif risk_category == "Partially Unfavorable":
            review_text = "Mention material concerns requiring underwriter validation. Carefully review " + (', '.join(unfav) if unfav else "all signals") + "."
        elif risk_category == "Unfavorable":
            review_text = "Mention confirmed high-risk indicators. Deep review required for " + (', '.join(unfav) if unfav else "all cyber controls") + "."
        
        summary = (
            f"Overall Risk Category: {risk_category}\n"
            f"Key Favorable Indicators: {', '.join(fav) if fav else 'None'}\n"
            f"Key Risk Indicators: {', '.join(unfav) if unfav else 'None'}\n"
            f"Evidence Quality: {quality}\n"
            f"Recommended Underwriting Review Points: {review_text}"
        )
        return summary
