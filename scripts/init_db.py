import os
import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from shared.database.base import Base, engine
from shared.database import models

def init_db():
    """初始化數據庫"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 