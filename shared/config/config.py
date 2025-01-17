import os
from dotenv import load_dotenv
from pathlib import Path
import logging

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 獲取項目根目錄
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_PATH = ROOT_DIR / '.env'

# 加載環境變數
if ENV_PATH.exists():
    logger.info(f"Loading .env file from: {ENV_PATH}")
    load_dotenv(ENV_PATH)
else:
    logger.warning(f"No .env file found at: {ENV_PATH}")

class Config:
    # Line Bot 設定
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    
    # Google API 設定
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Ngrok 設定
    NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN')
    
    # 服務器設定
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """驗證必要的配置是否存在"""
        required_fields = [
            'LINE_CHANNEL_ACCESS_TOKEN',
            'LINE_CHANNEL_SECRET',
            'GOOGLE_API_KEY',
            'NGROK_AUTH_TOKEN'
        ]
        
        missing_fields = []
        for field in required_fields:
            value = getattr(cls, field)
            if not value:
                logger.error(f"Missing required configuration: {field}")
                missing_fields.append(field)
            else:
                logger.info(f"Configuration loaded: {field}")
        
        if missing_fields:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_fields)}"
            )
        else:
            logger.info("All required configurations loaded successfully")

    @classmethod
    def print_config(cls):
        """打印當前配置（用於調試）"""
        logger.info("Current configuration:")
        logger.info(f"ROOT_DIR: {ROOT_DIR}")
        logger.info(f"ENV_PATH: {ENV_PATH}")
        logger.info(f"HOST: {cls.HOST}")
        logger.info(f"PORT: {cls.PORT}")
        logger.info(f"DEBUG: {cls.DEBUG}")