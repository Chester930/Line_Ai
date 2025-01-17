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
    LINE_BOT_ID = os.getenv('LINE_BOT_ID')
    
    # Google API Settings
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_ENABLED_MODELS = os.getenv('GOOGLE_ENABLED_MODELS', 'gemini-pro').split(',')
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ENABLED_MODELS = os.getenv('OPENAI_ENABLED_MODELS', 'gpt-3.5-turbo').split(',')
    
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_ENABLED_MODELS = os.getenv('ANTHROPIC_ENABLED_MODELS', 'claude-3-opus').split(',')
    
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gemini-pro')
    
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
            'NGROK_AUTH_TOKEN'
        ]
        
        # 確保至少有一個 AI API Key
        ai_apis = [
            cls.GOOGLE_API_KEY,
            cls.OPENAI_API_KEY,
            cls.CLAUDE_API_KEY
        ]
        if not any(ai_apis):
            missing.append('需要至少一個 AI API Key')
        
        missing = []
        for key in required:
            if not getattr(cls, key):
                missing.append(key)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    @classmethod
    def get_available_models(cls):
        """獲取所有可用的模型"""
        models = []
        if cls.GOOGLE_API_KEY:
            models.extend(cls.GOOGLE_ENABLED_MODELS)
        if cls.OPENAI_API_KEY:
            models.extend(cls.OPENAI_ENABLED_MODELS)
        if cls.CLAUDE_API_KEY:
            models.extend(cls.CLAUDE_ENABLED_MODELS)
        return models