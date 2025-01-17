from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.config.config import Config

# 創建基礎模型類
Base = declarative_base()

# 創建資料庫引擎
engine = create_engine(Config.DATABASE_URL)

# 創建會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """獲取資料庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 