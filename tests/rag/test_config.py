import pytest
import os
import json
from pathlib import Path
from shared.rag.config.config_manager import (
    ConfigManager,
    VectorStoreConfig,
    RetrieverConfig,
    ChatManagerConfig,
    RagConfig
)

@pytest.fixture
def test_config_dir(tmp_path):
    """創建測試配置目錄"""
    config_dir = tmp_path / "test_config"
    config_dir.mkdir()
    return config_dir

@pytest.fixture
def config_manager(test_config_dir):
    """創建配置管理器實例"""
    config_path = str(test_config_dir / "config.json")
    return ConfigManager(config_path)

def test_default_config(config_manager):
    """測試默認配置"""
    # 驗證默認值
    assert config_manager.config.vector_store.model_name == "paraphrase-multilingual-MiniLM-L12-v2"
    assert config_manager.config.vector_store.dimension == 384
    assert config_manager.config.retriever.top_k == 5
    assert config_manager.config.chat_manager.max_history_turns == 10

def test_save_load_config(test_config_dir, config_manager):
    """測試配置的保存和加載"""
    # 修改配置
    config_manager.update_config({
        "vector_store": {
            "dimension": 512
        },
        "retriever": {
            "top_k": 10
        }
    })
    
    # 保存配置
    config_path = str(test_config_dir / "test_save.json")
    config_manager.save_config(config_path)
    
    # 加載配置
    new_manager = ConfigManager(config_path)
    
    # 驗證加載的配置
    assert new_manager.config.vector_store.dimension == 512
    assert new_manager.config.retriever.top_k == 10

def test_component_config(config_manager):
    """測試獲取組件配置"""
    # 獲取向量存儲配置
    vector_config = config_manager.get_component_config("vector_store")
    assert isinstance(vector_config, VectorStoreConfig)
    assert vector_config.dimension == 384
    
    # 獲取檢索器配置
    retriever_config = config_manager.get_component_config("retriever")
    assert isinstance(retriever_config, RetrieverConfig)
    assert retriever_config.top_k == 5
    
    # 獲取對話管理器配置
    chat_config = config_manager.get_component_config("chat_manager")
    assert isinstance(chat_config, ChatManagerConfig)
    assert chat_config.max_history_turns == 10

def test_config_validation(config_manager):
    """測試配置驗證"""
    # 設置無效配置
    config_manager.update_config({
        "vector_store": {
            "dimension": -1
        },
        "retriever": {
            "score_threshold": 2.0
        }
    })
    
    # 驗證配置
    errors = config_manager.validate_config()
    
    # 檢查錯誤信息
    assert len(errors) >= 2
    assert any("向量維度" in error for error in errors)
    assert any("score_threshold" in error for error in errors)

def test_config_summary(config_manager):
    """測試配置摘要"""
    summary = config_manager.get_config_summary()
    
    # 驗證摘要結構
    assert "vector_store" in summary
    assert "retriever" in summary
    assert "chat_manager" in summary
    assert "directories" in summary
    
    # 驗證摘要內容
    assert summary["vector_store"]["dimension"] == 384
    assert summary["retriever"]["top_k"] == 5
    assert summary["chat_manager"]["max_turns"] == 10

def test_directory_creation(test_config_dir):
    """測試目錄創建"""
    # 創建新的配置
    config = RagConfig(
        data_dir=str(test_config_dir / "data"),
        vector_store=VectorStoreConfig(
            vector_dir=str(test_config_dir / "vectors")
        ),
        chat_manager=ChatManagerConfig(
            conversation_save_dir=str(test_config_dir / "conversations")
        )
    )
    
    # 驗證目錄創建
    assert os.path.exists(config.data_dir)
    assert os.path.exists(config.vector_store.vector_dir)
    assert os.path.exists(config.chat_manager.conversation_save_dir)

def test_config_update(config_manager):
    """測試配置更新"""
    # 初始配置
    assert config_manager.config.retriever.top_k == 5
    
    # 更新配置
    config_manager.update_config({
        "retriever": {
            "top_k": 20,
            "score_threshold": 0.7
        }
    })
    
    # 驗證更新
    assert config_manager.config.retriever.top_k == 20
    assert config_manager.config.retriever.score_threshold == 0.7
    
    # 驗證其他配置保持不變
    assert config_manager.config.vector_store.dimension == 384 