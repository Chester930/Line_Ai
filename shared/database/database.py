from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy import text
from .base import Base, engine, SessionLocal, get_db
import os

logger = logging.getLogger(__name__)

# 添加資料庫初始化標記
_DB_INITIALIZED = False

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
    global _DB_INITIALIZED
    
    # 如果已經初始化過，直接返回
    if _DB_INITIALIZED:
        return True
        
    try:
        # 檢查資料庫文件是否存在
        db_path = "database/app.db"
        if not os.path.exists(db_path):
            # 確保目錄存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # 創建資料庫表
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("Tables created successfully")
        
        _DB_INITIALIZED = True
        return True
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def close_db():
    """關閉資料庫連接"""
    engine.dispose()
