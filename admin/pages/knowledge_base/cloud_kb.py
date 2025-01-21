import streamlit as st
from shared.utils.cloud_manager import CloudServiceManager

def show_cloud_kb():
    """雲端知識庫管理"""
    st.subheader("雲端知識庫設定 (Cloud Knowledge Base Settings)")
    
    # 雲端服務選擇
    cloud_service = st.selectbox(
        "選擇雲端服務 (Select Cloud Service)",
        ["Google Drive", "Dropbox", "OneDrive", "自定義 WebDAV"],
        help="選擇要連接的雲端儲存服務"
    )
    
    # 顯示對應的設定選項
    show_service_settings(cloud_service)
    
    # 顯示已連接的服務
    show_connected_services()

def show_service_settings(service_type: str):
    """顯示服務設定選項"""
    with st.form(f"cloud_service_{service_type}"):
        if service_type == "Google Drive":
            st.info("Google Drive 連接設定")
            client_id = st.text_input("Client ID", type="password")
            client_secret = st.text_input("Client Secret", type="password")
            folder_id = st.text_input("指定資料夾 ID (Optional)")
            
        elif service_type == "Dropbox":
            st.info("Dropbox 連接設定")
            app_key = st.text_input("App Key", type="password")
            app_secret = st.text_input("App Secret", type="password")
            folder_path = st.text_input("指定資料夾路徑 (Optional)")
            
        elif service_type == "OneDrive":
            st.info("OneDrive 連接設定")
            client_id = st.text_input("Client ID", type="password")
            client_secret = st.text_input("Client Secret", type="password")
            folder_path = st.text_input("指定資料夾路徑 (Optional)")
            
        else:  # WebDAV
            st.info("WebDAV 連接設定")
            webdav_url = st.text_input("WebDAV URL")
            username = st.text_input("使用者名稱")
            password = st.text_input("密碼", type="password")
            folder_path = st.text_input("指定資料夾路徑 (Optional)")
        
        if st.form_submit_button("連接"):
            with st.spinner("正在連接..."):
                # TODO: 實現實際的連接邏輯
                st.success(f"成功連接到 {service_type}")

def show_connected_services():
    """顯示已連接的雲端服務"""
    st.subheader("已連接的雲端服務 (Connected Cloud Services)")
    
    # TODO: 從資料庫獲取實際連接的服務
    cloud_services = [
        {"name": "Google Drive", "status": "已連接", "last_sync": "2024-03-15 10:30"},
        {"name": "Dropbox", "status": "同步中", "last_sync": "2024-03-15 09:15"}
    ]
    
    for service in cloud_services:
        with st.expander(f"{service['name']}", expanded=False):
            col1, col2, col3 = st.columns([2,2,1])
            with col1:
                st.write(f"狀態：{service['status']}")
            with col2:
                st.write(f"最後同步：{service['last_sync']}")
            with col3:
                st.button("中斷連接", key=f"disconnect_{service['name']}")
                st.button("立即同步", key=f"sync_{service['name']}") 