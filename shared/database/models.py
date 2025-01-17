from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Bot(Base):
    """Line Bot 設定"""
    __tablename__ = 'bots'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    channel_id = Column(String(50), unique=True, nullable=False)
    channel_secret = Column(String(100), nullable=False)
    channel_access_token = Column(String(200), nullable=False)
    webhook_url = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 關聯
    documents = relationship("Document", back_populates="bot")
    chat_logs = relationship("ChatLog", back_populates="bot")

class Document(Base):
    """文件存儲"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey('bots.id'))
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # 例如: pdf, docx, xlsx
    file_size = Column(Integer, nullable=False)  # 以字節為單位
    content_type = Column(String(100))  # MIME 類型
    file_path = Column(String(500))  # 文件在磁盤上的存儲路徑
    processed = Column(Boolean, default=False)  # 是否已處理為知識庫
    processed_content = Column(JSON)  # 處理後的內容（如果需要）
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 關聯
    bot = relationship("Bot", back_populates="documents")

class ChatLog(Base):
    """對話記錄"""
    __tablename__ = 'chat_logs'
    
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey('bots.id'))
    user_id = Column(String(50), nullable=False)
    message = Column(String(2000), nullable=False)
    response = Column(String(2000))
    reference_doc_ids = Column(JSON)  # 引用的文件 ID 列表
    created_at = Column(DateTime, default=datetime.now)
    
    # 關聯
    bot = relationship("Bot", back_populates="chat_logs")
