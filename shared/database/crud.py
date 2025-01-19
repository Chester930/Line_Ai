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
        user_id: int,
        title: str,
        content: str,
        file_path: str,
        file_type: str
    ) -> models.Document:
        """創建新文件記錄"""
        document = models.Document(
            user_id=user_id,
            title=title,
            content=content,
            file_path=file_path,
            file_type=file_type,
            created_at=datetime.utcnow()
        )
        self.db.add(document)
        self.db.commit()
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