import streamlit as st

def show_header():
    """顯示頁面頭部"""
    
    # 使用列來創建頭部佈局
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("Line AI Assistant 管理介面")
        st.markdown("---")
    
    with col2:
        # 顯示當前時間或其他狀態資訊
        st.write("")  # 空行用於對齊
        st.caption("管理員模式")