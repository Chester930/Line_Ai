import os
from pathlib import Path
import logging

def init_project():
    """初始化專案目錄結構和配置"""
    # 專案根目錄
    root_dir = Path(__file__).parent.parent
    
    # 創建必要的目錄
    directories = [
        'logs',
        'data',
        'data/config',
        'data/uploads',
        'data/vector_store',
        'assets',
        'temp'
    ]
    
    for directory in directories:
        dir_path = root_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"創建目錄: {dir_path}")
    
    # 創建 .env 範本（如果不存在）
    env_example = root_dir / '.env.example'
    if not env_example.exists():
        with open(env_example, 'w', encoding='utf-8') as f:
            f.write("""# LINE Bot 設定
LINE_CHANNEL_SECRET=
LINE_CHANNEL_ACCESS_TOKEN=
LINE_BOT_ID=

# AI API Keys
OPENAI_API_KEY=
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=

# 資料庫設定
DATABASE_URL=sqlite:///data/app.db

# Ngrok 設定
NGROK_AUTH_TOKEN=
NGROK_REGION=ap

# 日誌設定
LOG_LEVEL=INFO

# 模型設定
MODEL_NAME=gemini-pro
MODEL_TEMPERATURE=0.7
MODEL_TOP_P=0.9
MAX_OUTPUT_TOKENS=2000

# 已啟用的模型
GOOGLE_ENABLED_MODELS=gemini-pro
OPENAI_ENABLED_MODELS=gpt-4-turbo-preview,gpt-3.5-turbo
CLAUDE_ENABLED_MODELS=claude-3-opus-20240229
""")
        print("創建 .env.example 文件")
    
    # 創建空的 .gitkeep 文件
    for directory in directories:
        gitkeep = root_dir / directory / '.gitkeep'
        if not gitkeep.exists():
            gitkeep.touch()
            print(f"創建 .gitkeep: {gitkeep}")

if __name__ == "__main__":
    try:
        init_project()
        print("專案初始化完成")
    except Exception as e:
        print(f"初始化失敗: {str(e)}") 