import streamlit as st
import asyncio
from datetime import datetime
from shared.database.base import get_db
from shared.utils.file_processor import FileProcessor
from shared.database.models import Document, KnowledgeBase
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

def process_uploaded_file(uploaded_file, kb, db):
    """處理上傳的文件"""
    with st.spinner("處理文件中..."):
        try:
            processor = FileProcessor()
            result = asyncio.run(processor.process_file_with_timeout(
                file=uploaded_file,
                file_type=uploaded_file.type,
                timeout=30,
                save_to_db=False
            ))
            
            if result['success']:
                doc = Document(
                    title=uploaded_file.name,
                    content=result['content'],
                    processed_content=result['processed_content'],
                    file_type=uploaded_file.type,
                    file_size=uploaded_file.size,
                    content_hash=result.get('content_hash'),
                    doc_metadata={
                        'original_filename': uploaded_file.name,
                        'mime_type': uploaded_file.type,
                        'processing_time': result.get('processing_time')
                    },
                    created_at=datetime.utcnow()
                )
                kb.documents.append(doc)
                db.add(doc)
                db.commit()
                st.success("文件上傳成功")
                st.rerun()
            else:
                st.error(f"文件處理失敗：{result.get('error', '未知錯誤')}")
        except Exception as e:
            logger.error(f"處理文件時發生錯誤: {str(e)}")
            st.error(f"處理文件時發生錯誤：{str(e)}")
            db.rollback()

def show_document_list(kb, db):
    """顯示文件列表"""
    st.subheader("文件列表")
    
    if not kb.documents:
        st.info("此知識庫暫無文件")
        return
        
    for doc in kb.documents:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"📄 {doc.title}")
                st.caption(f"上傳時間：{doc.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                st.caption(f"檔案大小：{doc.file_size/1024:.1f} KB")
                st.caption(f"檔案類型：{doc.file_type}")
            
            with col3:
                preview_key = f"preview_{doc.id}"
                if st.button("預覽", key=f"btn_{preview_key}"):
                    st.session_state[preview_key] = not st.session_state.get(preview_key, False)
                
                if st.button("刪除", key=f"del_{doc.id}"):
                    try:
                        db.delete(doc)
                        db.commit()
                        st.success("文件已刪除")
                        st.rerun()
                    except Exception as e:
                        logger.error(f"刪除文件失敗: {str(e)}")
                        st.error("刪除文件失敗")
                        db.rollback()
            
            if st.session_state.get(preview_key, False):
                with st.expander("文件內容", expanded=True):
                    st.text_area(
                        "",
                        value=doc.content[:1000] + "..." if len(doc.content) > 1000 else doc.content,
                        height=200,
                        disabled=True,
                        key=f"content_{doc.id}"
                    )
            
            st.divider()

def show_local_kb_section(kb: KnowledgeBase, db: Session):
    """顯示本地文件管理區塊"""
    try:
        with st.expander("上傳文件", expanded=True):
            uploaded_file = st.file_uploader(
                "選擇文件",
                type=['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx'],
                key=f"upload_{kb.id}",
                help="支援格式：TXT、PDF、Word、Excel"
            )
            
            if uploaded_file:
                process_uploaded_file(uploaded_file, kb, db)
        
        show_document_list(kb, db)
                        
    except Exception as e:
        logger.error(f"本地文件管理錯誤: {str(e)}")
        st.error("載入本地文件管理時發生錯誤") 