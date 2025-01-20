import streamlit as st
from shared.database.cloud_crud import CloudCRUD
from shared.utils.cloud_manager import CloudManager
from datetime import datetime

def show_cloud_kb():
    """顯示雲端知識庫頁面"""
    cloud_crud = CloudCRUD()
    cloud_manager = CloudManager()
    
    # 雲端服務設定
    with st.expander("雲端服務設定", expanded=True):
        show_cloud_settings(cloud_crud, cloud_manager)
    
    # 雲端文件列表
    st.subheader("雲端文件列表")
    show_cloud_documents(cloud_crud, cloud_manager)
    
    # 同步狀態
    with st.expander("同步狀態", expanded=True):
        show_sync_status(cloud_crud)

def show_cloud_settings(cloud_crud, cloud_manager):
    """顯示雲端服務設定"""
    # 選擇雲端服務
    service_type = st.selectbox(
        "選擇雲端服務",
        ["Google Drive", "Dropbox"],
        key="cloud_service_type"
    )
    
    if service_type == "Google Drive":
        show_google_drive_settings(cloud_crud, cloud_manager)
    else:
        show_dropbox_settings(cloud_crud, cloud_manager)
    
    # 同步設定
    st.subheader("同步設定")
    col1, col2 = st.columns(2)
    
    with col1:
        auto_sync = st.checkbox("啟用自動同步", value=True)
        if auto_sync:
            sync_interval = st.number_input(
                "同步間隔（分鐘）",
                min_value=5,
                value=30
            )
    
    with col2:
        if st.button("立即同步"):
            with st.spinner("正在同步..."):
                try:
                    result = cloud_manager.sync_documents()
                    if result['success']:
                        st.success("✅ 同步完成")
                        st.rerun()
                    else:
                        st.error(f"❌ 同步失敗：{result['error']}")
                except Exception as e:
                    st.error(f"❌ 同步時發生錯誤：{str(e)}")

def show_google_drive_settings(cloud_crud, cloud_manager):
    """顯示 Google Drive 設定"""
    st.subheader("Google Drive 設定")
    
    # 顯示當前狀態
    service = cloud_crud.get_service_by_type("google_drive")
    if service:
        st.info(f"狀態：{'已連接' if service.status == 'connected' else '未連接'}")
        if service.status == "connected":
            st.write(f"上次同步：{service.last_sync.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 設定選項
    col1, col2 = st.columns(2)
    
    with col1:
        folder_id = st.text_input(
            "資料夾 ID",
            value=service.config.get('folder_id', '') if service else '',
            help="Google Drive 資料夾的 ID"
        )
    
    with col2:
        if st.button("測試連接"):
            with st.spinner("測試中..."):
                result = cloud_manager.test_connection("google_drive", {
                    'folder_id': folder_id
                })
                if result['success']:
                    st.success("✅ 連接成功")
                else:
                    st.error(f"❌ 連接失敗：{result['error']}")

def show_dropbox_settings(cloud_crud, cloud_manager):
    """顯示 Dropbox 設定"""
    st.subheader("Dropbox 設定")
    
    # 顯示當前狀態
    service = cloud_crud.get_service_by_type("dropbox")
    if service:
        st.info(f"狀態：{'已連接' if service.status == 'connected' else '未連接'}")
        if service.status == "connected":
            st.write(f"上次同步：{service.last_sync.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 設定選項
    col1, col2 = st.columns(2)
    
    with col1:
        folder_path = st.text_input(
            "資料夾路徑",
            value=service.config.get('folder_path', '') if service else '',
            help="Dropbox 資料夾的路徑"
        )
    
    with col2:
        if st.button("測試連接"):
            with st.spinner("測試中..."):
                result = cloud_manager.test_connection("dropbox", {
                    'folder_path': folder_path
                })
                if result['success']:
                    st.success("✅ 連接成功")
                else:
                    st.error(f"❌ 連接失敗：{result['error']}")

def show_cloud_documents(cloud_crud, cloud_manager):
    """顯示雲端文件列表"""
    # 獲取所有雲端文件
    documents = cloud_crud.get_all_documents()
    
    if not documents:
        st.info("目前沒有任何雲端文件")
        return
    
    # 顯示文件列表
    for doc in documents:
        with st.expander(f"{doc.name} ({doc.path})", expanded=False):
            col1, col2 = st.columns([3,1])
            
            with col1:
                st.write(f"雲端服務：{doc.cloud_service.name}")
                st.write(f"檔案大小：{format_size(doc.size)}")
                st.write(f"最後修改：{doc.last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"同步狀態：{doc.sync_status}")
            
            with col2:
                if st.button("同步", key=f"sync_{doc.id}"):
                    with st.spinner("同步中..."):
                        try:
                            result = cloud_manager.sync_document(doc.id)
                            if result['success']:
                                st.success("✅ 同步成功")
                                st.rerun()
                            else:
                                st.error(f"❌ 同步失敗：{result['error']}")
                        except Exception as e:
                            st.error(f"❌ 同步時發生錯誤：{str(e)}")

def show_sync_status(cloud_crud):
    """顯示同步狀態統計"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("雲端文件總數", cloud_crud.count_documents())
    
    with col2:
        st.metric(
            "已同步文件數",
            cloud_crud.count_documents(sync_status="completed")
        )
    
    with col3:
        st.metric(
            "等待同步數",
            cloud_crud.count_documents(sync_status="pending")
        )

def format_size(size_in_bytes):
    """格式化檔案大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} TB" 