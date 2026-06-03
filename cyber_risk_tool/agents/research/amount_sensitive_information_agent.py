from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult
from agents.research.customer_type_agent import CustomerTypeAgent
from agents.research.ecommerce_agent import EcommerceAgent

class AmountSensitiveInformationAgent:
    def __init__(self):
        self.customer_agent = CustomerTypeAgent()
        self.ecommerce_agent = EcommerceAgent()

    async def run(self, company: CompanyInput) -> ModifierResult:
        customer_result = await self.customer_agent.run(company)
        ecommerce_result = await self.ecommerce_agent.run(company)

        # Merge findings and evidence
        findings = customer_result.findings + ecommerce_result.findings
        evidence = customer_result.evidence + ecommerce_result.evidence

        customer_type_score = customer_result.score
        ecommerce_score = ecommerce_result.score

        customer_cat = customer_result.risk_category
        ecommerce_cat = ecommerce_result.risk_category

        score = 3.0
        risk_category = "Unknown"
        confidence = (customer_result.confidence + ecommerce_result.confidence) / 2.0
        reason_for_score = ""

        # Logic:
        # - B2B + no e-commerce = Favorable (1.0 - 1.5)
        # - B2B + e-commerce = Partially Favorable / Average (2.0 - 2.5)
        # - B2C/B2B + no e-commerce = Average (2.0 - 2.5)
        # - B2C/B2B + e-commerce = Partially Unfavorable (3.0 - 3.5)

        is_b2b_only = customer_cat in ["Favorable", "Very Favorable"]
        is_ecommerce = ecommerce_cat in ["Partially Unfavorable", "Unfavorable"]

        if is_b2b_only and not is_ecommerce:
            score = 1.0
            risk_category = "Favorable"
            reason_for_score = "B2B profile with no detected e-commerce presence."
        elif is_b2b_only and is_ecommerce:
            score = 2.0
            risk_category = "Average"
            reason_for_score = "B2B profile with detected e-commerce presence."
        elif not is_b2b_only and not is_ecommerce:
            score = 2.5
            risk_category = "Average"
            reason_for_score = "B2C/Mixed profile with no detected e-commerce presence."
        elif not is_b2b_only and is_ecommerce:
            score = 3.0
            risk_category = "Partially Unfavorable"
            reason_for_score = "B2C/Mixed profile with detected e-commerce presence."
        else:
            score = 3.0
            risk_category = "Unknown"
            reason_for_score = "Insufficient data to determine sensitive information exposure."

        raw_data = {
            "customer_type_result": customer_result.model_dump(exclude={"evidence"}),
            "ecommerce_result": ecommerce_result.model_dump(exclude={"evidence"})
        }

        return ModifierResult(
            modifier_name="Amount of Sensitive Information",
            score=score,
            risk_category=risk_category,
            confidence=confidence,
            findings=findings,
            evidence=evidence,
            raw_data=raw_data,
            recommendation="Ensure robust data protection controls for customer portals and e-commerce platforms.",
            reason_for_score=reason_for_score
        )
