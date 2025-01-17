import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, Bot, Document, ChatLog
import logging
from shared.config.config import Config
from datetime import datetime
import mimetypes

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._init_db()
    
    def _init_db(self):
        """初始化資料庫連接"""
        try:
            database_url = Config.DATABASE_URL
            self.engine = create_engine(database_url)
            Base.metadata.create_all(bind=self.engine)
            self.SessionLocal = sessionmaker(bind=self.engine)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise

    def get_session(self):
        """獲取資料庫會話"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def create_bot(self, name, channel_id, channel_secret, channel_access_token):
        """創建新的 Bot"""
        session = self.SessionLocal()
        try:
            bot = Bot(
                name=name,
                channel_id=channel_id,
                channel_secret=channel_secret,
                channel_access_token=channel_access_token
            )
            session.add(bot)
            session.commit()
            return bot
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating bot: {str(e)}")
            raise
        finally:
            session.close()

    def save_document(self, bot_id, file, save_path):
        """保存上傳的文件"""
        session = self.SessionLocal()
        try:
            # 確保存儲目錄存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # 保存文件到磁盤
            with open(save_path, 'wb') as f:
                f.write(file.file.read())
            
            # 獲取文件資訊
            file_size = os.path.getsize(save_path)
            file_type = os.path.splitext(file.filename)[1][1:]  # 去掉點號
            content_type = mimetypes.guess_type(file.filename)[0]
            
            # 創建文件記錄
            doc = Document(
                bot_id=bot_id,
                filename=file.filename,
                file_type=file_type,
                file_size=file_size,
                content_type=content_type,
                file_path=save_path
            )
            
            session.add(doc)
            session.commit()
            return doc
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving document: {str(e)}")
            if os.path.exists(save_path):
                os.remove(save_path)  # 清理失敗的文件
            raise
        finally:
            session.close()

    def get_bot_documents(self, bot_id):
        """獲取 Bot 的所有文件"""
        session = self.SessionLocal()
        try:
            return session.query(Document).filter(Document.bot_id == bot_id).all()
        finally:
            session.close()

# 創建全局資料庫實例
db = Database()
