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
def test_document(test_dir):
    """創建測試文檔"""
    doc_path = test_dir / "test.txt"
    content = "這是一個測試文檔的內容。用於測試文檔管理功能。"
    doc_path.write_text(content, encoding="utf-8")
    return doc_path

def test_document_upload(api_client, test_document):
    """測試文檔上傳"""
    # 準備文件和元數據
    metadata = {
        "description": "測試文檔",
        "tags": ["test", "document"]
    }
    
    # 上傳文件
    with open(test_document, "rb") as f:
        response = api_client.post(
            "/documents/upload",
            files={"file": ("test.txt", f, "text/plain")},
            data={"metadata": json.dumps(metadata)}
        )
    
    # 驗證響應
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["file_name"] == "test.txt"
    assert "doc_id" in data
    assert "content_hash" in data
    
    # 保存文檔ID用於後續測試
    return data["doc_id"]

def test_document_list(api_client, test_document):
    """測試文檔列表"""
    # 先上傳一個文檔
    doc_id = test_document_upload(api_client, test_document)
    
    # 獲取文檔列表
    response = api_client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    
    # 驗證響應
    assert "documents" in data
    assert "total" in data
    assert data["total"] > 0
    assert any(doc["doc_id"] == doc_id for doc in data["documents"])

def test_document_update(api_client, test_document):
    """測試文檔更新"""
    # 先上傳一個文檔
    doc_id = test_document_upload(api_client, test_document)
    
    # 更新文檔
    update_data = {
        "content": "這是更新後的文檔內容。",
        "metadata": {
            "description": "更新後的測試文檔",
            "tags": ["updated", "test"]
        }
    }
    
    response = api_client.put(
        f"/documents/{doc_id}",
        json=update_data
    )
    
    # 驗證響應
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["doc_id"] == doc_id
    assert data["metadata"]["description"] == "更新後的測試文檔"

def test_document_metadata_update(api_client, test_document):
    """測試文檔元數據更新"""
    # 先上傳一個文檔
    doc_id = test_document_upload(api_client, test_document)
    
    # 更新元數據
    metadata = {
        "new_field": "新字段",
        "tags": ["metadata", "updated"]
    }
    
    response = api_client.patch(
        f"/documents/{doc_id}/metadata",
        json=metadata
    )
    
    # 驗證響應
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["metadata"]["new_field"] == "新字段"
    assert "updated_at" in data["metadata"]

def test_document_delete(api_client, test_document):
    """測試文檔刪除"""
    # 先上傳一個文檔
    doc_id = test_document_upload(api_client, test_document)
    
    # 刪除文檔
    response = api_client.delete(f"/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # 驗證文檔已被刪除
    response = api_client.get("/documents")
    data = response.json()
    assert not any(doc["doc_id"] == doc_id for doc in data["documents"])

def test_document_reindex(api_client, test_document):
    """測試文檔重新索引"""
    # 先上傳一個文檔
    test_document_upload(api_client, test_document)
    
    # 重建索引
    response = api_client.post("/documents/reindex")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "total_docs" in data
    assert "processing_time" in data

def test_invalid_document_operations(api_client):
    """測試無效的文檔操作"""
    # 測試上傳無效文件類型
    with open(__file__, "rb") as f:
        response = api_client.post(
            "/documents/upload",
            files={"file": ("test.invalid", f, "application/octet-stream")}
        )
    assert response.status_code == 400
    
    # 測試更新不存在的文檔
    response = api_client.put(
        "/documents/non_existent_id",
        json={"content": "test"}
    )
    assert response.status_code == 404
    
    # 測試刪除不存在的文檔
    response = api_client.delete("/documents/non_existent_id")
    assert response.status_code == 404 