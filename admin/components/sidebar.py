import streamlit as st

def show_sidebar() -> str:
    """顯示側邊欄並返回選單選項"""
    
    # 自定義側邊欄
    with st.sidebar:
        st.title("Line AI Assistant")
        
        menu = st.radio(
            "功能選單",
            options=[
                "系統狀態 (System Status)",
                "AI 模型設定 (Model Settings)",
                "LINE 官方帳號 (LINE Account)",
                "對話測試 (Chat Test)",
                "共用 Prompts (Shared Prompts)",
                "角色管理 (Role Management)",
                "插件功能 (Plugins)",
                "知識庫管理 (Knowledge Base)"
            ],
            index=0,
            key="sidebar_menu"
        )
        
        st.divider()
        st.caption("© 2024 Line AI Assistant")
        
        # 顯示維護通知
        st.info("部分功能正在維護中...")
    
    # 移除中文標題，只返回英文部分用於路由
    return menu.split(" (")[0] 