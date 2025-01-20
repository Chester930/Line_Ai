import streamlit as st
from pathlib import Path

def show_sidebar() -> str:
    """顯示側邊欄並返回選擇的功能"""
    with st.sidebar:
        # 檢查 logo 是否存在
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            st.image(str(logo_path), width=200)
        else:
            st.title("Line AI Assistant")
        
        # 使用原本的選單項目
        menu = st.selectbox(
            "選擇功能 (Select Function)",
            [
                "系統狀態 (System Status)", 
                "AI 模型設定 (AI Model Settings)", 
                "LINE 官方帳號管理 (LINE Official Account)",
                "對話測試 (Chat Test)",
                "共用 Prompts 管理 (Shared Prompts)",
                "角色管理 (Role Management)",
                "插件功能列表 (Plugin Features)",
                "文件管理 (Document Management)"  # 改回原本的文件管理
            ]
        )
        
        # 返回中文選單名稱
        return menu.split(" (")[0] 