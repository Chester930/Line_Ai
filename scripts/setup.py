import os
import sys
import logging
import subprocess
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_script(script_name, description):
    """運行指定的腳本"""
    logger.info(f"\n=== {description} ===")
    result = subprocess.run([sys.executable, script_name])
    return result.returncode == 0

def copy_env_example():
    """複製 .env.example 到 .env"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_example = os.path.join(base_dir, ".env.example")
        env_file = os.path.join(base_dir, ".env")
        
        if not os.path.exists(env_file):
            shutil.copy2(env_example, env_file)
            logger.info("✓ 創建 .env 文件")
        else:
            logger.info("! .env 文件已存在")
        return True
    except Exception as e:
        logger.error(f"✗ 創建 .env 文件失敗: {str(e)}")
        return False

def migrate_from_old_project():
    """從舊專案遷移配置"""
    try:
        # 獲取專案路徑
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        old_project_dir = os.path.join(os.path.dirname(current_dir), "FK_AI_Theology_Doctor")
        
        # 只遷移 .env 文件
        old_env = os.path.join(old_project_dir, ".env")
        new_env = os.path.join(current_dir, ".env")
        
        if os.path.exists(old_env):
            shutil.copy2(old_env, new_env)
            logger.info(f"✓ 遷移: .env")
            return True
        else:
            logger.warning("! 源 .env 文件不存在")
            return False
            
    except Exception as e:
        logger.error(f"✗ 遷移失敗: {str(e)}")
        return False

def main():
    """執行完整的設置流程"""
    scripts = [
        ("scripts/create_directories.py", "創建目錄結構"),
        ("scripts/create_project_files.py", "創建專案文件"),
        ("scripts/create_env_example.py", "創建環境變數模板")
    ]
    
    # 運行所有腳本
    for script, description in scripts:
        if not run_script(script, description):
            logger.error(f"{description}失敗")
            return False
    
    # 複製 .env.example 到 .env
    if not copy_env_example():
        return False
    
    # 嘗試從舊專案遷移配置
    logger.info("\n=== 遷移舊專案配置 ===")
    if migrate_from_old_project():
        logger.info("✓ 配置遷移成功")
    else:
        logger.warning("! 配置遷移失敗，請手動設置配置")
    
    logger.info("\n=== 設置完成 ===")
    logger.info("請確認以下文件：")
    logger.info("1. .env - 檢查並更新配置")
    logger.info("2. ngrok.yml - 確認 ngrok 配置")
    logger.info("\n運行應用：")
    logger.info("python run.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 