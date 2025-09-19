"""
申万行业相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional

class SWIndustryBase(BaseModel):
    industry_code: str = Field(..., description="行业代码")
    level1_industry: Optional[str] = None
    level2_industry: Optional[str] = None
    level3_industry: Optional[str] = None

class SWIndustry(SWIndustryBase):
    id: int
    index_code: Optional[str] = None

    class Config:
        from_attributes = True