from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# 獲取當前文件所在目錄
current_dir = os.path.dirname(os.path.abspath(__file__))

# 建立 database 目錄（如果不存在）
db_dir = os.path.join(current_dir, '..', '..', 'database')
os.makedirs(db_dir, exist_ok=True)

# 設定資料庫 URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(db_dir, 'app.db')}"

# 創建基礎模型類
Base = declarative_base()

# 創建資料庫引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 特定設定
)

# 創建會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """獲取資料庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 