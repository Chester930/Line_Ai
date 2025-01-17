import os
import sys
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_env_file():
    """遷移 .env 文件的配置"""
    try:
        # 檢查是否存在舊的配置文件
        old_env_path = Path(__file__).parent.parent.parent / 'FK_AI_Theology_Doctor' / '.env'
        new_env_path = Path(__file__).parent.parent / '.env'
        
        if old_env_path.exists():
            logger.info("發現舊的配置文件，開始遷移...")
            
            # 讀取舊的配置
            with open(old_env_path, 'r', encoding='utf-8') as f:
                old_config = f.read()
            
            # 如果新的配置文件已存在，先備份
            if new_env_path.exists():
                backup_path = new_env_path.with_suffix('.env.backup')
                shutil.copy2(new_env_path, backup_path)
                logger.info(f"已備份現有配置到: {backup_path}")
            
            # 寫入新的配置文件
            with open(new_env_path, 'w', encoding='utf-8') as f:
                f.write(old_config)
            
            logger.info("✓ 配置遷移成功")
            return True
            
        else:
            logger.info("未找到舊的配置文件，跳過遷移")
            return False
            
    except Exception as e:
        logger.error(f"配置遷移失敗: {str(e)}")
        return False

def migrate_notification_settings():
    """遷移通知設定"""
    try:
        old_path = Path(__file__).parent.parent.parent / 'FK_AI_Theology_Doctor/utils/notification_manager.py'
        new_path = Path(__file__).parent.parent / 'shared/utils/notification_manager.py'
        
        if old_path.exists():
            logger.info("發現舊的通知設定，開始遷移...")
            
            # 複製文件
            if new_path.exists():
                backup_path = new_path.with_suffix('.py.backup')
                shutil.copy2(new_path, backup_path)
                logger.info(f"已備份現有通知設定到: {backup_path}")
            
            shutil.copy2(old_path, new_path)
            logger.info("✓ 通知設定遷移成功")
            return True
            
        else:
            logger.info("未找到舊的通知設定，跳過遷移")
            return False
            
    except Exception as e:
        logger.error(f"通知設定遷移失敗: {str(e)}")
        return False

def main():
    """執行所有遷移任務"""
    logger.info("\n=== 開始配置遷移 ===")
    
    # 遷移環境變數
    env_migrated = migrate_env_file()
    
    # 遷移通知設定
    notification_migrated = migrate_notification_settings()
    
    if env_migrated or notification_migrated:
        logger.info("\n遷移完成！請檢查以下文件：")
        if env_migrated:
            logger.info("1. .env - 環境變數配置")
        if notification_migrated:
            logger.info("2. shared/utils/notification_manager.py - 通知設定")
    else:
        logger.info("\n沒有需要遷移的配置")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
