import os
from dotenv import load_dotenv
from pathlib import Path

# 加載 .env 文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class Config:
    # LINE Bot Settings
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    
    # Google API Settings
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Database Settings
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/line_ai.db')
    
    # Ngrok Settings
    NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN')
    
    # AI Model Settings
    MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-pro')
    MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', '0.7'))
    MODEL_TOP_P = float(os.getenv('MODEL_TOP_P', '0.9'))
    MAX_OUTPUT_TOKENS = int(os.getenv('MAX_OUTPUT_TOKENS', '2000'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Directories
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / 'data'
    UPLOAD_DIR = BASE_DIR / 'uploads'
    LOG_DIR = BASE_DIR / 'logs'
    
    @classmethod
    def validate(cls):
        """驗證必要的配置"""
        required = [
            'LINE_CHANNEL_SECRET',
            'LINE_CHANNEL_ACCESS_TOKEN',
            'GOOGLE_API_KEY',
            'NGROK_AUTH_TOKEN'
        ]
        
        missing = []
        for key in required:
            if not getattr(cls, key):
                missing.append(key)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")