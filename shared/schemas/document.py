from pydantic import BaseModel, field_validator
from typing import Optional, Dict
from datetime import datetime

class DocumentCreate(BaseModel):
    title: str
    content: str
    doc_metadata: Optional[Dict] = None
    file_type: Optional[str] = None
    file_path: Optional[str] = None
    knowledge_base_id: Optional[int] = None

    @field_validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('標題不能為空')
        return v.strip()

class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    doc_metadata: Optional[Dict] = None
    file_type: Optional[str] = None
    file_path: Optional[str] = None
    knowledge_base_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # 新版本中使用 from_attributes 替代 orm_mode 