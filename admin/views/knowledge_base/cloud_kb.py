import streamlit as st
from shared.utils.cloud_manager import CloudServiceManager
from shared.database.models import CloudSource, KnowledgeBase
from datetime import datetime
from shared.database.database import SessionLocal
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

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

def show_cloud_kb_section(kb: KnowledgeBase, db: Session):
    """顯示雲端來源管理區塊"""
    try:
        st.subheader("雲端來源管理")
        
        # 添加新的雲端來源
        with st.form(key=f"add_cloud_source_{kb.id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("來源名稱", placeholder="例如：公司網站")
                url = st.text_input("URL", placeholder="https://...")
            
            with col2:
                source_type = st.selectbox(
                    "來源類型",
                    options=["webpage", "api", "rss"],
                    format_func=lambda x: {
                        "webpage": "網頁",
                        "api": "API",
                        "rss": "RSS Feed"
                    }.get(x, x)
                )
                sync_frequency = st.selectbox(
                    "同步頻率",
                    options=["hourly", "daily", "weekly"],
                    format_func=lambda x: {
                        "hourly": "每小時",
                        "daily": "每天",
                        "weekly": "每週"
                    }.get(x, x)
                )
            
            if st.form_submit_button("添加來源"):
                if not name or not url:
                    st.error("請填寫來源名稱和 URL")
                else:
                    try:
                        # 檢查是否已存在相同的來源
                        existing = db.query(CloudSource).filter(
                            CloudSource.knowledge_base_id == kb.id,
                            CloudSource.name == name
                        ).first()
                        
                        if existing:
                            st.error(f"來源名稱 '{name}' 已存在")
                        else:
                            # 創建新的雲端來源
                            cloud_source = CloudSource(
                                knowledge_base_id=kb.id,
                                name=name,
                                url=url,
                                type=source_type,
                                sync_frequency=sync_frequency,
                                created_at=datetime.utcnow()
                            )
                            db.add(cloud_source)
                            db.commit()
                            st.success("成功添加雲端來源")
                            st.rerun()
                    except Exception as e:
                        logger.error(f"添加雲端來源失敗: {str(e)}")
                        st.error("添加雲端來源失敗")
                        db.rollback()
        
        # 顯示現有雲端來源
        st.markdown("---")
        st.subheader("現有來源")
        
        if not kb.cloud_sources:
            st.info("尚未添加任何雲端來源")
        else:
            for source in kb.cloud_sources:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.write(f"🌐 {source.name}")
                        st.caption(f"URL: {source.url}")
                    
                    with col2:
                        st.caption(f"類型: {source.type}")
                        st.caption(f"同步頻率: {source.sync_frequency}")
                        if source.last_sync:
                            st.caption(f"上次同步: {source.last_sync.strftime('%Y-%m-%d %H:%M')}")
                    
                    with col3:
                        # 立即同步按鈕
                        if st.button("同步", key=f"sync_{source.id}"):
                            with st.spinner("同步中..."):
                                try:
                                    # TODO: 實現同步邏輯
                                    st.success("同步完成")
                                except Exception as e:
                                    logger.error(f"同步失敗: {str(e)}")
                                    st.error("同步失敗")
                        
                        # 刪除按鈕
                        if st.button("刪除", key=f"del_source_{source.id}"):
                            try:
                                db.delete(source)
                                db.commit()
                                st.success("已刪除雲端來源")
                                st.rerun()
                            except Exception as e:
                                logger.error(f"刪除雲端來源失敗: {str(e)}")
                                st.error("刪除失敗")
                                db.rollback()
                    
                    st.divider()
                    
    except Exception as e:
        logger.error(f"雲端來源管理錯誤: {str(e)}")
        st.error("載入雲端來源管理時發生錯誤") 