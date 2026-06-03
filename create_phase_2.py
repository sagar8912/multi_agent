import os

agents = {
    'mergers_acquisitions_agent': {
        'name': 'Mergers and Acquisitions',
        'findings': 'Requires subsidiary/legal entity data from annual reports, SEC Exhibit 21, corporate registries or D&B.'
    },
    'organizational_complexity_agent': {
        'name': 'Organizational Complexity',
        'findings': 'Requires subsidiary/legal entity data from annual reports, SEC Exhibit 21, corporate registries or D&B.'
    },
    'seasonality_sales_agent': {
        'name': 'Seasonality of Sales',
        'findings': 'Requires quarterly revenue data from SEC filings, annual reports, or investor relations.'
    },
    'volatility_recovery_sales_agent': {
        'name': 'Volatility / Recovery in Sales',
        'findings': 'Requires detailed footprint and digital channel sales volume analysis.'
    }
}

template = '''from schemas.input_models import CompanyInput
from schemas.output_models import ModifierResult

class {class_name}:
    async def run(self, company: CompanyInput) -> ModifierResult:
        return ModifierResult(
            modifier_name="{mod_name}",
            score=3.0,
            risk_category="Manual Review Required",
            confidence=0.1,
            findings=["{findings}"],
            evidence=[],
            status="not_implemented_phase_2",
            reason_for_score="Phase 2 modifier not currently calculated.",
            recommendation="Use external data sources to validate."
        )
'''

for file_name, data in agents.items():
    class_name = ''.join(word.capitalize() for word in file_name.split('_')[:-1]) + 'Agent'
    content = template.format(class_name=class_name, mod_name=data['name'], findings=data['findings'])
    with open(f'cyber_risk_tool/agents/research/{file_name}.py', 'w') as f:
        f.write(content)
