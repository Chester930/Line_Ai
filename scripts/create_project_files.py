import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_project_root():
    """獲取專案根目錄"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_files():
    """創建專案文件"""
    base_dir = get_project_root()
    files_to_create = {
        # 配置文件
        "shared/config/config.py": """
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
""",
        
        # UI 相關
        "ui/line_bot_ui.py": """
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from shared.config.config import Config

app = Flask(__name__)

line_bot_api = LineBotApi(Config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # TODO: 實現消息處理邏輯
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )

if __name__ == "__main__":
    app.run(port=5000)
""",
        
        # 工具類
        "shared/utils/notification_manager.py": """
import logging
from linebot.models import TextSendMessage
from shared.config.config import Config

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
    
    def send_notification(self, user_id, message):
        try:
            self.line_bot_api.push_message(
                user_id,
                TextSendMessage(text=message)
            )
            return True
        except Exception as e:
            logger.error(f"發送通知失敗: {str(e)}")
            return False
""",
        
        # 主程序
        "run.py": """
import argparse
import sys
import os
import logging
from pathlib import Path
import psutil
import json

logger = logging.getLogger(__name__)

class ProjectStatus:
    def __init__(self):
        self.status_file = "data/project_status.json"
        self.ensure_status_file()
    
    def ensure_status_file(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.status_file):
            self.save_status({"first_run": True, "bot_running": False})
    
    def save_status(self, status):
        with open(self.status_file, 'w') as f:
            json.dump(status, f)
    
    def load_status(self):
        with open(self.status_file, 'r') as f:
            return json.load(f)
    
    def is_first_run(self):
        return self.load_status().get("first_run", True)
    
    def mark_first_run_complete(self):
        status = self.load_status()
        status["first_run"] = False
        self.save_status(status)
    
    def set_bot_status(self, running: bool):
        status = self.load_status()
        status["bot_running"] = running
        self.save_status(status)
    
    def is_bot_running(self):
        return self.load_status().get("bot_running", False)

def ensure_directories():
    directories = ['config', 'data', 'uploads', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def main():
    project_status = ProjectStatus()
    
    if project_status.is_first_run():
        logger.info("首次運行，啟動管理員介面")
        run_admin()
        project_status.mark_first_run_complete()
        return
    
    if project_status.is_bot_running():
        logger.error("LINE BOT 正在運行中，請先關閉後再進行設定")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description='Run Line AI Assistant')
    parser.add_argument('--mode', type=str, choices=['admin', 'app'], 
                       help='Choose the mode: admin or app')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'app':
            project_status.set_bot_status(True)
            run_app()
        else:
            run_admin()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        project_status.set_bot_status(False)

if __name__ == "__main__":
    ensure_directories()
    main()
"""
    }
    
    for file_path, content in files_to_create.items():
        target_path = os.path.join(base_dir, file_path)
        try:
            # 確保目標目錄存在
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # 寫入文件內容
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            
            logger.info(f"✓ 創建: {file_path}")
            
        except Exception as e:
            logger.error(f"✗ 創建失敗 {file_path}: {str(e)}")
            return False
    
    return True

def create_init_files():
    """創建 __init__.py 文件"""
    base_dir = get_project_root()
    python_dirs = [
        "shared",
        "shared/config",
        "shared/database",
        "shared/utils",
        "shared/line_sdk",
        "ui",
        "admin"
    ]
    
    for directory in python_dirs:
        init_file = os.path.join(base_dir, directory, "__init__.py")
        try:
            os.makedirs(os.path.dirname(init_file), exist_ok=True)
            open(init_file, 'a').close()
            logger.info(f"✓ 創建: {init_file}")
        except Exception as e:
            logger.error(f"✗ 創建失敗 {init_file}: {str(e)}")
            return False
    
    return True

def main():
    """執行創建流程"""
    logger.info("開始創建文件...")
    
    # 創建文件
    if not create_files():
        logger.error("創建文件失敗")
        return False
    
    # 創建 __init__.py 文件
    if not create_init_files():
        logger.error("創建 __init__.py 文件失敗")
        return False
    
    logger.info("創建完成")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)