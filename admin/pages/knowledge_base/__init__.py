import streamlit as st
from . import local_kb, cloud_kb

def show_page():
    """知識庫管理頁面"""
    st.header("知識庫管理 (Knowledge Base Management)")
    
    # 分頁
    tab1, tab2 = st.tabs([
        "本地知識庫 (Local Knowledge Base)",
        "雲端知識庫 (Cloud Knowledge Base)"
    ])
    
    # 本地知識庫
    with tab1:
        local_kb.show_local_kb()
    
    # 雲端知識庫
    with tab2:
        cloud_kb.show_cloud_kb() 