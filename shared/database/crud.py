from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from . import models
from .base import SessionLocal

class BaseCRUD:
    """基礎 CRUD 操作類"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def close(self):
        """關閉會話"""
        if self.db:
            self.db.close()

class UserCRUD(BaseCRUD):
    """使用者 CRUD 操作"""
    
    def get_by_line_id(self, line_user_id: str) -> Optional[models.User]:
        """根據 LINE 用戶 ID 獲取用戶"""
        return self.db.query(models.User).filter_by(line_user_id=line_user_id).first()
    
    def create_user(self, line_user_id: str, nickname: Optional[str] = None) -> models.User:
        """創建新用戶"""
        user = models.User(
            line_user_id=line_user_id,
            nickname=nickname,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        self.db.add(user)
        self.db.commit()
        return user
    
    def update_last_active(self, user_id: int) -> None:
        """更新用戶最後活動時間"""
        user = self.db.query(models.User).get(user_id)
        if user:
            user.last_active = datetime.utcnow()
            self.db.commit()

class ConversationCRUD(BaseCRUD):
    """對話 CRUD 操作"""
    
    def create_conversation(self, user_id: int, model: str) -> models.Conversation:
        """創建新對話"""
        conversation = models.Conversation(
            user_id=user_id,
            model=model,
            created_at=datetime.utcnow()
        )
        self.db.add(conversation)
        self.db.commit()
        return conversation
    
    def get_user_conversations(self, user_id: int) -> List[models.Conversation]:
        """獲取用戶的所有對話"""
        return self.db.query(models.Conversation)\
            .filter_by(user_id=user_id)\
            .order_by(models.Conversation.created_at.desc())\
            .all()
    
    def get_conversation(self, conversation_id: int) -> Optional[models.Conversation]:
        """獲取特定對話"""
        return self.db.query(models.Conversation).get(conversation_id)

class MessageCRUD(BaseCRUD):
    """訊息 CRUD 操作"""
    
    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str
    ) -> models.Message:
        """添加新訊息"""
        message = models.Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )
        self.db.add(message)
        self.db.commit()
        return message
    
    def get_conversation_messages(
        self,
        conversation_id: int,
        limit: int = 50
    ) -> List[models.Message]:
        """獲取對話的訊息歷史"""
        return self.db.query(models.Message)\
            .filter_by(conversation_id=conversation_id)\
            .order_by(models.Message.created_at.desc())\
            .limit(limit)\
            .all()

class DocumentCRUD(BaseCRUD):
    """文件 CRUD 操作"""
    
    def create_document(
        self,
        db: Session,
        title: str,
        content: str,
        doc_metadata: dict = None,
        file_type: str = None,
        file_path: str = None,
        knowledge_base_id: int = None
    ) -> models.Document:
        """創建新文件記錄"""
        document = models.Document(
            title=title,
            content=content,
            doc_metadata=doc_metadata,
            file_type=file_type,
            file_path=file_path,
            knowledge_base_id=knowledge_base_id,
            created_at=datetime.utcnow()
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
    
    def get_user_documents(self, user_id: int) -> List[models.Document]:
        """獲取用戶的所有文件"""
        return self.db.query(models.Document)\
            .filter_by(user_id=user_id)\
            .order_by(models.Document.created_at.desc())\
            .all()
    
    def get_document(self, document_id: int) -> Optional[models.Document]:
        """獲取特定文件"""
        return self.db.query(models.Document).get(document_id)
    
    def delete_document(self, document_id: int) -> bool:
        """刪除文件"""
        document = self.get_document(document_id)
        if document:
            self.db.delete(document)
            self.db.commit()
            return True
        return False

def create_knowledge_base(db: Session, name: str, description: str = None):
    """創建新的知識庫"""
    kb = models.KnowledgeBase(
        name=name,
        description=description,
        enabled=True,
        created_at=datetime.now()
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb

def get_knowledge_base(db: Session, kb_id: int):
    """獲取指定ID的知識庫"""
    return db.query(models.KnowledgeBase).filter(models.KnowledgeBase.id == kb_id).first()

def get_knowledge_bases(db: Session, skip: int = 0, limit: int = 100):
    """獲取所有知識庫列表"""
    return db.query(models.KnowledgeBase).offset(skip).limit(limit).all()

def update_knowledge_base(db: Session, kb_id: int, name: str = None, description: str = None, enabled: bool = None):
    """更新知識庫信息"""
    kb = get_knowledge_base(db, kb_id)
    if not kb:
        return None
        
    if name is not None:
        kb.name = name
    if description is not None:
        kb.description = description
    if enabled is not None:
        kb.enabled = enabled
        
    kb.updated_at = datetime.now()
    db.commit()
    db.refresh(kb)
    return kb

def delete_knowledge_base(db: Session, kb_id: int):
    """刪除知識庫"""
    kb = get_knowledge_base(db, kb_id)
    if not kb:
        return False
    db.delete(kb)
    db.commit()
    return True

# Document CRUD operations
def create_document(db: Session, title: str, content: str, knowledge_base_id: int, 
                   file_type: str = None, file_path: str = None, doc_metadata: dict = None):
    """創建新文檔"""
    doc = models.Document(
        title=title,
        content=content,
        knowledge_base_id=knowledge_base_id,
        file_type=file_type,
        file_path=file_path,
        doc_metadata=doc_metadata,
        created_at=datetime.now()
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_document(db: Session, doc_id: int):
    """獲取指定ID的文檔"""
    return db.query(models.Document).filter(models.Document.id == doc_id).first()

def get_documents_by_knowledge_base(db: Session, kb_id: int, skip: int = 0, limit: int = 100):
    """獲取指定知識庫下的所有文檔"""
    return db.query(models.Document).filter(
        models.Document.knowledge_base_id == kb_id
    ).offset(skip).limit(limit).all()

def update_document(db: Session, doc_id: int, **kwargs):
    """更新文檔信息"""
    doc = get_document(db, doc_id)
    if not doc:
        return None
        
    for key, value in kwargs.items():
        if hasattr(doc, key):
            setattr(doc, key, value)
    
    doc.updated_at = datetime.now()
    db.commit()
    db.refresh(doc)
    return doc

def delete_document(db: Session, doc_id: int):
    """刪除文檔"""
    doc = get_document(db, doc_id)
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True