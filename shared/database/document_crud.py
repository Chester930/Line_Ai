from typing import List, Optional, Dict
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from .models import (
    Document, DocumentChunk, KnowledgeBase, KnowledgeBaseFolder,
    RoleKnowledgeBase, KnowledgeBasePermission, KnowledgeBaseShare,
    KnowledgeBaseLog, PermissionType
)
from .database import get_db

class DocumentCRUD:
    """文件資料庫操作"""
    
    def __init__(self):
        self.db = next(get_db())
    
    # 知識庫相關操作
    def create_knowledge_base(
        self,
        user_id: int,
        name: str,
        description: str = None,
        is_default: bool = False
    ) -> Optional[KnowledgeBase]:
        """創建新知識庫"""
        try:
            kb = KnowledgeBase(
                user_id=user_id,
                name=name,
                description=description,
                is_default=is_default
            )
            self.db.add(kb)
            self.db.commit()
            self.db.refresh(kb)
            return kb
        except Exception as e:
            self.db.rollback()
            raise

    def get_knowledge_base(self, kb_id: int) -> Optional[KnowledgeBase]:
        """獲取知識庫"""
        return self.db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    def get_user_knowledge_bases(self, user_id: int) -> List[KnowledgeBase]:
        """獲取用戶的所有知識庫"""
        return self.db.query(KnowledgeBase).filter(KnowledgeBase.user_id == user_id).all()

    def delete_knowledge_base(self, kb_id: int) -> bool:
        """刪除知識庫"""
        try:
            kb = self.get_knowledge_base(kb_id)
            if kb:
                self.db.delete(kb)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            return False

    # 資料夾相關操作
    def create_folder(
        self,
        knowledge_base_id: int,
        name: str,
        parent_id: Optional[int] = None
    ) -> Optional[KnowledgeBaseFolder]:
        """創建資料夾"""
        try:
            # 構建完整路徑
            path = name
            if parent_id:
                parent = self.get_folder(parent_id)
                if parent:
                    path = f"{parent.path}/{name}"
            
            folder = KnowledgeBaseFolder(
                knowledge_base_id=knowledge_base_id,
                parent_id=parent_id,
                name=name,
                path=path
            )
            self.db.add(folder)
            self.db.commit()
            self.db.refresh(folder)
            return folder
        except Exception as e:
            self.db.rollback()
            raise

    def get_folder(self, folder_id: int) -> Optional[KnowledgeBaseFolder]:
        """獲取資料夾"""
        return self.db.query(KnowledgeBaseFolder).filter(KnowledgeBaseFolder.id == folder_id).first()
    
    def get_knowledge_base_folders(self, kb_id: int) -> List[KnowledgeBaseFolder]:
        """獲取知識庫的所有資料夾"""
        return self.db.query(KnowledgeBaseFolder).filter(KnowledgeBaseFolder.knowledge_base_id == kb_id).all()

    def delete_folder(self, folder_id: int) -> bool:
        """刪除資料夾"""
        try:
            folder = self.get_folder(folder_id)
            if folder:
                self.db.delete(folder)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            return False

    # 文件相關操作
    def create_document(
        self,
        knowledge_base_id: int,
        title: str,
        content: str,
        file_path: str,
        file_type: str,
        folder_id: Optional[int] = None
    ) -> Optional[Document]:
        """創建新文件"""
        try:
            doc = Document(
                knowledge_base_id=knowledge_base_id,
                folder_id=folder_id,
                title=title,
                content=content,
                file_path=file_path,
                file_type=file_type,
                embedding_status="pending"
            )
            self.db.add(doc)
            self.db.commit()
            self.db.refresh(doc)
            return doc
        except Exception as e:
            self.db.rollback()
            raise
    
    def get_document(self, doc_id: int) -> Optional[Document]:
        """獲取單個文件"""
        return self.db.query(Document).filter(Document.id == doc_id).first()
    
    def get_knowledge_base_documents(
        self,
        kb_id: int,
        folder_id: Optional[int] = None
    ) -> List[Document]:
        """獲取知識庫中的文件"""
        query = self.db.query(Document).filter(Document.knowledge_base_id == kb_id)
        if folder_id is not None:
            query = query.filter(Document.folder_id == folder_id)
        return query.all()
    
    def delete_document(self, doc_id: int) -> bool:
        """刪除文件"""
        try:
            doc = self.get_document(doc_id)
            if doc:
                self.db.delete(doc)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            return False

    def count_documents(self, kb_id: Optional[int] = None, embedding_status: Optional[str] = None) -> int:
        """計算文件數量"""
        query = self.db.query(Document)
        if kb_id is not None:
            query = query.filter(Document.knowledge_base_id == kb_id)
        if embedding_status:
            query = query.filter(Document.embedding_status == embedding_status)
        return query.count()

    def count_chunks(self, kb_id: Optional[int] = None) -> int:
        """計算文本片段數量"""
        query = self.db.query(DocumentChunk)
        if kb_id is not None:
            query = query.join(Document).filter(Document.knowledge_base_id == kb_id)
        return query.count()

    # 角色知識庫相關操作
    def get_role_knowledge_bases(self, role_id: str) -> List[KnowledgeBase]:
        """獲取角色配置的知識庫列表"""
        return self.db.query(KnowledgeBase)\
            .join(RoleKnowledgeBase)\
            .filter(RoleKnowledgeBase.role_id == role_id)\
            .all()
    
    def update_role_knowledge_bases(
        self,
        role_id: str,
        knowledge_base_ids: List[int]
    ) -> bool:
        """更新角色的知識庫配置"""
        try:
            # 刪除現有配置
            self.db.query(RoleKnowledgeBase)\
                .filter(RoleKnowledgeBase.role_id == role_id)\
                .delete()
            
            # 添加新配置
            for kb_id in knowledge_base_ids:
                role_kb = RoleKnowledgeBase(
                    role_id=role_id,
                    knowledge_base_id=kb_id
                )
                self.db.add(role_kb)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def add_role_knowledge_base(
        self,
        role_id: str,
        knowledge_base_id: int
    ) -> bool:
        """為角色添加知識庫"""
        try:
            role_kb = RoleKnowledgeBase(
                role_id=role_id,
                knowledge_base_id=knowledge_base_id
            )
            self.db.add(role_kb)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def remove_role_knowledge_base(
        self,
        role_id: str,
        knowledge_base_id: int
    ) -> bool:
        """移除角色的知識庫"""
        try:
            self.db.query(RoleKnowledgeBase)\
                .filter(
                    RoleKnowledgeBase.role_id == role_id,
                    RoleKnowledgeBase.knowledge_base_id == knowledge_base_id
                )\
                .delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False

    # 文本塊相關操作
    def create_document_chunk(
        self,
        document_id: int,
        content: str,
        embedding: List[float]
    ) -> Optional[DocumentChunk]:
        """創建文本塊"""
        try:
            chunk = DocumentChunk(
                document_id=document_id,
                content=content,
                embedding=embedding
            )
            self.db.add(chunk)
            self.db.commit()
            self.db.refresh(chunk)
            return chunk
        except Exception as e:
            self.db.rollback()
            raise
    
    def get_document_chunks(
        self,
        document_id: int
    ) -> List[DocumentChunk]:
        """獲取文件的所有文本塊"""
        return self.db.query(DocumentChunk)\
            .filter(DocumentChunk.document_id == document_id)\
            .all()
    
    def delete_document_chunks(
        self,
        document_id: int
    ) -> bool:
        """刪除文件的所有文本塊"""
        try:
            self.db.query(DocumentChunk)\
                .filter(DocumentChunk.document_id == document_id)\
                .delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def update_document_status(
        self,
        doc_id: int,
        status: str
    ) -> bool:
        """更新文件狀態"""
        try:
            doc = self.get_document(doc_id)
            if doc:
                doc.embedding_status = status
                doc.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            return False

    # 權限相關操作
    def check_permission(
        self,
        user_id: int,
        kb_id: int,
        required_permission: PermissionType
    ) -> bool:
        """檢查用戶是否有指定權限"""
        # 檢查是否為知識庫擁有者
        kb = self.get_knowledge_base(kb_id)
        if kb and kb.user_id == user_id:
            return True
        
        # 檢查是否有指定權限
        permission = self.db.query(KnowledgeBasePermission)\
            .filter(
                KnowledgeBasePermission.knowledge_base_id == kb_id,
                KnowledgeBasePermission.user_id == user_id
            )\
            .first()
        
        if not permission:
            return False
        
        # ADMIN 權限可以執行所有操作
        if permission.permission_type == PermissionType.ADMIN:
            return True
        
        # WRITE 權限可以執行 READ 和 WRITE 操作
        if permission.permission_type == PermissionType.WRITE:
            return required_permission != PermissionType.ADMIN
        
        # READ 權限只能執行 READ 操作
        return required_permission == PermissionType.READ
    
    def grant_permission(
        self,
        kb_id: int,
        user_id: int,
        permission_type: PermissionType
    ) -> bool:
        """授予用戶權限"""
        try:
            # 檢查是否已有權限
            existing = self.db.query(KnowledgeBasePermission)\
                .filter(
                    KnowledgeBasePermission.knowledge_base_id == kb_id,
                    KnowledgeBasePermission.user_id == user_id
                )\
                .first()
            
            if existing:
                # 更新現有權限
                existing.permission_type = permission_type
                existing.updated_at = datetime.utcnow()
            else:
                # 創建新權限
                permission = KnowledgeBasePermission(
                    knowledge_base_id=kb_id,
                    user_id=user_id,
                    permission_type=permission_type
                )
                self.db.add(permission)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def revoke_permission(
        self,
        kb_id: int,
        user_id: int
    ) -> bool:
        """撤銷用戶權限"""
        try:
            self.db.query(KnowledgeBasePermission)\
                .filter(
                    KnowledgeBasePermission.knowledge_base_id == kb_id,
                    KnowledgeBasePermission.user_id == user_id
                )\
                .delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def get_kb_permissions(
        self,
        kb_id: int
    ) -> List[KnowledgeBasePermission]:
        """獲取知識庫的所有權限設置"""
        return self.db.query(KnowledgeBasePermission)\
            .filter(KnowledgeBasePermission.knowledge_base_id == kb_id)\
            .all()
    
    # 分享相關操作
    def create_share(
        self,
        kb_id: int,
        permission_type: PermissionType,
        expires_at: Optional[datetime] = None
    ) -> Optional[str]:
        """創建分享"""
        try:
            # 生成分享碼
            share_code = str(uuid.uuid4())
            
            # 創建分享記錄
            share = KnowledgeBaseShare(
                knowledge_base_id=kb_id,
                share_code=share_code,
                permission_type=permission_type,
                expires_at=expires_at
            )
            self.db.add(share)
            self.db.commit()
            
            return share_code
        except Exception as e:
            self.db.rollback()
            return None
    
    def get_share(
        self,
        share_code: str
    ) -> Optional[KnowledgeBaseShare]:
        """獲取分享信息"""
        return self.db.query(KnowledgeBaseShare)\
            .filter(KnowledgeBaseShare.share_code == share_code)\
            .first()
    
    def delete_share(
        self,
        share_code: str
    ) -> bool:
        """刪除分享"""
        try:
            self.db.query(KnowledgeBaseShare)\
                .filter(KnowledgeBaseShare.share_code == share_code)\
                .delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def get_kb_shares(
        self,
        kb_id: int
    ) -> List[KnowledgeBaseShare]:
        """獲取知識庫的所有分享"""
        return self.db.query(KnowledgeBaseShare)\
            .filter(KnowledgeBaseShare.knowledge_base_id == kb_id)\
            .all()
    
    # 日誌相關操作
    def log_action(
        self,
        kb_id: int,
        user_id: int,
        action: str,
        details: Dict = None
    ) -> bool:
        """記錄操作日誌"""
        try:
            log = KnowledgeBaseLog(
                knowledge_base_id=kb_id,
                user_id=user_id,
                action=action,
                details=details or {}
            )
            self.db.add(log)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def get_kb_logs(
        self,
        kb_id: int,
        limit: int = 100
    ) -> List[KnowledgeBaseLog]:
        """獲取知識庫的操作日誌"""
        return self.db.query(KnowledgeBaseLog)\
            .filter(KnowledgeBaseLog.knowledge_base_id == kb_id)\
            .order_by(KnowledgeBaseLog.created_at.desc())\
            .limit(limit)\
            .all() 