from pathlib import Path
import numpy as np
import faiss
import pickle
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, config):
        self.config = config
        self.vector_path = Path(config.get('VECTOR_STORE_PATH'))
        self.vector_path.mkdir(parents=True, exist_ok=True)
        self.index = None
        self.document_lookup = {}
        
    def create_index(self, dimension: int = 768):
        """創建新的向量索引"""
        try:
            self.index = faiss.IndexFlatL2(dimension)
            self.document_lookup = {}
            return True
        except Exception as e:
            logger.error(f"創建索引時發生錯誤：{str(e)}")
            return False
    
    def add_vectors(self, vectors: np.ndarray, documents: List[Dict]):
        """添加向量到索引"""
        try:
            if self.index is None:
                self.create_index(vectors.shape[1])
            
            # 獲取當前索引大小作為起始ID
            start_id = self.index.ntotal
            
            # 添加向量到索引
            self.index.add(vectors)
            
            # 更新文檔查找表
            for i, doc in enumerate(documents):
                self.document_lookup[start_id + i] = doc
                
            return True
        except Exception as e:
            logger.error(f"添加向量時發生錯誤：{str(e)}")
            return False
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict]:
        """搜索最相似的向量"""
        try:
            if self.index is None:
                return []
            
            # 執行搜索
            distances, indices = self.index.search(query_vector.reshape(1, -1), k)
            
            # 獲取對應的文檔
            results = []
            for i, idx in enumerate(indices[0]):
                if idx in self.document_lookup:
                    doc = self.document_lookup[idx].copy()
                    doc['distance'] = float(distances[0][i])
                    results.append(doc)
                    
            return results
        except Exception as e:
            logger.error(f"搜索時發生錯誤：{str(e)}")
            return []
    
    def save(self, name: str):
        """保存索引和文檔查找表"""
        try:
            if self.index is None:
                return False
                
            # 保存索引
            index_path = self.vector_path / f"{name}.index"
            faiss.write_index(self.index, str(index_path))
            
            # 保存文檔查找表
            lookup_path = self.vector_path / f"{name}.lookup"
            with open(lookup_path, 'wb') as f:
                pickle.dump(self.document_lookup, f)
                
            return True
        except Exception as e:
            logger.error(f"保存索引時發生錯誤：{str(e)}")
            return False
    
    def load(self, name: str):
        """加載索引和文檔查找表"""
        try:
            # 加載索引
            index_path = self.vector_path / f"{name}.index"
            if not index_path.exists():
                return False
            self.index = faiss.read_index(str(index_path))
            
            # 加載文檔查找表
            lookup_path = self.vector_path / f"{name}.lookup"
            if not lookup_path.exists():
                return False
            with open(lookup_path, 'rb') as f:
                self.document_lookup = pickle.load(f)
                
            return True
        except Exception as e:
            logger.error(f"加載索引時發生錯誤：{str(e)}")
            return False 