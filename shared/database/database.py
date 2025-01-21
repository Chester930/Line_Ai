from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy import text
from .base import Base, engine, SessionLocal, get_db

logger = logging.getLogger(__name__)

def check_database_connection() -> bool:
    """檢查資料庫連接狀態"""
    try:
        # 嘗試建立連接並執行簡單查詢
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error when checking database: {str(e)}")
        return False

def init_db():
    """初始化資料庫"""
    try:
        # 檢查資料庫連接
        if not check_database_connection():
            logger.error("Cannot connect to database")
            return False
            
        # 檢查表格是否已存在
        with engine.connect() as conn:
            tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            existing_tables = [row[0] for row in tables]
            
            required_tables = [
                'knowledge_bases', 'documents', 'document_chunks',
                'cloud_sources', 'knowledge_base_documents'
            ]
            
            # 如果所有必需的表格都存在，直接返回成功
            if all(table in existing_tables for table in required_tables):
                logger.info("All required tables already exist")
                return True
        
        # 導入所有模型
        from .models import (
            User, Role, KnowledgeBase, Document, DocumentChunk,
            CloudSource, Conversation, Message, UserSetting,
            CloudService, CloudDocument, knowledge_base_documents
        )
        
        # 創建缺失的表格
        logger.info("Creating missing database tables...")
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            return False
            
        # 驗證表格是否創建成功
        with engine.connect() as conn:
            tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            existing_tables = [row[0] for row in tables]
            logger.info(f"Existing tables: {existing_tables}")
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                logger.error(f"Missing tables after creation: {missing_tables}")
                return False
                
        return True
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        if "permission" in str(e).lower():
            logger.error("Database permission error. Please check file permissions.")
        elif "locked" in str(e).lower():
            logger.error("Database is locked. Please ensure no other process is using it.")
        return False

def close_db():
    """關閉資料庫連接"""
    engine.dispose()
