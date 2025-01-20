import streamlit as st
from shared.database.document_crud import DocumentCRUD
from shared.utils.vector_store import VectorStore
from typing import List, Dict, Optional

def show_search_kb():
    """顯示知識庫搜索頁面"""
    # 初始化必要的類別
    doc_crud = DocumentCRUD()
    vector_store = VectorStore()
    
    # 獲取當前用戶ID (暫時使用測試ID)
    current_user_id = 1  # TODO: 從session獲取實際用戶ID
    
    # 獲取用戶的所有知識庫
    knowledge_bases = doc_crud.get_user_knowledge_bases(current_user_id)
    if not knowledge_bases:
        st.warning("尚未創建任何知識庫")
        return
    
    # 搜索區域
    with st.form("search_form"):
        # 搜索框
        query = st.text_input(
            "搜索內容",
            placeholder="請輸入要搜索的內容..."
        )
        
        # 過濾選項
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 選擇知識庫
            selected_kb_ids = []
            st.write("選擇知識庫：")
            for kb in knowledge_bases:
                if st.checkbox(kb.name, True):
                    selected_kb_ids.append(kb.id)
        
        with col2:
            # 選擇資料夾
            selected_folder_ids = []
            if selected_kb_ids:
                st.write("選擇資料夾：")
                for kb_id in selected_kb_ids:
                    folders = doc_crud.get_knowledge_base_folders(kb_id)
                    if folders:
                        st.write(f"**{next(kb.name for kb in knowledge_bases if kb.id == kb_id)}**")
                        for folder in folders:
                            if st.checkbox(folder.name, True, key=f"folder_{folder.id}"):
                                selected_folder_ids.append(folder.id)
        
        with col3:
            # 搜索選項
            st.write("搜索選項：")
            top_k = st.number_input("返回結果數", min_value=1, value=5)
            threshold = st.slider("相似度閾值", 0.0, 1.0, 0.5)
            
        # 搜索按鈕
        search_clicked = st.form_submit_button("搜索")
    
    # 執行搜索
    if search_clicked and query:
        with st.spinner("搜索中..."):
            try:
                # 構建過濾條件
                filters = {
                    "knowledge_base_ids": selected_kb_ids,
                    "folder_ids": selected_folder_ids if selected_folder_ids else None
                }
                
                # 執行向量搜索
                results = vector_store.search(
                    query=query,
                    filters=filters,
                    top_k=top_k,
                    threshold=threshold
                )
                
                # 顯示結果
                show_search_results(doc_crud, results)
            except Exception as e:
                st.error(f"❌ 搜索失敗：{str(e)}")

def show_search_results(doc_crud: DocumentCRUD, results: List[Dict]):
    """顯示搜索結果"""
    if not results:
        st.info("未找到相關內容")
        return
    
    st.subheader("搜索結果")
    
    for i, result in enumerate(results, 1):
        # 獲取文件信息
        doc = doc_crud.get_document(result['document_id'])
        if not doc:
            continue
            
        with st.expander(
            f"{i}. {doc.title} ({result['similarity']:.2%}相似度)",
            expanded=True
        ):
            # 顯示文件信息
            st.markdown("**文件信息：**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"知識庫：{doc.knowledge_base.name}")
                if doc.folder:
                    st.write(f"資料夾：{doc.folder.path}")
                st.write(f"文件類型：{doc.file_type}")
            
            with col2:
                st.write(f"創建時間：{doc.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"更新時間：{doc.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 顯示匹配內容
            st.markdown("**匹配內容：**")
            st.markdown(f"```\n{result['content']}\n```")
            
            # 顯示上下文
            if st.button("顯示更多上下文", key=f"context_{doc.id}"):
                context = get_content_context(doc.content, result['content'])
                st.markdown("**上下文：**")
                st.markdown(f"```\n{context}\n```") 