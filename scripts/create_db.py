import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config.config import Config
import logging

logger = logging.getLogger(__name__)

def create_database():
    """創建 PostgreSQL 資料庫"""
    try:
        # 解析資料庫 URL
        db_url = Config.DATABASE_URL
        db_parts = db_url.split('/')
        db_name = db_parts[-1]
        db_host = db_parts[2].split('@')[-1].split(':')[0]
        db_user = db_parts[2].split(':')[0].split('//')[1]
        db_password = db_parts[2].split(':')[1].split('@')[0]
        
        # 連接到 PostgreSQL
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # 創建資料庫
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE {db_name}")
        
        logger.info(f"資料庫 {db_name} 創建成功")
        return True
        
    except psycopg2.Error as e:
        if "already exists" in str(e):
            logger.info(f"資料庫 {db_name} 已存在")
            return True
        logger.error(f"創建資料庫失敗: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # 設置日誌
    Config.setup_logging()
    
    success = create_database()
    sys.exit(0 if success else 1) 