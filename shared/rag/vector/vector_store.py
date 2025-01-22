import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
from pathlib import Path
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class VectorStore:
    """向量存儲管理器"""
    
    def __init__(self, 
                 model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
                 vector_dir: str = "data/vectors",
                 dimension: int = 384):
        """
        初始化向量存儲
        
        Args:
            model_name: 使用的向量模型名稱
            vector_dir: 向量文件存儲目錄
            dimension: 向量維度
        """
        self.model = SentenceTransformer(model_name)
        self.vector_dir = vector_dir
        self.dimension = dimension
        
        # 創建向量存儲目錄
        os.makedirs(vector_dir, exist_ok=True)
        
        # 初始化 FAISS 索引
        self.index = faiss.IndexFlatL2(dimension)
        
        # 初始化文檔映射
        self.doc_mapping = {}
        
        # 加載現有向量
        self._load_existing_vectors()
    
    def add_document(self, 
                    doc_id: str,
                    content: str,
                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        添加文檔到向量存儲
        
        Args:
            doc_id: 文檔唯一標識
            content: 文檔內容
            metadata: 文檔元數據
        """
        try:
            # 生成文檔向量
            vector = self.model.encode(content)
            
            # 添加到 FAISS 索引
            self.index.add(np.array([vector], dtype=np.float32))
            
            # 更新文檔映射
            doc_info = {
                'id': doc_id,
                'vector_id': self.index.ntotal - 1,
                'metadata': metadata or {},
                'added_at': datetime.utcnow().isoformat()
            }
            self.doc_mapping[doc_id] = doc_info
            
            # 保存更新
            self._save_state()
            
            logger.info(f"成功添加文檔: {doc_id}")
            
        except Exception as e:
            logger.error(f"添加文檔失敗 {doc_id}: {str(e)}")
            raise
    
    def search(self, 
               query: str, 
               top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索相似文檔
        
        Args:
            query: 查詢文本
            top_k: 返回結果數量
            
        Returns:
            相似文檔列表
        """
        try:
            # 生成查詢向量
            query_vector = self.model.encode(query)
            
            # 搜索相似向量
            distances, indices = self.index.search(
                np.array([query_vector], dtype=np.float32), 
                top_k
            )
            
            # 整理搜索結果
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                # 查找對應的文檔信息
                doc_info = None
                for doc_id, info in self.doc_mapping.items():
                    if info['vector_id'] == idx:
                        doc_info = info
                        break
                
                if doc_info:
                    results.append({
                        'rank': i + 1,
                        'score': float(1 / (1 + distance)),  # 將距離轉換為相似度分數
                        'doc_id': doc_info['id'],
                        'metadata': doc_info['metadata']
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"搜索失敗: {str(e)}")
            raise
    
    def delete_document(self, doc_id: str) -> bool:
        """
        刪除文檔
        
        Args:
            doc_id: 文檔唯一標識
            
        Returns:
            是否刪除成功
        """
        try:
            if doc_id not in self.doc_mapping:
                return False
            
            # 獲取向量 ID
            vector_id = self.doc_mapping[doc_id]['vector_id']
            
            # 從 FAISS 索引中移除
            # 注意: FAISS 不支持直接刪除,需要重建索引
            vectors = []
            for i in range(self.index.ntotal):
                if i != vector_id:
                    vector = self.index.reconstruct(i)
                    vectors.append(vector)
            
            # 重建索引
            self.index = faiss.IndexFlatL2(self.dimension)
            if vectors:
                self.index.add(np.array(vectors, dtype=np.float32))
            
            # 更新文檔映射
            del self.doc_mapping[doc_id]
            
            # 更新其他文檔的向量 ID
            for info in self.doc_mapping.values():
                if info['vector_id'] > vector_id:
                    info['vector_id'] -= 1
            
            # 保存更新
            self._save_state()
            
            logger.info(f"成功刪除文檔: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"刪除文檔失敗 {doc_id}: {str(e)}")
            raise
    
    def _save_state(self) -> None:
        """保存當前狀態"""
        # 保存 FAISS 索引
        index_path = os.path.join(self.vector_dir, 'vectors.index')
        faiss.write_index(self.index, index_path)
        
        # 保存文檔映射
        mapping_path = os.path.join(self.vector_dir, 'mapping.json')
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(self.doc_mapping, f, ensure_ascii=False, indent=2)
    
    def _load_existing_vectors(self) -> None:
        """加載現有向量數據"""
        try:
            # 加載 FAISS 索引
            index_path = os.path.join(self.vector_dir, 'vectors.index')
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
            
            # 加載文檔映射
            mapping_path = os.path.join(self.vector_dir, 'mapping.json')
            if os.path.exists(mapping_path):
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    self.doc_mapping = json.load(f)
                    
            logger.info(f"成功加載現有向量,共 {self.index.ntotal} 個向量")
            
        except Exception as e:
            logger.error(f"加載向量數據失敗: {str(e)}")
            # 如果加載失敗,使用新的索引
            self.index = faiss.IndexFlatL2(self.dimension)
            self.doc_mapping = {} 