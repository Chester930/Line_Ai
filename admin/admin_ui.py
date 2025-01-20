import streamlit as st
import sys
import os
import logging
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.header import show_header
from components.sidebar import show_sidebar
from components.footer import show_footer
from pages import (
    system_status,
    model_settings,
    line_management,
    chat_test,
    prompts_management,
    role_management,
    plugin_management,
    knowledge_base
)

# 設置 logger
logger = logging.getLogger(__name__)

# 必須在最開始設置頁面配置
st.set_page_config(
    page_title="Line AI Assistant - 管理介面",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# 隱藏預設側邊欄的 CSS
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        div[data-testid="stSidebarNav"] {display: none}
        .css-ch5dnh {display: none}  /* 隱藏 Streamlit 預設的側邊欄 */
    </style>
""", unsafe_allow_html=True)

def main():
    # 顯示頁面頭部
    show_header()
    
    # 使用原生的側邊欄
    with st.sidebar:
        st.title("Line AI Assistant")
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
                "知識庫管理 (Knowledge Base)"
            ]
        )
        selected_feature = menu.split(" (")[0]
    
    # 根據選擇顯示對應頁面
    if selected_feature == "系統狀態":
        system_status.show_page()
    elif selected_feature == "AI 模型設定":
        model_settings.show_page()
    elif selected_feature == "LINE 官方帳號管理":
        line_management.show_page()
    elif selected_feature == "對話測試":
        chat_test.show_page()
    elif selected_feature == "共用 Prompts 管理":
        prompts_management.show_page()
    elif selected_feature == "角色管理":
        role_management.show_page()
    elif selected_feature == "插件功能列表":
        plugin_management.show_page()
    elif selected_feature == "知識庫管理":
        knowledge_base.show_page()
    
    # 顯示頁面底部
    show_footer()

if __name__ == "__main__":
    main() 