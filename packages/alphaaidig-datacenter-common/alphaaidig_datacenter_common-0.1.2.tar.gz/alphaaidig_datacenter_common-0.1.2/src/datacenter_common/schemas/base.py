"""
基础Pydantic模型
"""
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    total: int
    page: int
    size: int
    items: List[T]

class BaseResponse(BaseModel):
    """基础响应模型"""
    status: str = "success"
    message: Optional[str] = None
    data: Optional[dict] = None