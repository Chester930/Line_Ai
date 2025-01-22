import pytest
from fastapi.testclient import TestClient
import json
from pathlib import Path
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
        }
    }
    
    config_file = test_dir / "config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    return str(config_file)

@pytest.fixture
def api_client(config_path):
    """創建測試客戶端"""
    api = RagAPI(config_path)
    return TestClient(api.app)

@pytest.fixture
def test_documents(test_dir):
    """創建多個測試文檔"""
    docs = []
    contents = [
        "人工智能是計算機科學的一個重要分支。",
        "機器學習是人工智能的核心技術之一。",
        "深度學習是機器學習中的一種方法。",
        "自然語言處理是人工智能的重要應用領域。",
        "計算機視覺是人工智能的另一個重要應用。"
    ]
    
    for i, content in enumerate(contents):
        doc_path = test_dir / f"doc_{i}.txt"
        doc_path.write_text(content, encoding="utf-8")
        docs.append(doc_path)
    
    return docs

@pytest.fixture
def uploaded_docs(api_client, test_documents):
    """上傳測試文檔並返回文檔ID列表"""
    doc_ids = []
    for i, doc in enumerate(test_documents):
        metadata = {
            "title": f"文檔 {i}",
            "category": "AI" if i < 3 else "應用",
            "tags": ["test", f"doc_{i}"]
        }
        
        with open(doc, "rb") as f:
            response = api_client.post(
                "/documents/upload",
                files={"file": (doc.name, f, "text/plain")},
                data={"metadata": json.dumps(metadata)}
            )
        
        assert response.status_code == 200
        doc_ids.append(response.json()["doc_id"])
    
    return doc_ids

def test_basic_search(api_client, uploaded_docs):
    """測試基本搜索功能"""
    response = api_client.post(
        "/search",
        json={
            "query": "人工智能",
            "top_k": 3
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= 3
    assert data["total_results"] > 0
    assert data["processing_time"] >= 0

def test_filtered_search(api_client, uploaded_docs):
    """測試帶過濾條件的搜索"""
    response = api_client.post(
        "/search",
        json={
            "query": "機器學習",
            "filters": {"category": "AI"},
            "top_k": 2
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= 2
    for result in data["results"]:
        assert result["metadata"]["category"] == "AI"

def test_batch_search(api_client, uploaded_docs):
    """測試批量搜索"""
    response = api_client.post(
        "/search/batch",
        json={
            "queries": ["人工智能", "機器學習", "深度學習"],
            "top_k": 2
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    for result in data:
        assert len(result["results"]) <= 2
        assert result["processing_time"] >= 0

def test_search_with_invalid_params(api_client, uploaded_docs):
    """測試無效的搜索參數"""
    # 測試空查詢
    response = api_client.post(
        "/search",
        json={
            "query": "",
            "top_k": 3
        }
    )
    assert response.status_code == 422
    
    # 測試無效的 top_k
    response = api_client.post(
        "/search",
        json={
            "query": "test",
            "top_k": -1
        }
    )
    assert response.status_code == 422
    
    # 測試超出範圍的 top_k
    response = api_client.post(
        "/search",
        json={
            "query": "test",
            "top_k": 101
        }
    )
    assert response.status_code == 422

def test_search_relevance(api_client, uploaded_docs):
    """測試搜索結果相關性"""
    response = api_client.post(
        "/search",
        json={
            "query": "機器學習 人工智能",
            "top_k": 3
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    results = data["results"]
    
    # 檢查第一個結果是否最相關
    assert "機器學習" in results[0]["content"] or "人工智能" in results[0]["content"]
    
    # 檢查分數排序
    scores = [result["score"] for result in results]
    assert scores == sorted(scores, reverse=True)

def test_search_empty_index(api_client):
    """測試空索引的搜索"""
    response = api_client.post(
        "/search",
        json={
            "query": "test",
            "top_k": 3
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 0
    assert data["total_results"] == 0 