from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from . import models
from .base import SessionLocal
from .database import engine, Base
from .models import Document, DocumentChunk, KnowledgeBase
import logging
from sqlalchemy import text

class DocumentCRUD:
    """文件 CRUD 操作"""
    
    def __init__(self):
        try:
            self.db = SessionLocal()
        except Exception as e:
            logger.error(f"Failed to create database session: {str(e)}")
            raise
    
    def _ensure_tables(self):
        """確保所需的表格存在"""
        try:
            # 檢查表是否存在
            with engine.connect() as conn:
                # 檢查 knowledge_bases 表
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_bases'"))
                if not result.scalar():
                    Base.metadata.create_all(bind=engine)
                    logging.info("Created database tables")
        except Exception as e:
            logging.error(f"Error ensuring tables: {str(e)}")
            raise
    
    def create_document(
        self,
        title: str,
        content: str,
        file_type: str,
        file_size: float
    ) -> Document:
        """創建新文件"""
        try:
            document = Document(
                title=title,
                content=content,
                file_type=file_type,
                file_size=file_size,
                created_at=datetime.utcnow()
            )
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            return document
        except Exception as e:
            self.db.rollback()
            logger.error(f"創建文件失敗: {str(e)}")
            raise
    
    def create_document_chunk(
        self,
        document_id: int,
        content: str,
        embedding: List[float]
    ) -> DocumentChunk:
        """創建文件分塊"""
        chunk = DocumentChunk(
            document_id=document_id,
            content=content,
            embedding=embedding,
            created_at=datetime.utcnow()
        )
        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)
        return chunk
    
    def get_all_documents(self) -> List[Document]:
        """獲取所有文件"""
        try:
            return self.db.query(Document).order_by(Document.created_at.desc()).all()
        except Exception as e:
            logger.error(f"獲取文件列表失敗: {str(e)}")
            raise
    
    def get_document(self, document_id: int) -> Optional[Document]:
        """獲取指定文件"""
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def delete_document(self, document_id: int) -> bool:
        """刪除文件"""
        try:
            document = self.get_document(document_id)
            if document:
                self.db.delete(document)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"刪除文件失敗: {str(e)}")
            return False
    
    def get_document_chunks(
        self,
        document_id: int
    ) -> List[DocumentChunk]:
        """獲取文件的所有分段"""
        return self.db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index).all()
    
    def __del__(self):
        """關閉資料庫連接"""
        try:
            self.db.close()
        except Exception as e:
            logger.error(f"關閉資料庫連接失敗: {str(e)}") 