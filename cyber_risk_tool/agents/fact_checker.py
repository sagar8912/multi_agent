from typing import List
from schemas.output_models import ModifierResult

class FactCheckerAgent:
    def verify(self, modifiers: List[ModifierResult]) -> List[ModifierResult]:
        for mod in modifiers:
            has_evidence = len(mod.evidence) > 0
            
            if not has_evidence or mod.risk_category == "Unknown":
                mod.verification_status = "not_verified"
                mod.confidence = max(0.1, mod.confidence - 0.2)
            else:
                is_weak = False
                if len(mod.evidence) == 1:
                    url = mod.evidence[0].url
                    # Weak if the evidence URL is just the homepage root
                    if url and url.rstrip('/').count('/') <= 2:
                        # For privacy, the homepage is weak evidence
                        if mod.modifier_name == "Privacy Regulation":
                            is_weak = True
                
                if is_weak:
                    mod.verification_status = "partially_verified"
                else:
                    mod.verification_status = "verified"
                    
        return modifiers
