import pytest
from shared.config.config import Config
from shared.ai.cag import CAGSystem
from shared.ai.rag.retriever import KnowledgeRetriever
from shared.database.models import KnowledgeBase, Document

@pytest.fixture
def config():
    """配置管理器測試夾具"""
    return Config()

@pytest.fixture
def cag_system(config):
    """CAG 系統測試夾具"""
    return CAGSystem(config)

@pytest.fixture
def knowledge_retriever(config):
    """知識檢索器測試夾具"""
    return KnowledgeRetriever(config)

@pytest.fixture
def test_knowledge_base():
    """測試用知識庫"""
    return KnowledgeBase(
        name="測試知識庫",
        description="用於測試的知識庫"
    )

@pytest.fixture
def test_document():
    """測試用文檔"""
    return Document(
        title="測試文檔",
        content="這是一個測試文檔的內容。",
        doc_metadata={"type": "test"}
    ) 