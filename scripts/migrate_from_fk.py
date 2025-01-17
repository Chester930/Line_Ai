import os
import sys
import shutil
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_files():
    """從 FK_AI_Theology_Doctor 遷移文件"""
    source_project = "FK_AI_Theology_Doctor"
    files_to_migrate = {
        # 配置文件
        "config.py": ("shared/config/config.py", True),  # True 表示需要修改
        ".env": (".env", True),
        "ngrok.yml": ("ngrok.yml", False),
        
        # UI 相關
        "ui/line_bot_ui.py": ("ui/line_bot_ui.py", True),
        
        # 工具類
        "utils/notification_manager.py": ("shared/utils/notification_manager.py", True),
        
        # 主程序
        "main.py": ("run.py", True)
    }
    
    base_dir = Config.BASE_DIR
    source_base = os.path.join(os.path.dirname(base_dir), source_project)
    
    for source_file, (target_file, needs_modification) in files_to_migrate.items():
        source_path = os.path.join(source_base, source_file)
        target_path = os.path.join(base_dir, target_file)
        
        if os.path.exists(source_path):
            # 確保目標目錄存在
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            try:
                if needs_modification:
                    # 讀取並修改文件內容
                    with open(source_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 更新導入路徑
                    content = content.replace(
                        "from utils.", 
                        "from shared.utils."
                    ).replace(
                        "from config", 
                        "from shared.config.config"
                    )
                    
                    # 寫入修改後的內容
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    logger.info(f"✓ 遷移並修改: {target_file}")
                else:
                    # 直接複製文件
                    shutil.copy2(source_path, target_path)
                    logger.info(f"✓ 複製: {target_file}")
                
            except Exception as e:
                logger.error(f"✗ 遷移失敗 {target_file}: {str(e)}")
                return False
        else:
            logger.warning(f"! 源文件不存在: {source_file}")
    
    return True

def create_init_files():
    """創建 __init__.py 文件"""
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
        init_file = os.path.join(Config.BASE_DIR, directory, "__init__.py")
        try:
            open(init_file, 'a').close()
            logger.info(f"✓ 創建: {init_file}")
        except Exception as e:
            logger.error(f"✗ 創建失敗 {init_file}: {str(e)}")
            return False
    
    return True

def main():
    """執行遷移流程"""
    logger.info("開始遷移文件...")
    
    # 遷移文件
    if not migrate_files():
        logger.error("遷移文件失敗")
        return False
    
    # 創建 __init__.py 文件
    if not create_init_files():
        logger.error("創建 __init__.py 文件失敗")
        return False
    
    logger.info("遷移完成")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 