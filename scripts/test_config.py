import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config.config import Config
from shared.database.database import db
import logging

logger = logging.getLogger(__name__)

def test_configuration():
    """測試配置和連接"""
    try:
        # 設置日誌
        Config.setup_logging()
        
        # 測試配置驗證
        logger.info("測試配置驗證...")
        Config.validate_config()
        logger.info("配置驗證成功")
        
        # 測試資料庫連接
        logger.info("測試資料庫連接...")
        session = next(db.get_session())
        session.execute("SELECT 1")
        logger.info("資料庫連接成功")
        
        return True
        
    except Exception as e:
        logger.error(f"測試失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_configuration()
    sys.exit(0 if success else 1) 