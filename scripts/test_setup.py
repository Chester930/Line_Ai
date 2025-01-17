import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config.config import Config
from shared.utils.role_manager import RoleManager
from shared.database.database import engine, Base
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_config():
    """測試配置"""
    required_vars = [
        "LINE_CHANNEL_SECRET",
        "LINE_CHANNEL_ACCESS_TOKEN",
        "GOOGLE_API_KEY",
        "NGROK_AUTH_TOKEN"
    ]
    
    missing = []
    for var in required_vars:
        if not getattr(Config, var):
            missing.append(var)
    
    if missing:
        logger.error(f"缺少必要的環境變數: {', '.join(missing)}")
        return False
    
    logger.info("✓ 配置檢查通過")
    return True

def test_database():
    """測試資料庫"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ 資料庫連接成功")
        return True
    except Exception as e:
        logger.error(f"資料庫連接失敗: {str(e)}")
        return False

def test_ai_model():
    """測試 AI 模型"""
    try:
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        logger.info("✓ AI 模型測試成功")
        return True
    except Exception as e:
        logger.error(f"AI 模型測試失敗: {str(e)}")
        return False

def main():
    """運行所有測試"""
    tests = [
        ("配置測試", test_config),
        ("資料庫測試", test_database),
        ("AI 模型測試", test_ai_model)
    ]
    
    success = True
    for name, test in tests:
        logger.info(f"\n=== {name} ===")
        if not test():
            success = False
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 