from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class User(Base):
    """用戶表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    line_user_id = Column(String(50), unique=True, index=True)
    display_name = Column(String(100))
    picture_url = Column(String(200))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    conversations = relationship("Conversation", back_populates="user")
    settings = relationship("UserSetting", back_populates="user", uselist=False)

class Conversation(Base):
    """對話表"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(String(50))  # 對應到 role_manager 中的角色
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    """消息表"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(20))  # user 或 assistant
    content = Column(Text)
    tokens = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    conversation = relationship("Conversation", back_populates="messages")

class UserSetting(Base):
    """用戶設定表"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    default_role_id = Column(String(50))
    notification_enabled = Column(Boolean, default=True)
    web_search_enabled = Column(Boolean, default=True)
    settings = Column(JSON)  # 其他自定義設定
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    user = relationship("User", back_populates="settings")

class Document(Base):
    """文件表"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text)
    file_path = Column(String(500))
    file_type = Column(String(50))
    embedding_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    """文件片段表 (用於向量搜索)"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    content = Column(Text)
    embedding = Column(JSON)  # 存儲向量嵌入
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    document = relationship("Document", back_populates="chunks")
