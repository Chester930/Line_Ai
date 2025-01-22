import pytest
from fastapi.testclient import TestClient
import os
import json
from pathlib import Path
from shared.rag.api.rag_api import RagAPI

@pytest.fixture
def test_api_dir(tmp_path):
    """創建測試 API 目錄"""
    api_dir = tmp_path / "test_api"
    api_dir.mkdir()
    return api_dir

@pytest.fixture
def api_client(test_api_dir):
    """創建 API 測試客戶端"""
    config_path = str(test_api_dir / "config.json")
    api = RagAPI(config_path)
    return TestClient(api.app)

def test_health_check(api_client):
    """測試健康檢查"""
    response = api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "components" in data

def test_document_upload(api_client, test_api_dir):
    """測試文檔上傳"""
    # 創建測試文件
    test_file = test_api_dir / "test.txt"
    test_content = "這是一個測試文檔"
    test_file.write_text(test_content)
    
    # 上傳文件
    with open(test_file, "rb") as f:
        response = api_client.post(
            "/documents/upload",
            files={"file": ("test.txt", f, "text/plain")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "test.txt"
    assert data["status"] == "success"
    assert "doc_id" in data
    assert "content_hash" in data

def test_search(api_client):
    """測試搜索"""
    # 發送搜索請求
    response = api_client.post(
        "/search",
        json={
            "query": "測試查詢",
            "filters": {"type": "test"},
            "top_k": 5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "metadata" in data
    assert data["metadata"]["query"] == "測試查詢"

def test_chat(api_client):
    """測試對話"""
    # 發送對話請求
    response = api_client.post(
        "/chat",
        json={
            "conversation_id": "test_conv",
            "message": "你好",
            "metadata": {"test": True}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == "test_conv"
    assert "response" in data
    assert "context" in data

def test_conversation_history(api_client):
    """測試獲取對話歷史"""
    # 創建對話
    api_client.post(
        "/chat",
        json={
            "conversation_id": "test_conv",
            "message": "測試消息"
        }
    )
    
    # 獲取歷史
    response = api_client.get("/conversations/test_conv/history")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert len(data["history"]) > 0

def test_delete_conversation(api_client):
    """測試刪除對話"""
    # 創建對話
    api_client.post(
        "/chat",
        json={
            "conversation_id": "test_conv",
            "message": "測試消息"
        }
    )
    
    # 刪除對話
    response = api_client.delete("/conversations/test_conv")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # 驗證刪除
    response = api_client.get("/conversations/test_conv/history")
    data = response.json()
    assert len(data["history"]) == 0

def test_config_management(api_client):
    """測試配置管理"""
    # 獲取配置
    response = api_client.get("/config")
    assert response.status_code == 200
    original_config = response.json()
    
    # 更新配置
    new_config = {
        "retriever": {
            "top_k": 10,
            "score_threshold": 0.7
        }
    }
    response = api_client.post("/config", json={"config": new_config})
    assert response.status_code == 200
    
    # 驗證更新
    response = api_client.get("/config")
    updated_config = response.json()
    assert updated_config["retriever"]["top_k"] == 10
    assert updated_config["retriever"]["threshold"] == 0.7

def test_invalid_config_update(api_client):
    """測試無效配置更新"""
    # 嘗試設置無效配置
    invalid_config = {
        "vector_store": {
            "dimension": -1
        }
    }
    response = api_client.post("/config", json={"config": invalid_config})
    assert response.status_code == 500
    assert "向量維度" in response.json()["detail"]

def test_error_handling(api_client):
    """測試錯誤處理"""
    # 測試無效的對話 ID
    response = api_client.get("/conversations/invalid_id/history")
    assert response.status_code == 200  # 返回空歷史而不是錯誤
    
    # 測試無效的搜索請求
    response = api_client.post(
        "/search",
        json={
            "query": "",  # 空查詢
            "top_k": -1  # 無效的 top_k
        }
    )
    assert response.status_code == 500 