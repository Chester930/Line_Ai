from sqlalchemy.orm import Session
from . import models
from datetime import datetime
from typing import Optional, List, Dict

class UserCRUD:
    @staticmethod
    def create_user(db: Session, line_user_id: str, display_name: str, picture_url: str = None):
        db_user = models.User(
            line_user_id=line_user_id,
            display_name=display_name,
            picture_url=picture_url
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_line_id(db: Session, line_user_id: str):
        return db.query(models.User).filter(models.User.line_user_id == line_user_id).first()

class ConversationCRUD:
    @staticmethod
    def create_conversation(db: Session, user_id: int, role_id: str, title: str = None):
        db_conv = models.Conversation(
            user_id=user_id,
            role_id=role_id,
            title=title or f"對話 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        db.add(db_conv)
        db.commit()
        db.refresh(db_conv)
        return db_conv
    
    @staticmethod
    def add_message(db: Session, conversation_id: int, role: str, content: str, tokens: int):
        db_msg = models.Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens=tokens
        )
        db.add(db_msg)
        db.commit()
        db.refresh(db_msg)
        return db_msg

class DocumentCRUD:
    @staticmethod
    def create_document(db: Session, title: str, content: str, file_path: str, file_type: str):
        db_doc = models.Document(
            title=title,
            content=content,
            file_path=file_path,
            file_type=file_type
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        return db_doc