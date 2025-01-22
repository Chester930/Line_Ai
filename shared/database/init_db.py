from .base import Base, engine

def init_database():
    """初始化資料庫"""
    # 創建所有定義的表
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_database() 