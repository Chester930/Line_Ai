import streamlit as st

def show_header():
    """顯示頁面頭部"""
    st.set_page_config(
        page_title="Line AI Assistant - 管理介面",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("Line AI Assistant 管理介面")
    
    # 顯示版本資訊
    st.markdown("""
    <div style='text-align: right; color: gray; padding-bottom: 20px;'>
        版本: 1.0.0 | 環境: Production
    </div>
    """, unsafe_allow_html=True)