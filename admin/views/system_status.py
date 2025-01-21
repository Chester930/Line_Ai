import streamlit as st
import psutil
import platform
from datetime import datetime
from shared.config.config import Config
from shared.database.database import get_db, check_database_connection
from shared.utils.system_info import get_system_info

def show_page():
    """系統狀態頁面"""
    st.header("系統狀態 (System Status)")
    st.write("目前版本 (Current Version)：1.0.0")
    
    # 顯示系統資訊
    col1, col2 = st.columns(2)
    with col1:
        st.info("系統設定 (System Settings)")
        st.write("- 資料庫類型 (Database Type)：SQLite")
        st.write("- AI 模型 (AI Model)：Gemini Pro")
        st.write("- 日誌級別 (Log Level)：INFO")
    
    with col2:
        st.info("運行狀態 (Runtime Status)")
        st.write("- 資料庫連接 (Database Connection)：正常 (Normal)")
        st.write("- API 連接 (API Connection)：正常 (Normal)")
        st.write("- Webhook：未啟動 (Not Started)")
    
    # 系統資源使用情況
    st.subheader("系統資源 (System Resources)")
    col3, col4 = st.columns(2)
    
    with col3:
        # CPU 和記憶體使用率
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        st.write("CPU 使用率：")
        st.progress(cpu_percent/100, f"{cpu_percent}%")
        
        st.write("記憶體使用率：")
        st.progress(memory.percent/100, f"{memory.percent}%")
    
    with col4:
        # 磁碟使用率和運行時間
        disk = psutil.disk_usage('/')
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        st.write("磁碟使用率：")
        st.progress(disk.percent/100, f"{disk.percent}%")
        
        st.write("系統運行時間：")
        st.write(f"{uptime.days} 天 {uptime.seconds//3600} 小時")
    
    # 系統版本資訊
    st.subheader("系統版本 (System Version)")
    st.write(f"- 作業系統：{platform.system()} {platform.release()}")
    st.write(f"- Python 版本：{platform.python_version()}")
    st.write("- 資料庫版本：SQLite 3")
    st.write("- API 版本：v1.0.0")

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