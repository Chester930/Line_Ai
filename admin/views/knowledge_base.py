import streamlit as st
from shared.database.models import KnowledgeBase, Document, CloudSource
from shared.database.document_crud import DocumentCRUD
from datetime import datetime
import logging
from admin.views.knowledge_base import local_kb, cloud_kb
from admin.views.knowledge_base.kb_utils import KnowledgeBaseManager

logger = logging.getLogger(__name__)

def show_page():
    """顯示知識庫管理頁面"""
    st.header("知識庫管理 (Knowledge Base Management)")
    
    # 初始化 DocumentCRUD 和 KnowledgeBaseManager
    doc_crud = DocumentCRUD()
    kb_manager = KnowledgeBaseManager()
    
    # 創建新知識庫
    with st.expander("➕ 創建新知識庫 (Create New Knowledge Base)", expanded=False):
        with st.form("create_knowledge_base"):
            name = st.text_input(
                "知識庫名稱 (Knowledge Base Name)",
                help="例如：產品手冊、FAQ等"
            )
            description = st.text_area(
                "知識庫描述 (Description)",
                help="此知識庫的用途說明"
            )
            
            if st.form_submit_button("創建"):
                try:
                    kb = KnowledgeBase(
                        name=name,
                        description=description,
                        created_at=datetime.utcnow()
                    )
                    doc_crud.db.add(kb)
                    doc_crud.db.commit()
                    st.success("✅ 知識庫創建成功！")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ 創建失敗：{str(e)}")
    
    # 知識庫列表和管理
    st.subheader("知識庫列表 (Knowledge Base List)")
    try:
        knowledge_bases = doc_crud.db.query(KnowledgeBase).all()
        
        if not knowledge_bases:
            st.info("📚 目前沒有任何知識庫，請先創建知識庫")
        else:
            for kb in knowledge_bases:
                with st.expander(f"📚 {kb.name}", expanded=False):
                    # 知識庫基本信息
                    st.write(f"描述：{kb.description}")
                    st.write(f"創建時間：{kb.created_at.strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"文件數量：{len(kb.documents)}")
                    
                    # 使用本地知識庫模組
                    local_kb.show_local_kb_section(kb)
                    
                    # 使用雲端知識庫模組
                    cloud_kb.show_cloud_kb_section(kb)
                    
                    # 知識庫刪除按鈕
                    st.subheader("⚠️ 危險區域")
                    if st.button("刪除此知識庫", key=f"del_kb_{kb.id}"):
                        try:
                            doc_crud.db.delete(kb)
                            doc_crud.db.commit()
                            st.success("✅ 知識庫已刪除")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"❌ 刪除失敗：{str(e)}")
    except Exception as e:
        st.error(f"❌ 獲取知識庫列表失敗：{str(e)}") 