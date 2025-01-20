from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
import enum

class PermissionType(enum.Enum):
    """權限類型"""
    READ = "read"  # 只讀
    WRITE = "write"  # 讀寫
    ADMIN = "admin"  # 管理員

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
    knowledge_bases = relationship("KnowledgeBase", back_populates="user")
    kb_permissions = relationship("KnowledgeBasePermission", back_populates="user")
    kb_logs = relationship("KnowledgeBaseLog", back_populates="user")

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

class KnowledgeBase(Base):
    """知識庫表"""
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)  # 是否公開
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    user = relationship("User", back_populates="knowledge_bases")
    folders = relationship("KnowledgeBaseFolder", back_populates="knowledge_base")
    documents = relationship("Document", back_populates="knowledge_base")
    roles = relationship("RoleKnowledgeBase", back_populates="knowledge_base")
    permissions = relationship("KnowledgeBasePermission", back_populates="knowledge_base")
    shares = relationship("KnowledgeBaseShare", back_populates="knowledge_base")
    logs = relationship("KnowledgeBaseLog", back_populates="knowledge_base")

class KnowledgeBaseFolder(Base):
    """知識庫資料夾表"""
    __tablename__ = "knowledge_base_folders"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    parent_id = Column(Integer, ForeignKey("knowledge_base_folders.id"), nullable=True)
    name = Column(String(100), nullable=False)
    path = Column(String(512))  # 完整路徑，用/分隔
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    knowledge_base = relationship("KnowledgeBase", back_populates="folders")
    parent = relationship("KnowledgeBaseFolder", remote_side=[id], backref="subfolders")
    documents = relationship("Document", back_populates="folder")

class RoleKnowledgeBase(Base):
    """角色知識庫關聯表"""
    __tablename__ = "role_knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(String(50))  # 對應到 role_manager 中的角色
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    knowledge_base = relationship("KnowledgeBase", back_populates="roles")

class Document(Base):
    """文件表"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    folder_id = Column(Integer, ForeignKey("knowledge_base_folders.id"), nullable=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    file_path = Column(String(512))
    file_type = Column(String(50))
    embedding_status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    folder = relationship("KnowledgeBaseFolder", back_populates="documents")
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

class CloudService(Base):
    __tablename__ = "cloud_services"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)  # 服務名稱
    service_type = Column(String(20), nullable=False)  # 服務類型 (Google Drive, Dropbox etc.)
    config = Column(JSON)  # 服務配置
    status = Column(String(20))  # 連接狀態
    last_sync = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    documents = relationship("CloudDocument", back_populates="cloud_service")

class CloudDocument(Base):
    __tablename__ = "cloud_documents"
    
    id = Column(Integer, primary_key=True)
    cloud_service_id = Column(Integer, ForeignKey('cloud_services.id'))
    remote_id = Column(String(255))  # 雲端文件ID
    name = Column(String(255))
    path = Column(String(512))
    size = Column(Integer)
    last_modified = Column(DateTime)
    sync_status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    cloud_service = relationship("CloudService", back_populates="documents")

class KnowledgeBasePermission(Base):
    """知識庫權限表"""
    __tablename__ = "knowledge_base_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    permission_type = Column(Enum(PermissionType))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    knowledge_base = relationship("KnowledgeBase", back_populates="permissions")
    user = relationship("User", back_populates="kb_permissions")

class KnowledgeBaseShare(Base):
    """知識庫分享表"""
    __tablename__ = "knowledge_base_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    share_code = Column(String(50), unique=True, index=True)  # 分享碼
    permission_type = Column(Enum(PermissionType))
    expires_at = Column(DateTime, nullable=True)  # 過期時間，null表示永不過期
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    knowledge_base = relationship("KnowledgeBase", back_populates="shares")

class KnowledgeBaseLog(Base):
    """知識庫操作日誌表"""
    __tablename__ = "knowledge_base_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50))  # 操作類型
    details = Column(JSON)  # 操作詳情
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    knowledge_base = relationship("KnowledgeBase", back_populates="logs")
    user = relationship("User", back_populates="kb_logs")
