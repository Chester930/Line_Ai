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
    """確保必要的目錄存在"""
    directories = ['config', 'data', 'uploads', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def main():
    project_status = ProjectStatus()
    
    # 如果是首次運行，直接啟動管理員介面
    if project_status.is_first_run():
        logger.info("首次運行，啟動管理員介面")
        run_admin()
        project_status.mark_first_run_complete()
        return
    
    # 檢查 LINE BOT 是否在運行
    if project_status.is_bot_running():
        logger.error("LINE BOT 正在運行中，請先關閉後再進行設定")
        sys.exit(1)
    
    # 解析命令行參數
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

def run_admin():
    """運行管理員界面"""
    try:
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", "admin/admin_ui.py"]
        logger.info("Starting admin interface...")
        sys.exit(stcli.main())
    except Exception as e:
        logger.error(f"Error running admin interface: {e}")
        sys.exit(1)

def run_app():
    """運行主應用程式"""
    from shared.config.settings_manager import SettingsManager
    import subprocess
    import yaml
    import time
    from flask import Flask
    
    settings_manager = SettingsManager()
    if not settings_manager.is_initialized():
        logger.error("System not initialized. Please run in admin mode first.")
        sys.exit(1)
    
    try:
        # 建立 ngrok 設定檔
        ngrok_config = {
            "version": "2",
            "authtoken": settings_manager.get_api_key("ngrok_auth_token"),
            "tunnels": {
                "line-bot": {
                    "proto": "http",
                    "addr": "5000"
                }
            }
        }
        
        config_path = "ngrok.yml"
        with open(config_path, "w") as f:
            yaml.dump(ngrok_config, f)
        
        # 啟動 ngrok
        ngrok_process = subprocess.Popen(
            ["ngrok", "start", "line-bot", "--config", config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待 ngrok 啟動
        time.sleep(3)
        
        # 啟動 Line Bot 應用
        from ui.line_bot_ui import app
        app.run(host='0.0.0.0', port=5000)
        
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        raise
    finally:
        if 'ngrok_process' in locals():
            ngrok_process.terminate()
        if os.path.exists(config_path):
            os.remove(config_path)

if __name__ == "__main__":
    ensure_directories()
    main() 