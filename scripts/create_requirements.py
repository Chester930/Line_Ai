import os

def create_requirements():
    content = """# LINE Bot
flask==3.0.0
line-bot-sdk>=3.7.0
aiohttp>=3.9.1

# Database
sqlalchemy==2.0.23

# AI & ML
google-generativeai==0.3.1
sentence-transformers==2.2.2

# Config
python-dotenv==1.0.0
pydantic==2.5.2

# UI
streamlit==1.29.0
watchdog==3.0.0

# Utils
psutil==5.9.6
requests==2.31.0
python-multipart==0.0.6
"""
    
    # 使用 UTF-8 編碼寫入
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    create_requirements() 