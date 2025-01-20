import streamlit as st
from shared.database.document_crud import DocumentCRUD
from shared.utils.file_processor import FileProcessor
import os
from datetime import datetime

def show_page():
    """知識庫管理頁面"""
    st.header("知識庫管理")
    
    # 初始化必要的類別
    doc_crud = DocumentCRUD()
    file_processor = FileProcessor()
    
    # 上傳文件區域
    with st.expander("上傳文件", expanded=True):
        show_upload_section(doc_crud, file_processor)
    
    # 文件列表
    st.subheader("文件列表")
    show_documents_list(doc_crud)
    
    # 知識庫統計
    with st.expander("知識庫統計", expanded=True):
        show_kb_stats(doc_crud)

def show_upload_section(doc_crud: DocumentCRUD, file_processor: FileProcessor):
    """顯示文件上傳區域"""
    uploaded_file = st.file_uploader(
        "選擇文件",
        type=['txt', 'pdf', 'docx', 'md'],
        help="支援的格式：TXT、PDF、Word、Markdown"
    )
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "文件標題",
                value=os.path.splitext(uploaded_file.name)[0]
            )
        
        with col2:
            file_type = uploaded_file.type
            st.text_input("文件類型", value=file_type, disabled=True)
        
        if st.button("上傳"):
            try:
                # 處理文件
                result = file_processor.process_file(uploaded_file)
                if result['success']:
                    # 保存到資料庫
                    doc = doc_crud.create_document(
                        title=title,
                        content=result['content'],
                        file_path=uploaded_file.name,
                        file_type=file_type
                    )
                    
                    if doc:
                        st.success("✅ 文件上傳成功！")
                        st.rerun()
                    else:
                        st.error("❌ 保存文件失敗")
                else:
                    st.error(f"❌ 處理文件失敗：{result.get('error', '未知錯誤')}")
                    
            except Exception as e:
                st.error(f"❌ 上傳失敗：{str(e)}")

def show_documents_list(doc_crud: DocumentCRUD):
    """顯示文件列表"""
    # 獲取所有文件
    documents = doc_crud.get_all_documents()
    
    if not documents:
        st.info("目前沒有任何文件")
        return
    
    # 顯示文件列表
    for doc in documents:
        with st.expander(f"{doc.title} ({doc.file_type})", expanded=False):
            col1, col2 = st.columns([3,1])
            
            with col1:
                st.text_area(
                    "內容預覽",
                    value=doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
                    height=150,
                    disabled=True,
                    key=f"preview_{doc.id}"
                )
                st.write(f"上傳時間：{doc.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"更新時間：{doc.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"Embedding 狀態：{doc.embedding_status}")
            
            with col2:
                if st.button("刪除", key=f"del_{doc.id}"):
                    if doc_crud.delete_document(doc.id):
                        st.success("✅ 文件已刪除")
                        st.rerun()
                    else:
                        st.error("❌ 刪除失敗")
                
                if doc.embedding_status != "completed":
                    if st.button("重新處理", key=f"reprocess_{doc.id}"):
                        # TODO: 實現重新處理邏輯
                        st.info("重新處理功能開發中...")

def show_kb_stats(doc_crud: DocumentCRUD):
    """顯示知識庫統計信息"""
    col1, col2, col3 = st.columns(3)
    
    # 獲取統計數據
    total_docs = doc_crud.count_documents()
    processed_docs = doc_crud.count_documents(embedding_status="completed")
    total_chunks = doc_crud.count_chunks()
    
    with col1:
        st.metric("總文件數", total_docs)
    
    with col2:
        st.metric("已處理文件數", processed_docs)
        
    with col3:
        st.metric("總片段數", total_chunks) 