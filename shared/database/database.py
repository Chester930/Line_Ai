from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
from pathlib import Path
from sqlalchemy import text

logger = logging.getLogger(__name__)

# 資料庫 URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{Path(__file__).parent.parent.parent}/data/app.db"

# 創建資料庫引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 特定設定
)

# 創建 SessionLocal 類別
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """獲取資料庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    from .models import Base  # 避免循環導入
    try:
        # 創建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        return False

def close_db():
    """關閉資料庫連接"""
    engine.dispose()
