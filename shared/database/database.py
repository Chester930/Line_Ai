from .base import Base, engine, SessionLocal

def get_db():
    """獲取資料庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化資料庫"""
    Base.metadata.create_all(bind=engine)

def close_db():
    """關閉資料庫連接"""
    engine.dispose()
