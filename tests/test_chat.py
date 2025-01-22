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
        },
        "chat": {
            "max_context_length": 2000,
            "max_history_turns": 10
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
    """創建測試文檔"""
    docs = []
    contents = [
        "人工智能是計算機科學的一個重要分支。",
        "機器學習是人工智能的核心技術之一。",
        "深度學習是機器學習中的一種方法。"
    ]
    
    for i, content in enumerate(contents):
        doc_path = test_dir / f"doc_{i}.txt"
        doc_path.write_text(content, encoding="utf-8")
        docs.append(doc_path)
    
    return docs

@pytest.fixture
def uploaded_docs(api_client, test_documents):
    """上傳測試文檔"""
    doc_ids = []
    for doc in test_documents:
        with open(doc, "rb") as f:
            response = api_client.post(
                "/documents/upload",
                files={"file": (doc.name, f, "text/plain")}
            )
        assert response.status_code == 200
        doc_ids.append(response.json()["doc_id"])
    return doc_ids

def test_create_conversation(api_client):
    """測試創建對話"""
    response = api_client.post("/chat/conversations")
    
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["status"] == "success"
    
    return data["conversation_id"]

def test_send_message(api_client, uploaded_docs):
    """測試發送消息"""
    # 創建對話
    conversation_id = test_create_conversation(api_client)
    
    # 發送消息
    message = "什麼是機器學習？"
    response = api_client.post(
        f"/chat/conversations/{conversation_id}/messages",
        json={"message": message}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "response" in data
    assert "relevant_docs" in data
    assert len(data["relevant_docs"]) <= 3

def test_conversation_history(api_client, uploaded_docs):
    """測試對話歷史"""
    # 創建對話
    conversation_id = test_create_conversation(api_client)
    
    # 發送多條消息
    messages = ["什麼是機器學習？", "深度學習是什麼？"]
    for message in messages:
        response = api_client.post(
            f"/chat/conversations/{conversation_id}/messages",
            json={"message": message}
        )
        assert response.status_code == 200
    
    # 獲取歷史記錄
    response = api_client.get(f"/chat/conversations/{conversation_id}/history")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == len(messages) * 2  # 用戶消息和系統回覆
    assert data["conversation_id"] == conversation_id

def test_context_management(api_client, uploaded_docs):
    """測試上下文管理"""
    # 創建對話
    conversation_id = test_create_conversation(api_client)
    
    # 發送相關消息
    messages = [
        "什麼是機器學習？",
        "它和深度學習有什麼關係？",  # 應該能夠理解"它"指的是機器學習
        "這些技術在人工智能中的作用是什麼？"  # 應該能夠理解上下文
    ]
    
    responses = []
    for message in messages:
        response = api_client.post(
            f"/chat/conversations/{conversation_id}/messages",
            json={"message": message}
        )
        assert response.status_code == 200
        responses.append(response.json())
    
    # 檢查回覆的相關性
    assert "機器學習" in responses[0]["response"]
    assert "深度學習" in responses[1]["response"]
    assert "人工智能" in responses[2]["response"]

def test_invalid_conversation_operations(api_client):
    """測試無效的對話操作"""
    # 測試訪問不存在的對話
    response = api_client.get("/chat/conversations/invalid_id/history")
    assert response.status_code == 404
    
    # 測試向不存在的對話發送消息
    response = api_client.post(
        "/chat/conversations/invalid_id/messages",
        json={"message": "test"}
    )
    assert response.status_code == 404
    
    # 測試發送空消息
    conversation_id = test_create_conversation(api_client)
    response = api_client.post(
        f"/chat/conversations/{conversation_id}/messages",
        json={"message": ""}
    )
    assert response.status_code == 422

def test_conversation_clear(api_client, uploaded_docs):
    """測試清除對話"""
    # 創建對話並發送消息
    conversation_id = test_create_conversation(api_client)
    response = api_client.post(
        f"/chat/conversations/{conversation_id}/messages",
        json={"message": "test message"}
    )
    assert response.status_code == 200
    
    # 清除對話
    response = api_client.delete(f"/chat/conversations/{conversation_id}")
    assert response.status_code == 200
    
    # 驗證對話已被清除
    response = api_client.get(f"/chat/conversations/{conversation_id}/history")
    assert response.status_code == 404

def test_conversation_list(api_client):
    """測試對話列表"""
    # 創建多個對話
    conversation_ids = []
    for _ in range(3):
        conversation_id = test_create_conversation(api_client)
        conversation_ids.append(conversation_id)
    
    # 獲取對話列表
    response = api_client.get("/chat/conversations")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["conversations"]) >= 3
    assert all(conv["conversation_id"] in conversation_ids 
              for conv in data["conversations"]) 