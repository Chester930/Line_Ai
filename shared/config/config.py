import os
from dotenv import load_dotenv
import logging

# 載入環境變數
load_dotenv()

class Config:
    # 基礎路徑設定
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    
    # 確保必要目錄存在
    for directory in [DATA_DIR, UPLOAD_DIR, LOG_DIR]:
        os.makedirs(directory, exist_ok=True)
    
    # 資料庫設定
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    if DB_TYPE == "sqlite":
        DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            f"sqlite:///{os.path.join(DATA_DIR, 'line_ai.db')}"
        )
    else:
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/line_ai_db")
    
    # LINE Bot 設定
    LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    
    # Ngrok 設定
    NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
    
    # AI 模型設定
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-pro")
    MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    MODEL_TOP_P = float(os.getenv("MODEL_TOP_P", "0.9"))
    MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "2000"))
    
    # 日誌設定
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = os.path.join(LOG_DIR, "app.log")