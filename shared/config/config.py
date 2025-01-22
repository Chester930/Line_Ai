import os
from dotenv import load_dotenv, dotenv_values
from pathlib import Path
import requests
from typing import Any, Optional

# 加載 .env 文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class Config:
    """配置管理類"""
    
    def __init__(self):
        # 加載 .env 文件
        env_path = Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        
        # API Keys
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
        self.GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
        self.ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
        
        # LINE 設定
        self.LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')
        self.LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
        
        # Ngrok 設定
        self.NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN', '')
        
        # 資料庫設定
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/app.db')
        
        # 模型設定
        self.DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gemini-pro')
        self.MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', '0.7'))
        self.MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))
        self.TOP_P = float(os.getenv('TOP_P', '0.9'))
        self.PRESENCE_PENALTY = float(os.getenv('PRESENCE_PENALTY', '0.0'))
        self.FREQUENCY_PENALTY = float(os.getenv('FREQUENCY_PENALTY', '0.0'))
        
        # 已啟用的模型
        self.GOOGLE_ENABLED_MODELS = os.getenv('GOOGLE_ENABLED_MODELS', '').split(',')
        self.OPENAI_ENABLED_MODELS = os.getenv('OPENAI_ENABLED_MODELS', '').split(',')
        self.CLAUDE_ENABLED_MODELS = os.getenv('CLAUDE_ENABLED_MODELS', '').split(',')
        
        # LINE Bot Settings
        self.LINE_BOT_ID = os.getenv('LINE_BOT_ID', '')
        
        # Google API Settings
        self.GOOGLE_ENABLED_MODELS = os.getenv('GOOGLE_ENABLED_MODELS', 'gemini-pro').split(',')
        
        # Database Settings
        self.DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
        
        # Ngrok Settings
        self.NGROK_REGION = os.getenv('NGROK_REGION', 'ap')
        
        # AI Model Settings
        self.MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', '0.7'))
        self.MODEL_TOP_P = float(os.getenv('MODEL_TOP_P', '0.9'))
        self.MAX_OUTPUT_TOKENS = int(os.getenv('MAX_OUTPUT_TOKENS', '2000'))
        
        # Logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        # Directories
        self.BASE_DIR = Path(__file__).parent.parent.parent
        self.DATA_DIR = self.BASE_DIR / 'data'
        self.CONFIG_DIR = self.DATA_DIR / 'config'
        self.UPLOAD_DIR = self.DATA_DIR / 'uploads'
        self.LOG_DIR = self.DATA_DIR / 'logs'
        
        # 確保必要目錄存在
        for directory in [self.DATA_DIR, self.CONFIG_DIR, self.UPLOAD_DIR, self.LOG_DIR]:
            os.makedirs(directory, exist_ok=True)
        
        # 設置基本路徑
        self.base_path = Path(__file__).parent.parent.parent
        
        # 創建必要的目錄
        self.directories = {
            'BASE_PATH': self.base_path,
            'VECTOR_STORE_PATH': self.base_path / 'data' / 'vectors',
            'JSON_STORE_PATH': self.base_path / 'data' / 'json_store',
            'TEMP_PATH': self.base_path / 'data' / 'temp',
            'LOG_PATH': self.base_path / 'data' / 'logs'
        }
        
        # 創建所有必要的目錄
        for path in self.directories.values():
            path.mkdir(parents=True, exist_ok=True)
    
    def check_api_connection(self) -> bool:
        """檢查 API 連接狀態"""
        try:
            # 測試 Google API
            if self.GOOGLE_API_KEY:
                response = requests.get(
                    'https://generativelanguage.googleapis.com/v1beta/models',
                    params={'key': self.GOOGLE_API_KEY}
                )
                if response.status_code != 200:
                    return False
            
            # 測試 OpenAI API
            if self.OPENAI_API_KEY:
                headers = {'Authorization': f'Bearer {self.OPENAI_API_KEY}'}
                response = requests.get(
                    'https://api.openai.com/v1/models',
                    headers=headers
                )
                if response.status_code != 200:
                    return False
            
            return True
        except:
            return False
    
    def check_webhook_status(self) -> bool:
        """檢查 Webhook 狀態"""
        try:
            if not (self.LINE_CHANNEL_SECRET and self.LINE_CHANNEL_ACCESS_TOKEN):
                return False
                
            headers = {
                'Authorization': f'Bearer {self.LINE_CHANNEL_ACCESS_TOKEN}'
            }
            response = requests.get(
                'https://api.line.me/v2/bot/channel/webhook/endpoint',
                headers=headers
            )
            
            return response.status_code == 200
        except:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        # 首先檢查目錄配置
        if key in self.directories:
            return str(self.directories[key])
            
        # 然後檢查環境變數
        return os.getenv(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """設置配置值"""
        os.environ[key] = str(value)
    
    def update(self, settings: dict):
        """更新配置"""
        for key, value in settings.items():
            setattr(self, key, value)
    
    def validate(self):
        """驗證必要的配置"""
        required = [
            ('LINE_CHANNEL_SECRET', self.LINE_CHANNEL_SECRET),
            ('LINE_CHANNEL_ACCESS_TOKEN', self.LINE_CHANNEL_ACCESS_TOKEN),
            ('NGROK_AUTH_TOKEN', self.NGROK_AUTH_TOKEN)
        ]
        
        missing = []
        for name, value in required:
            if not value:
                missing.append(name)
        
        # 檢查是否至少有一個 AI API
        if not any([self.GOOGLE_API_KEY, self.OPENAI_API_KEY, self.ANTHROPIC_API_KEY]):
            missing.append('需要至少設定一個 AI API Key')
        
        if missing:
            raise ValueError(f"缺少必要的設定: {', '.join(missing)}")
        
        return True
    
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
        if cls.ANTHROPIC_API_KEY:
            models.extend(cls.CLAUDE_ENABLED_MODELS)
        return models

    def update_config(self, updates: dict):
        """更新設定"""
        env_path = Path(__file__).parent.parent.parent / '.env'
        
        # 讀取當前設定
        if env_path.exists():
            current_env = dotenv_values(env_path)
        else:
            current_env = {}
        
        # 更新設定
        current_env.update(updates)
        
        # 寫入文件
        with open(env_path, 'w', encoding='utf-8') as f:
            for key, value in current_env.items():
                f.write(f"{key}={value}\n")
        
        # 更新實例屬性
        for key, value in updates.items():
            setattr(self, key, value)

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