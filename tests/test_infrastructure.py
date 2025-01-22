import pytest
import os
from pathlib import Path
from shared.config.config import Config
from shared.ai.vector_store import VectorStore
from shared.utils.file_utils import ensure_directory
from shared.rag.api.rag_api import RagAPI

@pytest.fixture
def test_dir(tmp_path):
    """創建測試目錄"""
    test_dir = tmp_path / "test_rag"
    test_dir.mkdir()
    return test_dir

@pytest.fixture
def config_path(test_dir):
    """創建測試配置文件"""
    config = {
        "vector_store": {
            "dimension": 768,
            "index_type": "L2",
            "data_dir": str(test_dir / "vectors")
        },
        "retriever": {
            "top_k": 3,
            "score_threshold": 0.5
        },
        "chat_manager": {
            "max_history": 10,
            "max_context_length": 2000
        }
    }
    
    config_file = test_dir / "config.json"
    import json
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    return str(config_file)

@pytest.fixture
def config():
    """配置管理器測試夾具"""
    return Config()

@pytest.fixture
def vector_store(config):
    """向量存儲測試夾具"""
    return VectorStore(config)

def test_config_manager_init(config):
    """測試配置管理器初始化"""
    assert config is not None
    assert isinstance(config, Config)
    # 檢查必要的配置項
    assert hasattr(config, 'get')
    assert hasattr(config, 'set')
    
    # 檢查基本配置
    base_path = config.get('BASE_PATH', '')
    assert base_path != ''
    assert Path(base_path).exists()

def test_vector_store_init(vector_store):
    """測試向量存儲初始化"""
    assert vector_store is not None
    assert isinstance(vector_store, VectorStore)
    
    # 檢查向量存儲目錄
    vector_path = vector_store.vector_path
    assert vector_path.exists()
    assert vector_path.is_dir()

@pytest.mark.asyncio
async def test_api_init():
    """測試 API 初始化"""
    api = RagAPI()
    assert api is not None

def test_directory_creation():
    """測試目錄創建"""
    test_dir = Path("test_dir")
    ensure_directory(test_dir)
    assert test_dir.exists()
    assert test_dir.is_dir()
    # 清理
    test_dir.rmdir()

def test_config_validation(config):
    """測試配置驗證"""
    # 測試必要配置項
    required_configs = [
        'BASE_PATH',
        'VECTOR_STORE_PATH',
        'JSON_STORE_PATH',
        'TEMP_PATH'
    ]
    
    for key in required_configs:
        value = config.get(key)
        assert value is not None
        assert value != ''
        assert Path(value).exists()

def test_component_dependencies(config, vector_store):
    """測試組件依賴關係"""
    # 檢查向量存儲是否正確依賴配置
    assert vector_store.config is config
    
    # 檢查向量存儲路徑是否正確設置
    vector_path = Path(config.get('VECTOR_STORE_PATH'))
    assert vector_store.vector_path == vector_path 