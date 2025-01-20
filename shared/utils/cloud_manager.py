from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import os
from datetime import datetime
from shared.database.models import CloudService, CloudDocument
from shared.database.document_crud import DocumentCRUD
from shared.database.cloud_crud import CloudCRUD
from shared.config.config import Config
import logging
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import dropbox
from dropbox.exceptions import ApiError
import io

logger = logging.getLogger(__name__)

class CloudServiceManager(ABC):
    """雲端服務管理器基類"""
    
    @abstractmethod
    def connect(self, config: Dict) -> bool:
        """連接雲端服務"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """中斷連接"""
        pass
    
    @abstractmethod
    def sync_files(self, folder_path: Optional[str] = None) -> List[Dict]:
        """同步文件"""
        pass
    
    @abstractmethod
    def download_file(self, file_id: str) -> bytes:
        """下載文件"""
        pass

class GoogleDriveManager(CloudServiceManager):
    """Google Drive 管理器"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    MIME_TYPES = {
        'text/plain': '.txt',
        'application/pdf': '.pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx'
    }
    
    def __init__(self):
        self.service = None
        self.config = Config()
    
    def connect(self, config: Dict) -> bool:
        """連接 Google Drive"""
        try:
            credentials = service_account.Credentials.from_service_account_info(
                config.get("credentials"),
                scopes=self.SCOPES
            )
            self.service = build("drive", "v3", credentials=credentials)
            return True
        except Exception as e:
            logger.error(f"Google Drive 連接失敗: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """中斷 Google Drive 連接"""
        try:
            if self.service:
                self.service.close()
                self.service = None
            return True
        except Exception as e:
            logger.error(f"中斷 Google Drive 連接失敗: {str(e)}")
            return False
    
    def sync_files(self, folder_id: Optional[str] = None) -> List[Dict]:
        """同步 Google Drive 文件"""
        try:
            if not self.service:
                raise Exception("未連接到 Google Drive")
            
            results = []
            query = f"'{folder_id}' in parents" if folder_id else "root in parents"
            
            # 列出文件
            response = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, size, modifiedTime)'
            ).execute()
            
            for file in response.get('files', []):
                if file['mimeType'] in self.MIME_TYPES:
                    results.append({
                        'id': file['id'],
                        'name': file['name'],
                        'type': file['mimeType'],
                        'size': int(file.get('size', 0)),
                        'modified': file['modifiedTime']
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"同步 Google Drive 文件失敗: {str(e)}")
            return []
    
    def download_file(self, file_id: str) -> bytes:
        """下載 Google Drive 文件"""
        try:
            if not self.service:
                raise Exception("未連接到 Google Drive")
            
            request = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            return file.getvalue()
            
        except Exception as e:
            logger.error(f"下載 Google Drive 文件失敗: {str(e)}")
            return None

class DropboxManager(CloudServiceManager):
    """Dropbox 管理器"""
    
    def __init__(self):
        self.client = None
        self.config = Config()
    
    def connect(self, config: Dict) -> bool:
        """連接 Dropbox"""
        try:
            self.client = dropbox.Dropbox(config.get("access_token"))
            self.client.users_get_current_account()
            return True
        except Exception as e:
            logger.error(f"Dropbox 連接失敗: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """中斷 Dropbox 連接"""
        try:
            if self.client:
                self.client.close()
                self.client = None
            return True
        except Exception as e:
            logger.error(f"中斷 Dropbox 連接失敗: {str(e)}")
            return False
    
    def sync_files(self, folder_path: Optional[str] = None) -> List[Dict]:
        """同步 Dropbox 文件"""
        try:
            if not self.client:
                raise Exception("未連接到 Dropbox")
            
            results = []
            path = folder_path or ""
            
            response = self.client.files_list_folder(path)
            for entry in response.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    results.append({
                        'id': entry.id,
                        'name': entry.name,
                        'path': entry.path_display,
                        'size': entry.size,
                        'modified': entry.client_modified
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"同步 Dropbox 文件失敗: {str(e)}")
            return []
    
    def download_file(self, file_path: str) -> bytes:
        """下載 Dropbox 文件"""
        try:
            if not self.client:
                raise Exception("未連接到 Dropbox")
            
            metadata, response = self.client.files_download(file_path)
            return response.content
            
        except Exception as e:
            logger.error(f"下載 Dropbox 文件失敗: {str(e)}")
            return None

class CloudManager:
    """雲端服務管理器"""
    
    def __init__(self):
        self.config = Config()
        self.cloud_crud = CloudCRUD()
        self.services = {}
        self._init_services()
    
    def _init_services(self):
        """初始化雲端服務"""
        # 初始化 Google Drive
        google_service = self.cloud_crud.get_service_by_type("google_drive")
        if google_service and google_service.status == "connected":
            try:
                self.services["google_drive"] = self._init_google_drive(google_service.config)
            except Exception as e:
                logger.error(f"初始化 Google Drive 失敗: {str(e)}")
        
        # 初始化 Dropbox
        dropbox_service = self.cloud_crud.get_service_by_type("dropbox")
        if dropbox_service and dropbox_service.status == "connected":
            try:
                self.services["dropbox"] = self._init_dropbox(dropbox_service.config)
            except Exception as e:
                logger.error(f"初始化 Dropbox 失敗: {str(e)}")
    
    def _init_google_drive(self, config: Dict) -> Any:
        """初始化 Google Drive 服務"""
        try:
            credentials = service_account.Credentials.from_service_account_info(
                config.get("credentials"),
                scopes=["https://www.googleapis.com/auth/drive.readonly"]
            )
            return build("drive", "v3", credentials=credentials)
        except Exception as e:
            raise Exception(f"初始化 Google Drive 失敗: {str(e)}")
    
    def _init_dropbox(self, config: Dict) -> Any:
        """初始化 Dropbox 服務"""
        try:
            return dropbox.Dropbox(config.get("access_token"))
        except Exception as e:
            raise Exception(f"初始化 Dropbox 失敗: {str(e)}")
    
    def test_connection(self, service_type: str, config: Dict) -> Dict[str, Any]:
        """測試雲端服務連接"""
        try:
            if service_type == "google_drive":
                service = self._init_google_drive(config)
                # 測試列出文件
                service.files().list(pageSize=1).execute()
                return {"success": True}
            
            elif service_type == "dropbox":
                dbx = self._init_dropbox(config)
                # 測試獲取帳戶信息
                dbx.users_get_current_account()
                return {"success": True}
            
            else:
                return {
                    "success": False,
                    "error": f"不支援的服務類型: {service_type}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_documents(self) -> Dict[str, Any]:
        """同步所有雲端文件"""
        try:
            results = {
                "success": True,
                "synced": 0,
                "failed": 0,
                "errors": []
            }
            
            # 同步 Google Drive
            if "google_drive" in self.services:
                google_result = self._sync_google_drive()
                self._update_sync_results(results, google_result)
            
            # 同步 Dropbox
            if "dropbox" in self.services:
                dropbox_result = self._sync_dropbox()
                self._update_sync_results(results, dropbox_result)
            
            return results
            
        except Exception as e:
            logger.error(f"同步文件時發生錯誤: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_document(self, doc_id: int) -> Dict[str, Any]:
        """同步單個文件"""
        try:
            doc = self.cloud_crud.get_document(doc_id)
            if not doc:
                return {
                    "success": False,
                    "error": "找不到指定文件"
                }
            
            service = doc.cloud_service
            if service.service_type == "google_drive":
                return self._sync_google_drive_file(doc)
            elif service.service_type == "dropbox":
                return self._sync_dropbox_file(doc)
            else:
                return {
                    "success": False,
                    "error": f"不支援的服務類型: {service.service_type}"
                }
                
        except Exception as e:
            logger.error(f"同步文件時發生錯誤: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _sync_google_drive(self) -> Dict[str, Any]:
        """同步 Google Drive 文件"""
        try:
            if "google_drive" not in self.services:
                return {
                    "success": False,
                    "error": "Google Drive 服務未初始化",
                    "synced": 0,
                    "failed": 0,
                    "errors": []
                }
            
            service = self.services["google_drive"]
            google_service = self.cloud_crud.get_service_by_type("google_drive")
            folder_id = google_service.config.get("folder_id")
            
            results = {
                "success": True,
                "synced": 0,
                "failed": 0,
                "errors": []
            }
            
            # 列出文件
            query = f"'{folder_id}' in parents" if folder_id else "root in parents"
            response = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, size, modifiedTime)'
            ).execute()
            
            for file in response.get('files', []):
                try:
                    # 檢查文件是否已存在
                    existing_doc = self.cloud_crud.get_document_by_remote_id(
                        google_service.id,
                        file['id']
                    )
                    
                    if not existing_doc:
                        # 創建新文件記錄
                        doc = self.cloud_crud.create_document(
                            cloud_service_id=google_service.id,
                            remote_id=file['id'],
                            name=file['name'],
                            path=f"/drive/{file['id']}",
                            size=int(file.get('size', 0)),
                            last_modified=datetime.fromisoformat(file['modifiedTime'].replace('Z', '+00:00'))
                        )
                        results["synced"] += 1
                    
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(str(e))
            
            return results
            
        except Exception as e:
            logger.error(f"Google Drive 同步失敗: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "synced": 0,
                "failed": 0,
                "errors": [str(e)]
            }
    
    def _sync_dropbox(self) -> Dict[str, Any]:
        """同步 Dropbox 文件"""
        try:
            if "dropbox" not in self.services:
                return {
                    "success": False,
                    "error": "Dropbox 服務未初始化",
                    "synced": 0,
                    "failed": 0,
                    "errors": []
                }
            
            dbx = self.services["dropbox"]
            dropbox_service = self.cloud_crud.get_service_by_type("dropbox")
            folder_path = dropbox_service.config.get("folder_path", "")
            
            results = {
                "success": True,
                "synced": 0,
                "failed": 0,
                "errors": []
            }
            
            # 列出文件
            response = dbx.files_list_folder(folder_path)
            
            for entry in response.entries:
                try:
                    if isinstance(entry, dropbox.files.FileMetadata):
                        # 檢查文件是否已存在
                        existing_doc = self.cloud_crud.get_document_by_remote_id(
                            dropbox_service.id,
                            entry.id
                        )
                        
                        if not existing_doc:
                            # 創建新文件記錄
                            doc = self.cloud_crud.create_document(
                                cloud_service_id=dropbox_service.id,
                                remote_id=entry.id,
                                name=entry.name,
                                path=entry.path_display,
                                size=entry.size,
                                last_modified=entry.client_modified
                            )
                            results["synced"] += 1
                        
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(str(e))
            
            return results
            
        except Exception as e:
            logger.error(f"Dropbox 同步失敗: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "synced": 0,
                "failed": 0,
                "errors": [str(e)]
            }
    
    def _sync_google_drive_file(self, doc: CloudDocument) -> Dict[str, Any]:
        """同步單個 Google Drive 文件"""
        try:
            if "google_drive" not in self.services:
                return {
                    "success": False,
                    "error": "Google Drive 服務未初始化"
                }
            
            service = self.services["google_drive"]
            
            # 下載文件
            request = service.files().get_media(fileId=doc.remote_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            # 更新文件狀態
            self.cloud_crud.update_document_status(doc.id, "completed")
            
            return {
                "success": True,
                "content": file.getvalue()
            }
            
        except Exception as e:
            logger.error(f"同步 Google Drive 文件失敗: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _sync_dropbox_file(self, doc: CloudDocument) -> Dict[str, Any]:
        """同步單個 Dropbox 文件"""
        try:
            if "dropbox" not in self.services:
                return {
                    "success": False,
                    "error": "Dropbox 服務未初始化"
                }
            
            dbx = self.services["dropbox"]
            
            # 下載文件
            metadata, response = dbx.files_download(doc.path)
            
            # 更新文件狀態
            self.cloud_crud.update_document_status(doc.id, "completed")
            
            return {
                "success": True,
                "content": response.content
            }
            
        except Exception as e:
            logger.error(f"同步 Dropbox 文件失敗: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _update_sync_results(self, results: Dict, new_result: Dict):
        """更新同步結果"""
        results["synced"] += new_result.get("synced", 0)
        results["failed"] += new_result.get("failed", 0)
        if "errors" in new_result:
            results["errors"].extend(new_result["errors"])

# ... 其他雲端服務管理器 