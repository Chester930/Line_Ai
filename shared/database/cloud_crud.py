from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from .models import CloudService, CloudDocument
from .database import get_db

class CloudCRUD:
    """雲端服務資料庫操作"""
    
    def __init__(self):
        self.db = next(get_db())
    
    def create_service(
        self,
        name: str,
        service_type: str,
        config: dict
    ) -> Optional[CloudService]:
        """創建雲端服務"""
        try:
            service = CloudService(
                name=name,
                service_type=service_type,
                config=config,
                status="pending"
            )
            self.db.add(service)
            self.db.commit()
            self.db.refresh(service)
            return service
        except Exception as e:
            self.db.rollback()
            raise
    
    def get_service(self, service_id: int) -> Optional[CloudService]:
        """獲取雲端服務"""
        return self.db.query(CloudService).filter(CloudService.id == service_id).first()
    
    def get_service_by_type(self, service_type: str) -> Optional[CloudService]:
        """根據類型獲取雲端服務"""
        return self.db.query(CloudService).filter(CloudService.service_type == service_type).first()
    
    def update_service_status(
        self,
        service_id: int,
        status: str,
        last_sync: datetime = None
    ) -> bool:
        """更新服務狀態"""
        try:
            service = self.get_service(service_id)
            if service:
                service.status = status
                if last_sync:
                    service.last_sync = last_sync
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            return False
    
    def create_document(
        self,
        cloud_service_id: int,
        remote_id: str,
        name: str,
        path: str,
        size: int,
        last_modified: datetime
    ) -> Optional[CloudDocument]:
        """創建雲端文件記錄"""
        try:
            doc = CloudDocument(
                cloud_service_id=cloud_service_id,
                remote_id=remote_id,
                name=name,
                path=path,
                size=size,
                last_modified=last_modified,
                sync_status="pending"
            )
            self.db.add(doc)
            self.db.commit()
            self.db.refresh(doc)
            return doc
        except Exception as e:
            self.db.rollback()
            raise
    
    def get_document(self, doc_id: int) -> Optional[CloudDocument]:
        """獲取雲端文件"""
        return self.db.query(CloudDocument).filter(CloudDocument.id == doc_id).first()
    
    def get_all_documents(self) -> List[CloudDocument]:
        """獲取所有雲端文件"""
        return self.db.query(CloudDocument).all()
    
    def update_document_status(
        self,
        doc_id: int,
        status: str
    ) -> bool:
        """更新文件同步狀態"""
        try:
            doc = self.get_document(doc_id)
            if doc:
                doc.sync_status = status
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            return False
    
    def count_documents(self, sync_status: str = None) -> int:
        """計算文件數量"""
        query = self.db.query(CloudDocument)
        if sync_status:
            query = query.filter(CloudDocument.sync_status == sync_status)
        return query.count() 