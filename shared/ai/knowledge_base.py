from typing import List, Dict, Optional
from shared.utils.vector_store import VectorStore
from shared.database.document_crud import DocumentCRUD

class KnowledgeBase:
    """知識庫管理"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.document_crud = DocumentCRUD()
    
    def query(
        self,
        question: str,
        top_k: int = 3,
        threshold: float = 0.5
    ) -> List[Dict]:
        """查詢知識庫"""
        # 搜索相關文檔
        results = self.vector_store.search(
            query=question,
            top_k=top_k,
            threshold=threshold
        )
        
        # 豐富結果資訊
        enriched_results = []
        for result in results:
            doc = self.document_crud.get_document(result['document_id'])
            enriched_results.append({
                'document': {
                    'id': doc.id,
                    'title': doc.title,
                    'type': doc.file_type
                },
                'content': result['content'],
                'similarity': result['similarity']
            })
        
        return enriched_results
    
    def format_context(self, results: List[Dict]) -> str:
        """格式化上下文資訊"""
        if not results:
            return ""
        
        context = "根據知識庫中的相關資訊：\n\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. 來自文件「{result['document']['title']}」：\n"
            context += f"{result['content']}\n\n"
        
        return context.strip() 