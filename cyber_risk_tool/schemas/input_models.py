from pydantic import BaseModel
from typing import Optional

class CompanyInput(BaseModel):
    company_name: str
    domain: str
    country: str
    revenue_band: str
    industry: Optional[str] = None
    demo_mode: bool = False
    demo_profile: Optional[str] = None
