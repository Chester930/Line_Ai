import streamlit as st
import json
import zipfile
import io
import os
from datetime import datetime
from shared.database.document_crud import DocumentCRUD
from shared.utils.file_processor import FileProcessor

def show_import_export_kb():
    """顯示知識庫導入/導出頁面"""
    # 初始化必要的類別
    doc_crud = DocumentCRUD()
    file_processor = FileProcessor()
    
    # 獲取當前用戶ID (暫時使用測試ID)
    current_user_id = 1  # TODO: 從session獲取實際用戶ID
    
    # 使用標籤頁組織不同功能
    tab1, tab2 = st.tabs(["批量導入", "導出/遷移"])
    
    with tab1:
        show_batch_import(doc_crud, file_processor, current_user_id)
    
    with tab2:
        show_export_migrate(doc_crud, current_user_id)

def show_batch_import(doc_crud, file_processor, user_id):
    """顯示批量導入功能"""
    st.subheader("批量導入")
    
    # 選擇目標知識庫
    knowledge_bases = doc_crud.get_user_knowledge_bases(user_id)
    if not knowledge_bases:
        st.warning("請先創建知識庫")
        return
    
    selected_kb = st.selectbox(
        "選擇目標知識庫",
        options=knowledge_bases,
        format_func=lambda x: x.name
    )
    
    if not selected_kb:
        return
    
    # 選擇目標資料夾
    folders = doc_crud.get_knowledge_base_folders(selected_kb.id)
    folder_options = ["根目錄"] + [f.path for f in folders]
    selected_folder = st.selectbox("選擇目標資料夾", folder_options)
    folder_id = None
    if selected_folder != "根目錄":
        folder_id = next(f.id for f in folders if f.path == selected_folder)
    
    # 上傳文件
    uploaded_files = st.file_uploader(
        "選擇要導入的文件",
        type=['txt', 'pdf', 'docx', 'md'],
        accept_multiple_files=True,
        help="支援的格式：TXT、PDF、Word、Markdown"
    )
    
    if uploaded_files:
        st.write(f"已選擇 {len(uploaded_files)} 個文件")
        
        # 顯示導入進度
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 開始導入
        if st.button("開始導入"):
            total_files = len(uploaded_files)
            success_count = 0
            failed_files = []
            
            for i, file in enumerate(uploaded_files, 1):
                try:
                    # 處理文件
                    status_text.write(f"正在處理：{file.name}")
                    result = file_processor.process_file(file)
                    
                    if result['success']:
                        # 保存到數據庫
                        doc = doc_crud.create_document(
                            knowledge_base_id=selected_kb.id,
                            folder_id=folder_id,
                            title=os.path.splitext(file.name)[0],
                            content=result['content'],
                            file_path=file.name,
                            file_type=file.type
                        )
                        
                        if doc:
                            success_count += 1
                        else:
                            failed_files.append((file.name, "保存失敗"))
                    else:
                        failed_files.append((file.name, result.get('error', '處理失敗')))
                
                except Exception as e:
                    failed_files.append((file.name, str(e)))
                
                # 更新進度
                progress = int((i / total_files) * 100)
                progress_bar.progress(progress)
            
            # 顯示結果
            status_text.write(f"導入完成！成功：{success_count}，失敗：{len(failed_files)}")
            
            if failed_files:
                st.error("以下文件導入失敗：")
                for name, error in failed_files:
                    st.write(f"- {name}: {error}")

def show_export_migrate(doc_crud, user_id):
    """顯示導出/遷移功能"""
    st.subheader("導出/遷移")
    
    # 選擇要導出的知識庫
    knowledge_bases = doc_crud.get_user_knowledge_bases(user_id)
    if not knowledge_bases:
        st.warning("尚無可導出的知識庫")
        return
    
    selected_kb = st.selectbox(
        "選擇要導出的知識庫",
        options=knowledge_bases,
        format_func=lambda x: x.name,
        key="export_kb"
    )
    
    if not selected_kb:
        return
    
    # 導出選項
    export_options = st.multiselect(
        "選擇要導出的內容",
        ["文件內容", "資料夾結構", "權限設置", "分享記錄"],
        default=["文件內容", "資料夾結構"]
    )
    
    if st.button("導出"):
        try:
            # 創建 ZIP 文件
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 導出基本信息
                kb_info = {
                    'id': selected_kb.id,
                    'name': selected_kb.name,
                    'description': selected_kb.description,
                    'is_public': selected_kb.is_public,
                    'created_at': selected_kb.created_at.isoformat(),
                    'updated_at': selected_kb.updated_at.isoformat()
                }
                zf.writestr('knowledge_base.json', json.dumps(kb_info, ensure_ascii=False, indent=2))
                
                # 導出資料夾結構
                if "資料夾結構" in export_options:
                    folders = doc_crud.get_knowledge_base_folders(selected_kb.id)
                    folders_data = [{
                        'id': f.id,
                        'name': f.name,
                        'path': f.path,
                        'parent_id': f.parent_id
                    } for f in folders]
                    zf.writestr('folders.json', json.dumps(folders_data, ensure_ascii=False, indent=2))
                
                # 導出文件內容
                if "文件內容" in export_options:
                    documents = doc_crud.get_knowledge_base_documents(selected_kb.id)
                    for doc in documents:
                        doc_data = {
                            'id': doc.id,
                            'title': doc.title,
                            'content': doc.content,
                            'file_type': doc.file_type,
                            'folder_id': doc.folder_id,
                            'created_at': doc.created_at.isoformat(),
                            'updated_at': doc.updated_at.isoformat()
                        }
                        zf.writestr(
                            f'documents/{doc.id}.json',
                            json.dumps(doc_data, ensure_ascii=False, indent=2)
                        )
                
                # 導出權限設置
                if "權限設置" in export_options:
                    permissions = doc_crud.get_kb_permissions(selected_kb.id)
                    perm_data = [{
                        'user_id': p.user_id,
                        'permission_type': p.permission_type.value
                    } for p in permissions]
                    zf.writestr('permissions.json', json.dumps(perm_data, ensure_ascii=False, indent=2))
                
                # 導出分享記錄
                if "分享記錄" in export_options:
                    shares = doc_crud.get_kb_shares(selected_kb.id)
                    share_data = [{
                        'share_code': s.share_code,
                        'permission_type': s.permission_type.value,
                        'expires_at': s.expires_at.isoformat() if s.expires_at else None,
                        'created_at': s.created_at.isoformat()
                    } for s in shares]
                    zf.writestr('shares.json', json.dumps(share_data, ensure_ascii=False, indent=2))
            
            # 提供下載
            zip_buffer.seek(0)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"knowledge_base_{selected_kb.id}_{timestamp}.zip"
            
            st.download_button(
                "下載導出文件",
                zip_buffer.getvalue(),
                filename,
                mime="application/zip"
            )
            
        except Exception as e:
            st.error(f"導出失敗：{str(e)}")

def import_from_zip(doc_crud, zip_file, user_id):
    """從 ZIP 文件導入知識庫"""
    try:
        with zipfile.ZipFile(zip_file, 'r') as zf:
            # 讀取知識庫信息
            kb_info = json.loads(zf.read('knowledge_base.json'))
            
            # 創建新知識庫
            kb = doc_crud.create_knowledge_base(
                user_id=user_id,
                name=f"{kb_info['name']} (導入)",
                description=kb_info['description']
            )
            
            if not kb:
                raise Exception("創建知識庫失敗")
            
            # 導入資料夾結構
            if 'folders.json' in zf.namelist():
                folders_data = json.loads(zf.read('folders.json'))
                folder_id_map = {}  # 舊ID到新ID的映射
                
                # 先創建沒有父資料夾的資料夾
                for folder in folders_data:
                    if not folder['parent_id']:
                        new_folder = doc_crud.create_folder(
                            knowledge_base_id=kb.id,
                            name=folder['name']
                        )
                        folder_id_map[folder['id']] = new_folder.id
                
                # 再創建有父資料夾的資料夾
                for folder in folders_data:
                    if folder['parent_id']:
                        new_folder = doc_crud.create_folder(
                            knowledge_base_id=kb.id,
                            name=folder['name'],
                            parent_id=folder_id_map[folder['parent_id']]
                        )
                        folder_id_map[folder['id']] = new_folder.id
            
            # 導入文件
            for name in zf.namelist():
                if name.startswith('documents/') and name.endswith('.json'):
                    doc_data = json.loads(zf.read(name))
                    folder_id = folder_id_map.get(doc_data['folder_id']) if doc_data['folder_id'] else None
                    
                    doc_crud.create_document(
                        knowledge_base_id=kb.id,
                        folder_id=folder_id,
                        title=doc_data['title'],
                        content=doc_data['content'],
                        file_path=f"{doc_data['title']}.{doc_data['file_type']}",
                        file_type=doc_data['file_type']
                    )
            
            return True
            
    except Exception as e:
        st.error(f"導入失敗：{str(e)}")
        return False 