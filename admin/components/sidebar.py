import streamlit as st

def show_sidebar() -> str:
    """顯示側邊欄並返回選單選項"""
    
    # 自定義側邊欄
    with st.sidebar:
        st.title("Line AI Assistant")
        
        menu = st.radio(
            "功能選單",
            options=[
                "系統狀態",
                "AI 模型設定",
                "LINE 官方帳號",
                "對話測試"
            ],
            index=0,
            key="sidebar_menu"
        )
        
        st.divider()
        st.caption("© 2024 Line AI Assistant")
        
        # 顯示維護通知
        st.info("部分功能正在維護中...")
    
    return menu 