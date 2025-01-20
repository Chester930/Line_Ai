import streamlit as st
import psutil
import platform
from datetime import datetime
from shared.config.config import Config
from shared.database.database import get_db

def show_page():
    """系統狀態頁面"""
    st.header("系統狀態 (System Status)")
    
    # 系統資訊
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("系統設定 (System Settings)")
        st.write("- 資料庫類型 (Database Type)：SQLite")
        st.write("- AI 模型 (AI Model)：Gemini Pro")
        st.write("- 日誌級別 (Log Level)：INFO")
        
        # 資料庫狀態
        try:
            db = next(get_db())
            db_status = "正常 (Normal)"
            db.execute("SELECT 1")
        except Exception as e:
            db_status = f"異常 (Error: {str(e)})"
        st.write(f"- 資料庫狀態: {db_status}")
    
    with col2:
        st.info("運行狀態 (Runtime Status)")
        st.write(f"- CPU 使用率: {psutil.cpu_percent()}%")
        st.write(f"- 記憶體使用率: {psutil.virtual_memory().percent}%")
        st.write(f"- OS: {platform.system()} {platform.version()}")
        st.write(f"- Python: {platform.python_version()}")
        
        # API 連接狀態
        config = Config()
        api_status = check_api_status(config)
        st.write(f"- API 連接: {api_status}")
    
    # 系統日誌
    st.subheader("系統日誌 (System Logs)")
    show_system_logs()

def check_api_status(config: Config) -> str:
    """檢查 API 狀態"""
    if not any([config.GOOGLE_API_KEY, config.OPENAI_API_KEY, config.CLAUDE_API_KEY]):
        return "未設定 (Not Configured)"
    
    try:
        # TODO: 實現實際的 API 檢查邏輯
        return "正常 (Normal)"
    except Exception as e:
        return f"異常 (Error: {str(e)})"

def show_system_logs():
    """顯示系統日誌"""
    # TODO: 實現實際的日誌讀取
    sample_logs = [
        {"time": "2024-03-15 10:30:00", "level": "INFO", "message": "系統啟動"},
        {"time": "2024-03-15 10:30:05", "level": "INFO", "message": "資料庫連接成功"},
        {"time": "2024-03-15 10:35:00", "level": "WARNING", "message": "API 響應時間過長"}
    ]
    
    for log in sample_logs:
        if log["level"] == "INFO":
            st.info(f"{log['time']} - {log['message']}")
        elif log["level"] == "WARNING":
            st.warning(f"{log['time']} - {log['message']}")
        elif log["level"] == "ERROR":
            st.error(f"{log['time']} - {log['message']}")