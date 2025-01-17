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