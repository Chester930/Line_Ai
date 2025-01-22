import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from pydantic import BaseModel, Field, validator
from datetime import datetime

logger = logging.getLogger(__name__)

class VectorStoreConfig(BaseModel):
    """向量存儲配置"""
    model_name: str = Field(
        default="paraphrase-multilingual-MiniLM-L12-v2",
        description="使用的向量模型名稱"
    )
    vector_dir: str = Field(
        default="data/vectors",
        description="向量文件存儲目錄"
    )
    dimension: int = Field(
        default=384,
        description="向量維度"
    )
    
    @validator('vector_dir')
    def create_vector_dir(cls, v):
        os.makedirs(v, exist_ok=True)
        return v

class RetrieverConfig(BaseModel):
    """檢索器配置"""
    top_k: int = Field(
        default=5,
        description="返回的最大文檔數量"
    )
    score_threshold: float = Field(
        default=0.5,
        description="相似度分數閾值"
    )
    rerank_size: int = Field(
        default=10,
        description="重排序的文檔數量"
    )

class ChatManagerConfig(BaseModel):
    """對話管理器配置"""
    max_context_length: int = Field(
        default=2000,
        description="上下文最大長度"
    )
    max_history_turns: int = Field(
        default=10,
        description="歷史對話最大輪數"
    )
    conversation_save_dir: str = Field(
        default="data/conversations",
        description="對話保存目錄"
    )
    
    @validator('conversation_save_dir')
    def create_save_dir(cls, v):
        os.makedirs(v, exist_ok=True)
        return v

class RagConfig(BaseModel):
    """RAG 系統總配置"""
    vector_store: VectorStoreConfig = Field(
        default_factory=VectorStoreConfig,
        description="向量存儲配置"
    )
    retriever: RetrieverConfig = Field(
        default_factory=RetrieverConfig,
        description="檢索器配置"
    )
    chat_manager: ChatManagerConfig = Field(
        default_factory=ChatManagerConfig,
        description="對話管理器配置"
    )
    data_dir: str = Field(
        default="data",
        description="數據根目錄"
    )
    
    @validator('data_dir')
    def create_data_dir(cls, v):
        os.makedirs(v, exist_ok=True)
        return v

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路徑,如果為 None 則使用默認配置
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> RagConfig:
        """加載配置"""
        try:
            if self.config_path and os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
                return RagConfig(**config_dict)
            return RagConfig()
            
        except Exception as e:
            logger.error(f"加載配置失敗: {str(e)}")
            return RagConfig()
    
    def save_config(self, file_path: Optional[str] = None) -> None:
        """
        保存配置
        
        Args:
            file_path: 保存路徑,如果為 None 則使用初始化時的路徑
        """
        try:
            save_path = file_path or self.config_path
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(
                        self.config.dict(),
                        f,
                        ensure_ascii=False,
                        indent=2
                    )
                    
        except Exception as e:
            logger.error(f"保存配置失敗: {str(e)}")
            raise
    
    def update_config(self, config_dict: Dict[str, Any]) -> None:
        """
        更新配置
        
        Args:
            config_dict: 新的配置字典
        """
        try:
            # 創建新的配置對象
            new_config = RagConfig(**{
                **self.config.dict(),
                **config_dict
            })
            
            # 驗證並更新
            self.config = new_config
            
            # 如果有配置文件路徑,則保存
            if self.config_path:
                self.save_config()
                
        except Exception as e:
            logger.error(f"更新配置失敗: {str(e)}")
            raise
    
    def get_component_config(self, component: str) -> BaseModel:
        """
        獲取組件配置
        
        Args:
            component: 組件名稱 (vector_store/retriever/chat_manager)
            
        Returns:
            組件配置對象
        """
        if not hasattr(self.config, component):
            raise ValueError(f"未知的組件名稱: {component}")
        return getattr(self.config, component)
    
    def validate_config(self) -> List[str]:
        """
        驗證配置
        
        Returns:
            錯誤信息列表
        """
        errors = []
        
        try:
            # 驗證向量維度
            if self.config.vector_store.dimension <= 0:
                errors.append("向量維度必須大於 0")
            
            # 驗證檢索參數
            if self.config.retriever.top_k <= 0:
                errors.append("top_k 必須大於 0")
            if not 0 <= self.config.retriever.score_threshold <= 1:
                errors.append("score_threshold 必須在 0 和 1 之間")
            
            # 驗證對話管理參數
            if self.config.chat_manager.max_context_length <= 0:
                errors.append("max_context_length 必須大於 0")
            if self.config.chat_manager.max_history_turns <= 0:
                errors.append("max_history_turns 必須大於 0")
            
            # 驗證目錄權限
            for dir_path in [
                self.config.data_dir,
                self.config.vector_store.vector_dir,
                self.config.chat_manager.conversation_save_dir
            ]:
                if not os.access(dir_path, os.W_OK):
                    errors.append(f"目錄無寫入權限: {dir_path}")
            
        except Exception as e:
            errors.append(f"驗證配置時發生錯誤: {str(e)}")
        
        return errors
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        獲取配置摘要
        
        Returns:
            配置摘要信息
        """
        return {
            "vector_store": {
                "model": self.config.vector_store.model_name,
                "dimension": self.config.vector_store.dimension
            },
            "retriever": {
                "top_k": self.config.retriever.top_k,
                "threshold": self.config.retriever.score_threshold
            },
            "chat_manager": {
                "max_context": self.config.chat_manager.max_context_length,
                "max_turns": self.config.chat_manager.max_history_turns
            },
            "directories": {
                "data": self.config.data_dir,
                "vectors": self.config.vector_store.vector_dir,
                "conversations": self.config.chat_manager.conversation_save_dir
            }
        } 