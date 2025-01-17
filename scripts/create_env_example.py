import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_env_example():
    """創建 .env.example 文件"""
    content = """# LINE Bot Settings
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token

# Database Settings (可選)
DB_TYPE=sqlite  # 或 postgresql
DATABASE_URL=your_database_url  # 如果使用 postgresql

# Ngrok Settings
NGROK_AUTH_TOKEN=your_ngrok_token

# AI Model Settings (可選)
MODEL_NAME=gemini-pro
MODEL_TEMPERATURE=0.7
MODEL_TOP_P=0.9
MAX_OUTPUT_TOKENS=2000

# Logging
LOG_LEVEL=INFO
"""
    
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_example_path = os.path.join(base_dir, ".env.example")
        
        with open(env_example_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✓ 創建: .env.example")
        return True
    except Exception as e:
        logger.error(f"✗ 創建 .env.example 失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_env_example()
    exit(0 if success else 1) 