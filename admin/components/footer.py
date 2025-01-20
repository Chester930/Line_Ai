import streamlit as st

def show_footer():
    """顯示頁面底部"""
    st.markdown("""---""")
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        © 2024 Line AI Assistant | <a href="https://github.com/yourusername/project" target="_blank">GitHub</a> | <a href="mailto:support@example.com">Support</a>
    </div>
    """, unsafe_allow_html=True)