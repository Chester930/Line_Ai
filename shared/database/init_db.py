from .base import Base
from .database import engine

def init_database():
    """初始化資料庫"""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_database() 