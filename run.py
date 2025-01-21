import argparse
import sys
import os
import logging
from pathlib import Path
import psutil
import json
from ui.line_bot_ui import start_line_bot
import streamlit.web.bootstrap as bootstrap
from shared.database.database import init_db, check_database_connection

# 設置日誌
logging.basicConfig(level=logging.INFO)
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
    """確保必要的目錄存在"""
    directories = ['data', 'data/config', 'data/uploads', 'data/logs']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def run_admin():
    """運行管理員界面"""
    try:
        import streamlit.web.cli as stcli
        import sys
        
        sys.argv = ["streamlit", "run", "admin/admin_ui.py"]
        logger.info("Starting admin interface...")
        sys.exit(stcli.main())
    except Exception as e:
        logger.error(f"Error running admin interface: {e}")
        sys.exit(1)

def run_app():
    """運行主應用程式"""
    try:
        from shared.utils.ngrok_manager import NgrokManager
        from ui.line_bot_ui import app
        
        # 啟動 ngrok
        ngrok = NgrokManager()
        webhook_url = ngrok.start()
        logger.info(f"Webhook URL: {webhook_url}")
        
        # 啟動 Line Bot 應用
        app.run(host='0.0.0.0', port=5000)
        
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        raise
    finally:
        if 'ngrok' in locals():
            ngrok.stop()

def main():
    parser = argparse.ArgumentParser(description='Line AI Assistant')
    parser.add_argument('--mode', type=str, required=True, 
                       choices=['bot', 'admin', 'studio'],
                       help='運行模式: bot/admin/studio')
    
    args = parser.parse_args()
    
    try:
        # 檢查並初始化資料庫
        if not check_database_connection():
            logger.info("Initializing database...")
            if not init_db():
                logger.error("Failed to initialize database")
                return
        
        if args.mode == 'bot':
            logger.info("啟動 LINE Bot 服務...")
            start_line_bot()
        elif args.mode == 'admin':
            logger.info("啟動管理員介面...")
            bootstrap.run("admin/admin_ui.py", "", [], {})
        elif args.mode == 'studio':
            logger.info("啟動 Studio 開發環境...")
            bootstrap.run("studio/studio_ui.py", "", [], {})
    except KeyboardInterrupt:
        logger.info("服務已停止")
    except Exception as e:
        logger.error(f"發生錯誤: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    ensure_directories()
    main()