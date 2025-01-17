import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_project_structure():
    """創建專案目錄結構"""
    directories = [
        "admin",
        "shared",
        "shared/config",
        "shared/database",
        "shared/utils",
        "shared/line_sdk",
        "ui",
        "data",
        "uploads",
        "logs"
    ]
    
    base_dir = Config.BASE_DIR
    
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        try:
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"✓ 創建目錄: {dir_path}")
        except Exception as e:
            logger.error(f"✗ 創建目錄失敗 {dir_path}: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    success = create_project_structure()
    sys.exit(0 if success else 1) 