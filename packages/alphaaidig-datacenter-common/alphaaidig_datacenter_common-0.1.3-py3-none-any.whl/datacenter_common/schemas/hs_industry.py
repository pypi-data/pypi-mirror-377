"""
沪深行业相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class HSIndustryBase(BaseModel):
    industry_code: str = Field(..., description="行业代码")
    industry_name: str = Field(..., description="行业名称")
    business_category_code: Optional[str] = None
    business_category_name: Optional[str] = None
    business_subcategory_code: Optional[str] = None
    business_subcategory_name: Optional[str] = None
    description: Optional[str] = None

class HSIndustry(HSIndustryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 为了兼容性，添加别名
HSIndustryCategory = HSIndustry