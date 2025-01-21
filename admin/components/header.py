import streamlit as st

def show_header():
    """顯示頁面頭部"""
    
    # 使用 columns 來布局
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 標題和版本資訊
        st.markdown("""
            <div style="text-align: center;">
                <h1 style="color: #ffffff;">Line AI Assistant</h1>
                <p style="color: #9BA4B5;">管理介面 v1.0.0</p>
            </div>
        """, unsafe_allow_html=True)
    
    # 分隔線
    st.divider()