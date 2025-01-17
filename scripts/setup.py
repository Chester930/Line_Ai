import os
import sys
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_script(script_name, description):
    """運行指定的腳本"""
    logger.info(f"\n=== {description} ===")
    result = subprocess.run([sys.executable, script_name])
    return result.returncode == 0

def main():
    """執行完整的設置流程"""
    scripts = [
        ("scripts/create_directories.py", "創建目錄結構"),
        ("scripts/create_project_files.py", "創建專案文件"),
        ("scripts/create_env_example.py", "創建環境變數模板")
    ]
    
    for script, description in scripts:
        if not run_script(script, description):
            logger.error(f"{description}失敗")
            return False
        
    logger.info("\n=== 設置完成 ===")
    logger.info("請執行以下步驟：")
    logger.info("1. 複製 .env.example 到 .env")
    logger.info("2. 在 .env 中設置您的 API Keys")
    logger.info("3. 運行 python run.py 啟動應用")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 