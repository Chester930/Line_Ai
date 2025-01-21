from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from . import models
from .base import SessionLocal

class DocumentCRUD:
    """文件 CRUD 操作"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def create_document(
        self,
        title: str,
        content: str,
        file_type: str,
        file_size: int
    ) -> models.Document:
        """創建新文件"""
        document = models.Document(
            title=title,
            content=content,
            file_type=file_type,
            file_size=file_size,
            embedding_status="pending",
            created_at=datetime.utcnow()
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def create_document_chunk(
        self,
        document_id: int,
        content: str,
        embedding: List[float]
    ) -> models.DocumentChunk:
        """創建文件分塊"""
        chunk = models.DocumentChunk(
            document_id=document_id,
            content=content,
            embedding=embedding,
            created_at=datetime.utcnow()
        )
        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)
        return chunk
    
    def get_all_documents(self) -> List[models.Document]:
        """獲取所有文件"""
        return self.db.query(models.Document)\
            .order_by(models.Document.created_at.desc())\
            .all()
    
    def get_document(self, document_id: int) -> Optional[models.Document]:
        """獲取特定文件"""
        return self.db.query(models.Document).get(document_id)
    
    def delete_document(self, document_id: int) -> bool:
        """刪除文件及其分塊"""
        document = self.get_document(document_id)
        if document:
            self.db.delete(document)
            self.db.commit()
            return True
        return False
    
    def get_document_chunks(
        self,
        document_id: int
    ) -> List[models.DocumentChunk]:
        """獲取文件的所有分塊"""
        return self.db.query(models.DocumentChunk)\
            .filter_by(document_id=document_id)\
            .all() 