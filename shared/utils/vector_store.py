from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from shared.database.document_crud import DocumentCRUD

class VectorStore:
    """向量存儲和搜索"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 使用輕量級模型
        self.document_crud = DocumentCRUD()
    
    def get_embedding(self, text: str) -> List[float]:
        """獲取文本的向量嵌入"""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Dict]:
        """搜索相關文檔片段"""
        # 獲取查詢的向量表示
        query_embedding = self.get_embedding(query)
        
        # 獲取所有文檔片段
        all_chunks = []
        for doc in self.document_crud.get_all_documents():
            chunks = self.document_crud.get_document_chunks(doc.id)
            all_chunks.extend(chunks)
        
        # 計算相似度並排序
        results = []
        for chunk in all_chunks:
            if chunk.embedding:  # 確保有向量嵌入
                similarity = self._cosine_similarity(
                    query_embedding,
                    chunk.embedding
                )
                
                if similarity >= threshold:
                    results.append({
                        'document_id': chunk.document_id,
                        'chunk_id': chunk.id,
                        'content': chunk.content,
                        'similarity': similarity
                    })
        
        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """計算餘弦相似度"""
        v1_array = np.array(v1)
        v2_array = np.array(v2)
        
        dot_product = np.dot(v1_array, v2_array)
        norm_v1 = np.linalg.norm(v1_array)
        norm_v2 = np.linalg.norm(v2_array)
        
        return dot_product / (norm_v1 * norm_v2) 