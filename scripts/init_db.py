import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config.config import Config
from shared.database.database import db
import logging

logger = logging.getLogger(__name__)

def init_database():
    """初始化資料庫"""
    try:
        # 設置日誌
        Config.setup_logging()
        
        # 驗證配置
        Config.validate_config()
        
        if Config.DB_TYPE == "sqlite":
            # 確保資料庫目錄存在
            os.makedirs(os.path.dirname(Config.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
        
        # 創建資料庫表
        db._init_db()
        
        logger.info("資料庫初始化成功")
        return True
        
    except Exception as e:
        logger.error(f"資料庫初始化失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1) 