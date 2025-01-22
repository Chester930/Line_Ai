from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Table
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from .base import Base

class User(Base):
    """用戶表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    line_user_id = Column(String(50), unique=True)
    display_name = Column(String(100))
    picture_url = Column(String(200))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 關聯到對話
    conversations = relationship("Conversation", back_populates="user")
    setting = relationship("UserSetting", back_populates="user", uselist=False)

class Role(Base):
    """角色表"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    role_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_enabled = Column(Boolean, default=True)
    knowledge_base_id = Column(Integer, ForeignKey('knowledge_bases.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    knowledge_base = relationship("KnowledgeBase", back_populates="roles")

class KnowledgeBase(Base):
    """知識庫表"""
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    documents = relationship("Document", back_populates="knowledge_base")
    roles = relationship("Role", back_populates="knowledge_base")
    cloud_sources = relationship("CloudSource", back_populates="knowledge_base")

class Document(Base):
    """文件表"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    processed_content = Column(Text)
    content_hash = Column(String(64))
    doc_metadata = Column(JSON)
    file_type = Column(String(50))
    file_path = Column(String(500))
    file_size = Column(Integer)
    knowledge_base_id = Column(Integer, ForeignKey('knowledge_bases.id'))
    parent_id = Column(Integer, ForeignKey('documents.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 關係定義
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    document_chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    parent = relationship(
        "Document",
        remote_side=[id],
        backref=backref("children", cascade="all, delete-orphan")
    )

# 知識庫與文件的多對多關聯表
knowledge_base_documents = Table(
    'knowledge_base_documents',
    Base.metadata,
    Column('knowledge_base_id', Integer, ForeignKey('knowledge_bases.id')),
    Column('document_id', Integer, ForeignKey('documents.id'))
)

class DocumentChunk(Base):
    """文件分段表"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    content = Column(Text)
    embedding = Column(Text)
    chunk_index = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    
    document = relationship("Document", back_populates="document_chunks")

class CloudSource(Base):
    """雲端知識來源表"""
    __tablename__ = "cloud_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    name = Column(String(100))
    url = Column(String(500))
    type = Column(String(50))  # webpage, api, rss 等
    auth_config = Column(JSON)  # 存儲認證資訊
    sync_frequency = Column(String(20))  # hourly, daily, weekly
    last_sync = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    knowledge_base = relationship("KnowledgeBase", back_populates="cloud_sources")

class Conversation(Base):
    """對話表"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(200))
    model = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    """消息表"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    role = Column(String(50))  # 'user' or 'assistant'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
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
    user = relationship("User", back_populates="setting")

class CloudService(Base):
    """雲端服務設定表"""
    __tablename__ = "cloud_services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    service_type = Column(String(50))  # google_drive, dropbox, onedrive 等
    auth_config = Column(JSON)  # 存儲認證資訊
    status = Column(String(20), default="inactive")  # active, inactive
    last_sync = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    documents = relationship("CloudDocument", back_populates="cloud_service")

class CloudDocument(Base):
    """雲端文件表"""
    __tablename__ = "cloud_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    cloud_service_id = Column(Integer, ForeignKey("cloud_services.id"))
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    remote_id = Column(String(200))  # 雲端服務中的文件 ID
    name = Column(String(200))
    file_type = Column(String(50))
    file_size = Column(Integer)
    last_modified = Column(DateTime)
    sync_status = Column(String(20), default="pending")  # pending, synced, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    cloud_service = relationship("CloudService", back_populates="documents")
    knowledge_base = relationship("KnowledgeBase")
