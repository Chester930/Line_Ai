import sys
import os
import subprocess
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_test(command, description):
    """運行測試命令"""
    logger.info(f"\n=== 測試 {description} ===")
    try:
        # 分開顯示 stdout 和 stderr
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 即時輸出日誌
        while True:
            output = process.stdout.readline()
            error = process.stderr.readline()
            
            if output == '' and error == '' and process.poll() is not None:
                break
                
            if output:
                logger.info(output.strip())
            if error:
                logger.error(error.strip())
        
        rc = process.poll()
        
        if rc == 0:
            logger.info(f"✓ {description} 測試通過")
            return True
        else:
            logger.error(f"✗ {description} 測試失敗 (返回碼: {rc})")
            return False
            
    except Exception as e:
        logger.error(f"✗ {description} 執行出錯：{str(e)}")
        return False

def main():
    """運行所有測試"""
    tests = [
        ("pip install -r requirements.txt", "安裝依賴"),
        ("python scripts/check_environment.py", "環境檢查"),
        ("python scripts/init_db.py", "初始化資料庫"),
        ("python scripts/test_ngrok.py", "Ngrok 測試")
    ]
    
    results = []
    for command, description in tests:
        success = run_test(command, description)
        results.append((description, success))
        if not success:
            logger.error(f"\n{description} 失敗，停止後續測試")
            break
    
    # 顯示測試結果摘要
    logger.info("\n=== 測試結果摘要 ===")
    for description, success in results:
        status = "✓" if success else "✗"
        logger.info(f"{status} {description}")
    
    # 如果所有測試都通過，運行完整流程
    if all(success for _, success in results):
        logger.info("\n所有測試通過，啟動應用...")
        try:
            subprocess.run(["python", "run.py"], check=True)
        except KeyboardInterrupt:
            logger.info("應用已停止")
        except Exception as e:
            logger.error(f"應用運行出錯：{str(e)}")

if __name__ == "__main__":
    main() 