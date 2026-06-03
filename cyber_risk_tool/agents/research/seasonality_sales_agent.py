from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult

class SeasonalitySalesAgent:
    async def run(self, company: CompanyInput) -> ModifierResult:
        return ModifierResult(
            modifier_name="Seasonality of Sales",
            score=3.0,
            risk_category="Manual Review Required",
            confidence=0.1,
            findings=["Requires quarterly revenue data from SEC filings, annual reports, or investor relations."],
            evidence=[],
            status="not_implemented_phase_2",
            reason_for_score="Phase 2 modifier not currently calculated.",
            recommendation="Use external data sources to validate."
        )
