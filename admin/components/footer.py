import streamlit as st

def show_footer():
    """顯示頁面底部"""
    
    # 分隔線
    st.divider()
    
    # 使用 columns 來布局
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 頁尾資訊
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <p style="color: #9BA4B5; font-size: 0.8rem;">
                    © 2024 Line AI Assistant. All rights reserved.<br>
                    <span style="color: #6C757D;">Version 1.0.0</span>
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # 系統資訊
        st.markdown("""
            <div style="text-align: center; font-size: 0.7rem; color: #6C757D;">
                System Status: Online | Database: Connected | API: Active
            </div>
        """, unsafe_allow_html=True)