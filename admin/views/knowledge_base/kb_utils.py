import streamlit as st
from shared.database.database import engine, Base

def init_database():
    """初始化資料庫表"""
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        st.error(f"初始化資料庫失敗: {str(e)}")
        return False