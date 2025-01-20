import streamlit as st
from shared.database.document_crud import DocumentCRUD
from shared.utils.file_processor import FileProcessor
import os
from datetime import datetime

def show_local_kb():
    """顯示本地知識庫頁面"""
    # 初始化必要的類別
    doc_crud = DocumentCRUD()
    file_processor = FileProcessor()
    
    # 獲取當前用戶ID (暫時使用測試ID)
    current_user_id = 1  # TODO: 從session獲取實際用戶ID
    
    # 知識庫選擇或創建
    st.subheader("選擇知識庫")
    show_knowledge_base_selector(doc_crud, current_user_id)
    
    # 獲取當前選中的知識庫
    current_kb = get_current_knowledge_base(doc_crud, current_user_id)
    if not current_kb:
        st.warning("請先創建或選擇一個知識庫")
        return
        
    # 顯示當前知識庫信息
    st.subheader(f"當前知識庫：{current_kb.name}")
    if current_kb.description:
        st.write(current_kb.description)
    
    # 資料夾管理
    with st.expander("資料夾管理", expanded=True):
        show_folder_management(doc_crud, current_kb.id)
    
    # 上傳文件區域
    with st.expander("上傳文件", expanded=True):
        show_upload_section(doc_crud, file_processor, current_kb.id)
    
    # 文件列表
    st.subheader("文件列表")
    show_documents_list(doc_crud, current_kb.id)
    
    # 知識庫統計
    with st.expander("知識庫統計", expanded=True):
        show_kb_stats(doc_crud, current_kb.id)

def show_knowledge_base_selector(doc_crud, user_id):
    """顯示知識庫選擇器"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 獲取用戶的所有知識庫
        knowledge_bases = doc_crud.get_user_knowledge_bases(user_id)
        kb_names = ["選擇知識庫..."] + [kb.name for kb in knowledge_bases]
        
        # 當前選中的知識庫
        current_kb_name = st.session_state.get("current_kb_name", "選擇知識庫...")
        selected_kb = st.selectbox(
            "選擇知識庫",
            kb_names,
            index=kb_names.index(current_kb_name)
        )
        
        if selected_kb != "選擇知識庫...":
            st.session_state.current_kb_name = selected_kb
    
    with col2:
        if st.button("新增知識庫"):
            st.session_state.show_new_kb_form = True
    
    # 顯示新增知識庫表單
    if st.session_state.get("show_new_kb_form", False):
        with st.form("new_kb_form"):
            name = st.text_input("知識庫名稱")
            description = st.text_area("描述")
            is_default = st.checkbox("設為預設知識庫")
            
            if st.form_submit_button("創建"):
                if name:
                    try:
                        kb = doc_crud.create_knowledge_base(
                            user_id=user_id,
                            name=name,
                            description=description,
                            is_default=is_default
                        )
                        if kb:
                            st.success("✅ 知識庫創建成功！")
                            st.session_state.current_kb_name = name
                            st.session_state.show_new_kb_form = False
                            st.rerun()
                        else:
                            st.error("❌ 創建失敗")
                    except Exception as e:
                        st.error(f"❌ 創建失敗：{str(e)}")
                else:
                    st.error("請輸入知識庫名稱")

def get_current_knowledge_base(doc_crud, user_id):
    """獲取當前選中的知識庫"""
    current_kb_name = st.session_state.get("current_kb_name")
    if not current_kb_name or current_kb_name == "選擇知識庫...":
        # 嘗試獲取預設知識庫
        knowledge_bases = doc_crud.get_user_knowledge_bases(user_id)
        default_kb = next((kb for kb in knowledge_bases if kb.is_default), None)
        if default_kb:
            st.session_state.current_kb_name = default_kb.name
            return default_kb
        return None
    
    # 獲取指定名稱的知識庫
    knowledge_bases = doc_crud.get_user_knowledge_bases(user_id)
    return next((kb for kb in knowledge_bases if kb.name == current_kb_name), None)

def show_folder_management(doc_crud, kb_id):
    """顯示資料夾管理"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 獲取所有資料夾
        folders = doc_crud.get_knowledge_base_folders(kb_id)
        
        # 建立資料夾樹狀結構
        root_folders = [f for f in folders if f.parent_id is None]
        if root_folders:
            for folder in root_folders:
                show_folder_tree(doc_crud, folder, folders)
        else:
            st.info("尚未創建任何資料夾")
    
    with col2:
        if st.button("新增資料夾"):
            st.session_state.show_new_folder_form = True
    
    # 顯示新增資料夾表單
    if st.session_state.get("show_new_folder_form", False):
        with st.form("new_folder_form"):
            name = st.text_input("資料夾名稱")
            parent_id = None
            if folders:  # 如果有現有資料夾，允許選擇父資料夾
                parent_options = ["無"] + [f"{f.path}" for f in folders]
                parent_choice = st.selectbox("父資料夾", parent_options)
                if parent_choice != "無":
                    parent_id = next(f.id for f in folders if f.path == parent_choice)
            
            if st.form_submit_button("創建"):
                if name:
                    try:
                        folder = doc_crud.create_folder(
                            knowledge_base_id=kb_id,
                            name=name,
                            parent_id=parent_id
                        )
                        if folder:
                            st.success("✅ 資料夾創建成功！")
                            st.session_state.show_new_folder_form = False
                            st.rerun()
                        else:
                            st.error("❌ 創建失敗")
                    except Exception as e:
                        st.error(f"❌ 創建失敗：{str(e)}")
                else:
                    st.error("請輸入資料夾名稱")

def show_folder_tree(doc_crud, folder, all_folders, level=0):
    """遞迴顯示資料夾樹狀結構"""
    prefix = "  " * level + ("📁 " if level > 0 else "")
    expander = st.expander(f"{prefix}{folder.name}", expanded=False)
    
    with expander:
        # 顯示資料夾中的文件
        documents = doc_crud.get_knowledge_base_documents(
            kb_id=folder.knowledge_base_id,
            folder_id=folder.id
        )
        if documents:
            for doc in documents:
                st.write(f"📄 {doc.title}")
        else:
            st.info("資料夾為空")
        
        # 顯示刪除按鈕
        if st.button("刪除資料夾", key=f"del_folder_{folder.id}"):
            if doc_crud.delete_folder(folder.id):
                st.success("✅ 資料夾已刪除")
                st.rerun()
            else:
                st.error("❌ 刪除失敗")
    
    # 遞迴顯示子資料夾
    subfolders = [f for f in all_folders if f.parent_id == folder.id]
    for subfolder in subfolders:
        show_folder_tree(doc_crud, subfolder, all_folders, level + 1)

def show_upload_section(doc_crud, file_processor, kb_id):
    """顯示文件上傳區域"""
    uploaded_file = st.file_uploader(
        "選擇文件",
        type=['txt', 'pdf', 'docx', 'md'],
        help="支援的格式：TXT、PDF、Word、Markdown"
    )
    
    if uploaded_file:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            title = st.text_input(
                "文件標題",
                value=os.path.splitext(uploaded_file.name)[0]
            )
        
        with col2:
            file_type = uploaded_file.type
            st.text_input("文件類型", value=file_type, disabled=True)
        
        with col3:
            # 選擇上傳到哪個資料夾
            folders = doc_crud.get_knowledge_base_folders(kb_id)
            folder_options = ["根目錄"] + [f.path for f in folders]
            selected_folder = st.selectbox("選擇資料夾", folder_options)
            folder_id = None
            if selected_folder != "根目錄":
                folder_id = next(f.id for f in folders if f.path == selected_folder)
        
        if st.button("上傳"):
            try:
                result = file_processor.process_file(uploaded_file)
                if result['success']:
                    doc = doc_crud.create_document(
                        knowledge_base_id=kb_id,
                        folder_id=folder_id,
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

def show_documents_list(doc_crud, kb_id):
    """顯示文件列表"""
    # 獲取知識庫中的所有文件
    documents = doc_crud.get_knowledge_base_documents(kb_id)
    
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
                if doc.folder:
                    st.write(f"所在資料夾：{doc.folder.path}")
            
            with col2:
                if st.button("刪除", key=f"del_{doc.id}"):
                    if doc_crud.delete_document(doc.id):
                        st.success("✅ 文件已刪除")
                        st.rerun()
                    else:
                        st.error("❌ 刪除失敗")

def show_kb_stats(doc_crud, kb_id):
    """顯示知識庫統計"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("文件總數", doc_crud.count_documents(kb_id=kb_id))
    
    with col2:
        st.metric(
            "已處理文件數", 
            doc_crud.count_documents(kb_id=kb_id, embedding_status="completed")
        )
    
    with col3:
        st.metric("文本片段數", doc_crud.count_chunks(kb_id=kb_id)) 