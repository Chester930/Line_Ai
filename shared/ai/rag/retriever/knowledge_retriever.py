from typing import List, Dict, Optional
import numpy as np
from shared.ai.vector_store import VectorStore
from shared.database.models import Document, KnowledgeBase
import logging

logger = logging.getLogger(__name__)

class KnowledgeRetriever:
    def __init__(self, config):
        self.config = config
        self.vector_store = VectorStore(config)
        
    async def retrieve(
        self,
        query: str,
        kb_id: Optional[int] = None,
        top_k: int = 5
    ) -> Dict:
        """檢索相關文檔"""
        try:
            # 將查詢轉換為向量
            query_vector = await self._encode_query(query)
            
            # 搜索相似文檔
            results = self.vector_store.search(
                query_vector=query_vector,
                k=top_k
            )
            
            # 如果指定了知識庫ID，過濾結果
            if kb_id is not None:
                results = [
                    r for r in results 
                    if r.get('knowledge_base_id') == kb_id
                ]
            
            return {
                "success": True,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"檢索文檔時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _encode_query(self, query: str) -> np.ndarray:
        """將查詢轉換為向量"""
        # 這裡應該使用實際的文本嵌入模型
        # 目前返回隨機向量作為示例
        return np.random.rand(768).astype('float32')
    
    def add_documents(
        self,
        documents: List[Document],
        kb_id: Optional[int] = None
    ) -> Dict:
        """添加文檔到向量存儲"""
        try:
            # 將文檔轉換為向量
            vectors = []
            docs_data = []
            
            for doc in documents:
                # 這裡應該使用實際的文本嵌入模型
                vector = np.random.rand(768).astype('float32')
                vectors.append(vector)
                
                docs_data.append({
                    'id': doc.id,
                    'title': doc.title,
                    'content': doc.content,
                    'knowledge_base_id': kb_id or doc.knowledge_base_id
                })
            
            # 添加到向量存儲
            success = self.vector_store.add_vectors(
                vectors=np.array(vectors),
                documents=docs_data
            )
            
            if success:
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": "添加向量失敗"
                }
                
        except Exception as e:
            logger.error(f"添加文檔時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_index(self, name: str = "default") -> Dict:
        """保存向量索引"""
        try:
            success = self.vector_store.save(name)
            return {"success": success}
        except Exception as e:
            logger.error(f"保存索引時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_index(self, name: str = "default") -> Dict:
        """加載向量索引"""
        try:
            success = self.vector_store.load(name)
            return {"success": success}
        except Exception as e:
            logger.error(f"加載索引時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 