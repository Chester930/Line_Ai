from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from shared.database.document_crud import DocumentCRUD

class VectorStore:
    """向量存儲和搜索"""
    
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        self.doc_crud = DocumentCRUD()
    
    def encode(self, text: str) -> np.ndarray:
        """將文本編碼為向量"""
        return self.model.encode(text)
    
    def search(
        self,
        query: str,
        filters: Optional[Dict] = None,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Dict]:
        """搜索相似內容
        
        Args:
            query: 搜索查詢
            filters: 過濾條件，包含 knowledge_base_ids 和 folder_ids
            top_k: 返回結果數量
            threshold: 相似度閾值
            
        Returns:
            List[Dict]: 搜索結果列表
        """
        # 對查詢文本進行向量化
        query_vector = self.encode(query)
        
        # 構建查詢條件
        conditions = []
        if filters:
            if filters.get("knowledge_base_ids"):
                conditions.append(
                    "d.knowledge_base_id IN :kb_ids"
                )
            if filters.get("folder_ids"):
                conditions.append(
                    "d.folder_id IN :folder_ids"
                )
        
        # 構建 SQL 查詢
        sql = """
            SELECT 
                dc.id,
                dc.document_id,
                dc.content,
                dc.embedding,
                d.title,
                d.file_type,
                d.knowledge_base_id,
                d.folder_id
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
        """
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        # 執行查詢
        params = {}
        if filters:
            if filters.get("knowledge_base_ids"):
                params["kb_ids"] = filters["knowledge_base_ids"]
            if filters.get("folder_ids"):
                params["folder_ids"] = filters["folder_ids"]
        
        chunks = self.doc_crud.db.execute(sql, params).fetchall()
        
        # 計算相似度並排序
        results = []
        for chunk in chunks:
            chunk_vector = np.array(chunk.embedding)
            similarity = np.dot(query_vector, chunk_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(chunk_vector)
            )
            
            if similarity >= threshold:
                results.append({
                    'chunk_id': chunk.id,
                    'document_id': chunk.document_id,
                    'content': chunk.content,
                    'similarity': float(similarity)
                })
        
        # 按相似度排序並返回 top_k 結果
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def add_document(self, document_id: int, chunk_size: int = 500) -> bool:
        """添加文件到向量存儲
        
        Args:
            document_id: 文件ID
            chunk_size: 文本分塊大小
            
        Returns:
            bool: 是否成功
        """
        try:
            # 獲取文件
            doc = self.doc_crud.get_document(document_id)
            if not doc:
                return False
            
            # 分塊並向量化
            chunks = self._split_text(doc.content, chunk_size)
            for chunk in chunks:
                embedding = self.encode(chunk)
                
                # 保存到數據庫
                self.doc_crud.create_document_chunk(
                    document_id=doc.id,
                    content=chunk,
                    embedding=embedding.tolist()
                )
            
            # 更新文件狀態
            self.doc_crud.update_document_status(
                doc_id=doc.id,
                status="completed"
            )
            
            return True
        except Exception as e:
            print(f"Error adding document to vector store: {str(e)}")
            return False
    
    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """將文本分塊
        
        Args:
            text: 要分塊的文本
            chunk_size: 每塊的大小
            
        Returns:
            List[str]: 文本塊列表
        """
        # 簡單按字符數分塊，可以根據需要改進分塊策略
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            if chunk.strip():  # 忽略空白塊
                chunks.append(chunk)
        return chunks 