import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database.database import engine
from shared.database.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """初始化資料庫"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ 資料庫初始化成功")
        return True
    except Exception as e:
        logger.error(f"✗ 資料庫初始化失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)