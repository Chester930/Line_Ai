import streamlit as st
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from shared.database.models import KnowledgeBase, Document
from shared.database.base import get_db
import logging

logger = logging.getLogger(__name__)

def init_session_state():
    """初始化 session state"""
    if 'kb_name' not in st.session_state:
        st.session_state.kb_name = ""
    if 'kb_description' not in st.session_state:
        st.session_state.kb_description = ""
    if 'current_kb' not in st.session_state:
        st.session_state.current_kb = None
    if 'show_create_form' not in st.session_state:
        st.session_state.show_create_form = False

def reset_form():
    """重置表單數據"""
    st.session_state.kb_name = ""
    st.session_state.kb_description = ""
    st.session_state.show_create_form = False

def show_page():
    """顯示知識庫管理頁面"""
    st.title("知識庫管理")
    
    # 初始化 session state
    init_session_state()
    
    # 使用資料庫會話
    try:
        db = next(get_db())
        
        # 創建新知識庫按鈕
        if not st.session_state.show_create_form:
            if st.button("➕ 創建新知識庫"):
                st.session_state.show_create_form = True
                st.rerun()
        
        # 創建新知識庫的表單
        if st.session_state.show_create_form:
            with st.form("create_kb_form"):
                st.subheader("創建新知識庫")
                kb_name = st.text_input("知識庫名稱", value=st.session_state.kb_name)
                kb_description = st.text_area("描述", value=st.session_state.kb_description)
                col1, col2 = st.columns([1, 4])
                with col1:
                    submitted = st.form_submit_button("創建")
                with col2:
                    if st.form_submit_button("取消"):
                        reset_form()
                        st.rerun()
                
                if submitted:
                    if not kb_name:
                        st.error("請輸入知識庫名稱")
                    else:
                        # 檢查知識庫名稱是否已存在
                        existing_kb = db.query(KnowledgeBase).filter(
                            KnowledgeBase.name == kb_name
                        ).first()
                        
                        if existing_kb:
                            st.error(f"知識庫名稱 '{kb_name}' 已存在")
                        else:
                            try:
                                new_kb = KnowledgeBase(
                                    name=kb_name,
                                    description=kb_description,
                                    created_at=datetime.utcnow()
                                )
                                db.add(new_kb)
                                db.commit()
                                st.success(f"成功創建知識庫：{kb_name}")
                                
                                # 重置表單
                                reset_form()
                                st.rerun()
                            except Exception as e:
                                logger.error(f"創建知識庫失敗: {str(e)}")
                                st.error("創建知識庫失敗，請檢查日誌")
                                db.rollback()
            
            st.markdown("---")
        
        # 顯示現有知識庫列表
        st.subheader("知識庫列表")
        knowledge_bases = db.query(KnowledgeBase).order_by(KnowledgeBase.created_at.desc()).all()
        
        if not knowledge_bases:
            st.info("目前沒有知識庫，請先創建一個新的知識庫")
            return
            
        # 為每個知識庫創建一個區域
        for kb in knowledge_bases:
            with st.expander(f"📚 {kb.name}", expanded=st.session_state.current_kb == kb.id):
                st.write(f"描述：{kb.description or '無'}")
                st.write(f"創建時間：{kb.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 刪除知識庫按鈕
                if st.button(f"刪除知識庫", key=f"del_kb_{kb.id}"):
                    try:
                        db.delete(kb)
                        db.commit()
                        st.success("知識庫已刪除")
                        # 重置當前選中的知識庫
                        st.session_state.current_kb = None
                        st.rerun()
                    except Exception as e:
                        logger.error(f"刪除知識庫失敗: {str(e)}")
                        st.error("刪除知識庫失敗，請檢查日誌")
                        db.rollback()
                
                st.markdown("---")
                
                # 記錄當前展開的知識庫
                st.session_state.current_kb = kb.id
                
                # 顯示本地文件管理區域
                from .local_kb import show_local_kb_section
                show_local_kb_section(kb, db)
                
                st.markdown("---")
                
                # 顯示雲端來源管理區域
                from .cloud_kb import show_cloud_kb_section
                show_cloud_kb_section(kb, db)
                
    except Exception as e:
        logger.error(f"知識庫管理頁面錯誤: {str(e)}")
        st.error("載入知識庫管理頁面時發生錯誤，請檢查日誌") 