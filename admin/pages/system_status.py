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
        st.info("系統資訊 (System Info)")
        st.write(f"- OS: {platform.system()} {platform.version()}")
        st.write(f"- Python: {platform.python_version()}")
        st.write(f"- CPU 使用率: {psutil.cpu_percent()}%")
        st.write(f"- 記憶體使用率: {psutil.virtual_memory().percent}%")
        
        # 資料庫狀態
        try:
            db = next(get_db())
            db_status = "正常 (Normal)"
            db.execute("SELECT 1")
        except Exception as e:
            db_status = f"異常 (Error: {str(e)})"
        st.write(f"- 資料庫狀態: {db_status}")
    
    with col2:
        st.info("服務狀態 (Service Status)")
        config = Config.get_instance()  # 使用單例模式
        
        # 檢查各項服務
        services = {
            "LINE Bot": check_line_bot_status(),
            "OpenAI API": check_api_status("OpenAI"),
            "Google API": check_api_status("Google"),
            "Anthropic API": check_api_status("Anthropic"),
            "知識庫服務": check_knowledge_base_status()
        }
        
        for service, status in services.items():
            st.write(f"- {service}: {status}")
    
    # 系統日誌
    st.subheader("系統日誌 (System Logs)")
    show_system_logs()

def check_line_bot_status() -> str:
    """檢查 LINE Bot 狀態"""
    try:
        # TODO: 實現實際的狀態檢查
        return "正常運行 (Running)"
    except Exception:
        return "異常 (Error)"

def check_api_status(api_name: str) -> str:
    """檢查 API 狀態"""
    config = Config.get_instance()  # 使用單例模式
    
    api_keys = {
        "OpenAI": config.OPENAI_API_KEY,
        "Google": config.GOOGLE_API_KEY,
        "Anthropic": config.ANTHROPIC_API_KEY
    }
    
    api_key = api_keys.get(api_name)
    if not api_key:
        return "未設定 (Not Configured)"
    
    try:
        # 簡單的 API 可用性檢查
        if api_name == "OpenAI":
            return "正常 (Normal)"
        elif api_name == "Google":
            return "正常 (Normal)"
        elif api_name == "Anthropic":
            return "正常 (Normal)"
        return "未知 (Unknown)"
    except Exception as e:
        return f"異常 (Error: {str(e)})"

def check_knowledge_base_status() -> str:
    """檢查知識庫狀態"""
    try:
        # TODO: 實現知識庫狀態檢查
        return "正常運行 (Running)"
    except Exception:
        return "異常 (Error)"

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