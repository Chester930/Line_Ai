import os
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from shared.config.config import Config

def init_config():
    """初始化配置文件"""
    config = Config(
        OPENAI_API_KEY="",
        GOOGLE_API_KEY="",
        ANTHROPIC_API_KEY="",
        LINE_CHANNEL_SECRET="",
        LINE_CHANNEL_ACCESS_TOKEN=""
    )
    config.save()
    print("配置文件已創建：", config.CONFIG_PATH)

if __name__ == "__main__":
    init_config() 