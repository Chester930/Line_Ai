from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from shared.config.config import Config
from .models import Base

class Database:
    """資料庫管理類"""
    
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
    
    def init_db(self):
        """初始化資料庫"""
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """獲取資料庫會話"""
        return self.Session()
    
    def close_session(self):
        """關閉資料庫會話"""
        self.Session.remove()

# 創建全局資料庫實例
db = Database()
