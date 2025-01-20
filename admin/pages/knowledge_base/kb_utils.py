import streamlit as st
from shared.database.document_crud import DocumentCRUD

def display_file_list():
    """顯示文件列表"""
    documents = DocumentCRUD().get_all_documents()
    if documents:
        for doc in documents:
            with st.expander(f"{doc.title} ({doc.file_type})", expanded=False):
                col1, col2, col3 = st.columns([3,2,1])
                with col1:
                    st.write(f"上傳時間：{doc.created_at}")
                    st.write(f"狀態：{doc.embedding_status}")
                with col2:
                    st.write(f"檔案大小：{doc.file_size}")
                    st.write(f"分塊數量：{len(doc.chunks)}")
                with col3:
                    if st.button("刪除", key=f"del_{doc.id}"):
                        if DocumentCRUD().delete_document(doc.id):
                            st.success("文件已刪除")
                            st.rerun()
                
                show_file_details(doc)
    else:
        st.info("目前沒有本地文件")

def show_file_details(doc):
    """顯示文件詳細資訊"""
    with st.expander("內容預覽", expanded=False):
        st.write(doc.content[:500] + "...")
        
    with st.expander("向量分塊", expanded=False):
        for i, chunk in enumerate(doc.chunks, 1):
            st.markdown(f"**分塊 {i}:**")
            st.write(chunk.content[:200] + "...")
            if st.checkbox(f"顯示向量 {i}", key=f"vec_{doc.id}_{i}"):
                st.write(f"向量維度: {len(chunk.embedding)}")