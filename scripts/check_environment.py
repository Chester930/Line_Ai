import sys
import os
import importlib
import logging
import pkg_resources
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """檢查依賴項"""
    required_packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'sqlalchemy': 'sqlalchemy',
        'python-dotenv': 'dotenv',  # 修正：實際導入名稱
        'pydantic': 'pydantic',
        'line-bot-sdk': 'linebot',  # 修正：實際導入名稱
        'langchain': 'langchain',
        'sentence-transformers': 'sentence_transformers',  # 修正：實際導入名稱
        'streamlit': 'streamlit',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'psutil': 'psutil',
        'requests': 'requests'
    }
    
    missing = []
    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    
    for package, import_name in required_packages.items():
        try:
            importlib.import_module(import_name)
            version = installed_packages.get(package, "unknown version")
            logger.info(f"✓ {package} ({version})")
        except ImportError:
            missing.append(package)
            logger.error(f"✗ {package}")
    
    if missing:
        logger.info("\n缺少的依賴項：")
        logger.info(f"pip install {' '.join(missing)}")
    
    return len(missing) == 0

def check_directories():
    """檢查目錄結構"""
    required_dirs = [
        Config.DATA_DIR,
        Config.UPLOAD_DIR,
        Config.LOG_DIR,
        os.path.join(Config.BASE_DIR, "admin"),
        os.path.join(Config.BASE_DIR, "shared"),
        os.path.join(Config.BASE_DIR, "ui")
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if os.path.exists(directory):
            logger.info(f"✓ {directory}")
        else:
            missing_dirs.append(directory)
            logger.error(f"✗ {directory}")
    
    if missing_dirs:
        logger.info("\n缺少的目錄：")
        for directory in missing_dirs:
            logger.info(f"mkdir {directory}")
    
    return len(missing_dirs) == 0

def check_config_files():
    """檢查配置文件"""
    required_files = [
        os.path.join(Config.BASE_DIR, ".env"),
        os.path.join(Config.BASE_DIR, "requirements.txt")
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.info(f"✓ {file_path}")
        else:
            missing_files.append(file_path)
            logger.error(f"✗ {file_path}")
    
    return len(missing_files) == 0

def main():
    logger.info("檢查環境配置...")
    
    # 檢查依賴
    logger.info("\n檢查依賴項:")
    deps_ok = check_dependencies()
    
    # 檢查目錄
    logger.info("\n檢查目錄結構:")
    dirs_ok = check_directories()
    
    # 檢查配置文件
    logger.info("\n檢查配置文件:")
    files_ok = check_config_files()
    
    # 檢查配置
    logger.info("\n檢查配置:")
    try:
        Config.validate_config()
        logger.info("✓ 配置驗證通過")
        config_ok = True
    except Exception as e:
        logger.error(f"✗ 配置驗證失敗: {str(e)}")
        config_ok = False
    
    # 總結
    logger.info("\n檢查結果:")
    logger.info(f"依賴項: {'✓' if deps_ok else '✗'}")
    logger.info(f"目錄結構: {'✓' if dirs_ok else '✗'}")
    logger.info(f"配置文件: {'✓' if files_ok else '✗'}")
    logger.info(f"配置內容: {'✓' if config_ok else '✗'}")
    
    return all([deps_ok, dirs_ok, files_ok, config_ok])

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)