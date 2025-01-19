import os
from dotenv import load_dotenv
from pathlib import Path

# 加載 .env 文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class Config:
    def __init__(self):
        load_dotenv()
        
        # API Keys - 從環境變數讀取，沒有則為 None
        self.GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
        
        # 模型設定
        self.MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
        self.MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', '0.7'))
        self.MODEL_TOP_P = float(os.getenv('MODEL_TOP_P', '0.9'))
        self.MAX_OUTPUT_TOKENS = int(os.getenv('MAX_OUTPUT_TOKENS', '2000'))
        
        # 已啟用的模型
        self.GOOGLE_ENABLED_MODELS = os.getenv('GOOGLE_ENABLED_MODELS', '').split(',')
        self.OPENAI_ENABLED_MODELS = os.getenv('OPENAI_ENABLED_MODELS', '').split(',')
        self.CLAUDE_ENABLED_MODELS = os.getenv('CLAUDE_ENABLED_MODELS', '').split(',')
        
        # 預設模型
        self.DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gemini-2.0-flash-exp')
        
        # LINE Bot Settings
        self.LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
        self.LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.LINE_BOT_ID = os.getenv('LINE_BOT_ID')
        
        # Google API Settings
        self.GOOGLE_ENABLED_MODELS = os.getenv('GOOGLE_ENABLED_MODELS', 'gemini-pro').split(',')
        
        # Database Settings
        self.DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/line_ai.db')
        
        # Ngrok Settings
        self.NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN')
        
        # AI Model Settings
        self.MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', '0.7'))
        self.MODEL_TOP_P = float(os.getenv('MODEL_TOP_P', '0.9'))
        self.MAX_OUTPUT_TOKENS = int(os.getenv('MAX_OUTPUT_TOKENS', '2000'))
        
        # Logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        # Directories
        self.BASE_DIR = Path(__file__).parent.parent.parent
        self.DATA_DIR = self.BASE_DIR / 'data'
        self.UPLOAD_DIR = self.BASE_DIR / 'uploads'
        self.LOG_DIR = self.BASE_DIR / 'logs'
    
    @classmethod
    def validate(cls):
        """驗證必要的配置"""
        required = [
            'LINE_CHANNEL_SECRET',
            'LINE_CHANNEL_ACCESS_TOKEN',
            'NGROK_AUTH_TOKEN'
        ]
        
        missing = []
        for key in required:
            if not getattr(cls, key):
                missing.append(key)
        
        # 檢查是否至少有一個 AI API
        if not any([cls.GOOGLE_API_KEY, cls.OPENAI_API_KEY, cls.CLAUDE_API_KEY]):
            missing.append('需要至少設定一個 AI API Key')
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    @classmethod
    def update_api_key(cls, provider: str, api_key: str):
        """更新 API Key 到環境變數和 .env 文件"""
        env_var_name = f"{provider.upper()}_API_KEY"
        
        # 更新環境變數
        os.environ[env_var_name] = api_key
        
        # 更新 .env 文件
        env_path = Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            # 讀取現有的 .env 內容
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 尋找並更新或添加 API key
            key_found = False
            for i, line in enumerate(lines):
                if line.startswith(f"{env_var_name}="):
                    lines[i] = f"{env_var_name}={api_key}\n"
                    key_found = True
                    break
            
            if not key_found:
                lines.append(f"{env_var_name}={api_key}\n")
            
            # 寫回文件
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
    
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

class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def init_app(cls, app):
        """生產環境特定的初始化"""
        super().init_app(app)
        
        # 在生產環境中使用更安全的設定
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['REMEMBER_COOKIE_SECURE'] = True

class TestingConfig(Config):
    """測試環境配置"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    DATABASE_URL = 'sqlite:///:memory:'  # 使用記憶體資料庫

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}