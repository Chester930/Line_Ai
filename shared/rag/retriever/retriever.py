import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
import numpy as np
from ..vector.vector_store import VectorStore

logger = logging.getLogger(__name__)

class Retriever:
    """文檔檢索器"""
    
    def __init__(self,
                 vector_store: VectorStore,
                 top_k: int = 5,
                 score_threshold: float = 0.5):
        """
        初始化檢索器
        
        Args:
            vector_store: 向量存儲實例
            top_k: 返回的最大文檔數量
            score_threshold: 相似度分數閾值
        """
        self.vector_store = vector_store
        self.top_k = top_k
        self.score_threshold = score_threshold
        
        # 初始化檢索歷史
        self.retrieval_history = []
    
    def retrieve(self, 
                query: str,
                filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        檢索相關文檔
        
        Args:
            query: 查詢文本
            filters: 過濾條件
            
        Returns:
            檢索結果列表
        """
        try:
            # 向量搜索
            results = self.vector_store.search(query, self.top_k)
            
            # 應用過濾條件
            if filters:
                results = self._apply_filters(results, filters)
            
            # 應用分數閾值
            results = [r for r in results if r['score'] >= self.score_threshold]
            
            # 記錄檢索歷史
            self._record_retrieval(query, results)
            
            return results
            
        except Exception as e:
            logger.error(f"檢索失敗: {str(e)}")
            raise
    
    def retrieve_with_rerank(self,
                           query: str,
                           filters: Optional[Dict[str, Any]] = None,
                           rerank_size: int = 10) -> List[Dict[str, Any]]:
        """
        檢索並重新排序文檔
        
        Args:
            query: 查詢文本
            filters: 過濾條件
            rerank_size: 重排序的文檔數量
            
        Returns:
            重新排序後的檢索結果
        """
        try:
            # 獲取更多候選文檔
            results = self.vector_store.search(query, rerank_size)
            
            # 應用過濾條件
            if filters:
                results = self._apply_filters(results, filters)
            
            # 重新排序
            reranked_results = self._rerank_results(query, results)
            
            # 取 top_k 個結果
            reranked_results = reranked_results[:self.top_k]
            
            # 應用分數閾值
            reranked_results = [r for r in reranked_results if r['score'] >= self.score_threshold]
            
            # 記錄檢索歷史
            self._record_retrieval(query, reranked_results, reranked=True)
            
            return reranked_results
            
        except Exception as e:
            logger.error(f"檢索重排序失敗: {str(e)}")
            raise
    
    def _apply_filters(self,
                      results: List[Dict[str, Any]],
                      filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """應用過濾條件"""
        filtered_results = []
        
        for result in results:
            metadata = result['metadata']
            match = True
            
            # 檢查每個過濾條件
            for key, value in filters.items():
                if key not in metadata or metadata[key] != value:
                    match = False
                    break
            
            if match:
                filtered_results.append(result)
        
        return filtered_results
    
    def _rerank_results(self,
                       query: str,
                       results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """重新排序結果"""
        # 這裡可以實現更複雜的重排序邏輯
        # 目前使用簡單的分數排序
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def _record_retrieval(self,
                         query: str,
                         results: List[Dict[str, Any]],
                         reranked: bool = False) -> None:
        """記錄檢索歷史"""
        record = {
            'timestamp': datetime.utcnow().isoformat(),
            'query': query,
            'results': results,
            'reranked': reranked
        }
        self.retrieval_history.append(record)
        
        # 保持歷史記錄在合理範圍內
        if len(self.retrieval_history) > 1000:
            self.retrieval_history = self.retrieval_history[-1000:]
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """獲取檢索統計信息"""
        stats = {
            'total_queries': len(self.retrieval_history),
            'avg_results_per_query': 0,
            'reranked_queries': 0,
            'avg_score': 0
        }
        
        if stats['total_queries'] > 0:
            # 計算平均結果數
            total_results = sum(len(h['results']) for h in self.retrieval_history)
            stats['avg_results_per_query'] = total_results / stats['total_queries']
            
            # 計算重排序查詢數
            stats['reranked_queries'] = sum(1 for h in self.retrieval_history if h['reranked'])
            
            # 計算平均分數
            total_scores = sum(
                result['score']
                for h in self.retrieval_history
                for result in h['results']
            )
            total_all_results = sum(len(h['results']) for h in self.retrieval_history)
            if total_all_results > 0:
                stats['avg_score'] = total_scores / total_all_results
        
        return stats 