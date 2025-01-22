import streamlit as st
from shared.config.config import Config
from shared.ai.cag import CAGSystem
from shared.ai.rag.retriever import KnowledgeRetriever
from shared.database.models import KnowledgeBase, Document
import pytest
import sys
import io
from shared.database.base import SessionLocal
import logging
from admin.views.knowledge_base.local_kb import show_local_kb_section

# 必須是第一個 Streamlit 命令
st.set_page_config(
    page_title="AI 助手管理介面",
    page_icon="🤖",
    layout="wide"
)

logger = logging.getLogger(__name__)

class TestView:
    def __init__(self):
        self.config = Config()
        self.cag_system = CAGSystem(self.config)
        self.knowledge_retriever = KnowledgeRetriever(self.config)
        
    def render(self):
        st.title("系統測試介面")
        
        # 測試類別選擇
        test_type = st.selectbox(
            "選擇測試類別",
            ["基礎設施測試", "知識庫測試", "文檔管理測試", "搜索功能測試", "對話功能測試"]
        )
        
        # 執行測試按鈕
        if st.button("執行測試"):
            self._run_tests(test_type)
    
    def _run_tests(self, test_type):
        st.write(f"執行 {test_type} 中...")
        
        # 捕獲測試輸出
        output = io.StringIO()
        sys.stdout = output
        
        try:
            if test_type == "基礎設施測試":
                pytest.main(["-v", "tests/test_infrastructure.py"])
            elif test_type == "知識庫測試":
                pytest.main(["-v", "tests/test_knowledge_base.py"])
            elif test_type == "文檔管理測試":
                pytest.main(["-v", "tests/test_document_management.py"])
            elif test_type == "搜索功能測試":
                pytest.main(["-v", "tests/test_search.py"])
            elif test_type == "對話功能測試":
                pytest.main(["-v", "tests/test_chat.py"])
            
            # 顯示測試結果
            test_output = output.getvalue()
            st.code(test_output)
            
            # 解析測試結果
            self._display_test_results(test_output)
            
        except Exception as e:
            st.error(f"執行測試時發生錯誤：{str(e)}")
        finally:
            sys.stdout = sys.__stdout__
    
    def _display_test_results(self, test_output):
        """解析並顯示測試結果"""
        # 計算測試統計
        passed = test_output.count("PASSED")
        failed = test_output.count("FAILED")
        errors = test_output.count("ERROR")
        
        # 顯示統計
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("通過", passed, delta=None, delta_color="normal")
        with col2:
            st.metric("失敗", failed, delta=None, delta_color="inverse")
        with col3:
            st.metric("錯誤", errors, delta=None, delta_color="inverse")

def main():
    # 側邊欄導航
    with st.sidebar:
        st.title("管理選項")
        page = st.radio(
            "選擇功能",
            ["知識庫管理", "角色管理", "對話記錄", "系統設定"]
        )
    
    # 主要內容區域
    db = SessionLocal()
    try:
        if page == "知識庫管理":
            show_knowledge_base_management(db)
        elif page == "角色管理":
            st.title("角色管理")
            st.info("角色管理功能開發中...")
        elif page == "對話記錄":
            st.title("對話記錄")
            st.info("對話記錄功能開發中...")
        elif page == "系統設定":
            st.title("系統設定")
            st.info("系統設定功能開發中...")
    finally:
        db.close()

def show_knowledge_base_management(db):
    st.title("知識庫管理")
    
    # 創建知識庫表單
    with st.form("create_kb_form"):
        kb_name = st.text_input("知識庫名稱")
        kb_desc = st.text_area("知識庫描述")
        submitted = st.form_submit_button("創建知識庫")
        
        if submitted and kb_name:
            try:
                kb = KnowledgeBase(name=kb_name, description=kb_desc)
                db.add(kb)
                db.commit()
                st.success("知識庫創建成功！")
                st.rerun()
            except Exception as e:
                logger.error(f"創建知識庫失敗: {str(e)}")
                st.error("創建知識庫失敗")
                db.rollback()
    
    # 顯示現有知識庫列表
    kbs = db.query(KnowledgeBase).all()
    if kbs:
        for kb in kbs:
            with st.expander(f"📚 {kb.name}", expanded=True):
                st.write(f"描述：{kb.description or '無'}")
                show_local_kb_section(kb, db)
    else:
        st.info("目前沒有知識庫，請先創建一個知識庫。")

if __name__ == "__main__":
    main() 