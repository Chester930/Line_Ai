import argparse
import logging
from shared.database.database import init_db, check_database_connection
import subprocess
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='啟動 AI 助手')
    parser.add_argument('--mode', choices=['admin', 'line'], required=True, help='選擇運行模式')
    args = parser.parse_args()
    
    # 初始化資料庫
    logger.info("正在檢查並初始化資料庫...")
    if not check_database_connection():
        logger.error("資料庫連接失敗")
        return
    
    # 根據運行模式啟動不同的介面
    if args.mode == 'admin':
        logger.info("啟動管理員介面...")
        subprocess.run(["streamlit", "run", "admin/views/test_view.py"])
    elif args.mode == 'line':
        logger.info("啟動 LINE Bot...")
        from line_bot.app import app
        app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()