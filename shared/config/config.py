import os
from dotenv import load_dotenv
from pathlib import Path

# 獲取項目根目錄
ROOT_DIR = Path(__file__).parent.parent.parent

# 加載環境變數
load_dotenv(ROOT_DIR / '.env')

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
        
        missing_fields = [
            field for field in required_fields
            if not getattr(cls, field)
        ]
        
        if missing_fields:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_fields)}"
            )