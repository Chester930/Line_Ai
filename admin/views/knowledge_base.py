import streamlit as st
from admin.components.knowledge_base import show_local_knowledge_base

def show_page():
    """顯示知識庫管理頁面"""
    st.header("知識庫管理 (Knowledge Base)")
    
    # 使用 tabs 分離本地和雲端知識庫
    local_tab, cloud_tab = st.tabs(["本地知識庫", "雲端知識庫"])
    
    with local_tab:
        show_local_knowledge_base()
    
    with cloud_tab:
        st.info("雲端知識庫功能開發中...") 