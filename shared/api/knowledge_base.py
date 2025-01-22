from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from ..database import crud, get_db
from ..utils.file_processor import FileProcessor
from pydantic import BaseModel
import os

router = APIRouter()
file_processor = FileProcessor(upload_dir='data/uploads')

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str = None

class KnowledgeBaseUpdate(BaseModel):
    name: str = None
    description: str = None
    enabled: bool = None

@router.post("/knowledge-bases/")
def create_knowledge_base(kb: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    """創建新的知識庫"""
    return crud.create_knowledge_base(db=db, name=kb.name, description=kb.description)

@router.get("/knowledge-bases/")
def get_knowledge_bases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """獲取所有知識庫列表"""
    return crud.get_knowledge_bases(db=db, skip=skip, limit=limit)

@router.get("/knowledge-bases/{kb_id}")
def get_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    """獲取指定知識庫"""
    kb = crud.get_knowledge_base(db=db, kb_id=kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return kb

@router.put("/knowledge-bases/{kb_id}")
def update_knowledge_base(kb_id: int, kb_update: KnowledgeBaseUpdate, db: Session = Depends(get_db)):
    """更新知識庫"""
    kb = crud.update_knowledge_base(
        db=db,
        kb_id=kb_id,
        name=kb_update.name,
        description=kb_update.description,
        enabled=kb_update.enabled
    )
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return kb

@router.delete("/knowledge-bases/{kb_id}")
def delete_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    """刪除知識庫"""
    success = crud.delete_knowledge_base(db=db, kb_id=kb_id)
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {"status": "success"}

@router.post("/knowledge-bases/{kb_id}/documents/")
async def upload_document(kb_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上傳文檔到知識庫"""
    try:
        # 檢查知識庫是否存在
        kb = crud.get_knowledge_base(db=db, kb_id=kb_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        # 處理文件
        result = file_processor.process_file(file.file, file.filename)
        
        # 創建文檔記錄
        doc = crud.create_document(
            db=db,
            title=file.filename,
            content=result['content'],
            knowledge_base_id=kb_id,
            file_type=result['mime_type'],
            file_path=result['file_path'],
            doc_metadata={'processed_info': result}
        )
        
        return doc
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/knowledge-bases/{kb_id}/documents/")
def get_documents(kb_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """獲取知識庫中的所有文檔"""
    return crud.get_documents_by_knowledge_base(db=db, kb_id=kb_id, skip=skip, limit=limit) 