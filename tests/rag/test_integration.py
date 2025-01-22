import pytest
import os
import shutil
from datetime import datetime
from shared.rag.vector.vector_store import VectorStore
from shared.rag.retriever.retriever import Retriever
from shared.rag.chat.chat_manager import ChatManager

@pytest.fixture
def test_data_dir(tmp_path):
    """創建測試數據目錄"""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    yield test_dir
    # 清理測試數據
    shutil.rmtree(test_dir)

@pytest.fixture
def vector_store(test_data_dir):
    """創建向量存儲實例"""
    store = VectorStore(
        vector_dir=str(test_data_dir / "vectors"),
        dimension=384
    )
    return store

@pytest.fixture
def retriever(vector_store):
    """創建檢索器實例"""
    return Retriever(
        vector_store=vector_store,
        top_k=3,
        score_threshold=0.5
    )

@pytest.fixture
def chat_manager(retriever):
    """創建對話管理器實例"""
    return ChatManager(
        retriever=retriever,
        max_context_length=1000,
        max_history_turns=5
    )

def test_document_processing_and_retrieval(vector_store):
    """測試文檔處理和檢索"""
    # 添加測試文檔
    docs = [
        {
            "id": "doc1",
            "content": "人工智能是計算機科學的一個重要分支",
            "metadata": {"type": "article", "topic": "AI"}
        },
        {
            "id": "doc2",
            "content": "機器學習是人工智能的核心技術之一",
            "metadata": {"type": "article", "topic": "ML"}
        },
        {
            "id": "doc3",
            "content": "深度學習在圖像識別領域取得了重大突破",
            "metadata": {"type": "article", "topic": "DL"}
        }
    ]
    
    for doc in docs:
        vector_store.add_document(doc['id'], doc['content'], doc['metadata'])
    
    # 測試檢索
    query = "人工智能的應用"
    results = vector_store.search(query, top_k=2)
    
    assert len(results) > 0
    assert results[0]['score'] > 0
    assert 'metadata' in results[0]

def test_retrieval_with_filters(vector_store, retriever):
    """測試帶過濾條件的檢索"""
    # 添加測試文檔
    docs = [
        {
            "id": "doc1",
            "content": "Python是一種流行的程式語言",
            "metadata": {"type": "tutorial", "language": "Python"}
        },
        {
            "id": "doc2",
            "content": "Java在企業應用開發中廣泛使用",
            "metadata": {"type": "tutorial", "language": "Java"}
        }
    ]
    
    for doc in docs:
        vector_store.add_document(doc['id'], doc['content'], doc['metadata'])
    
    # 測試帶過濾條件的檢索
    query = "程式語言"
    filters = {"language": "Python"}
    results = retriever.retrieve(query, filters)
    
    assert len(results) > 0
    assert all(r['metadata']['language'] == 'Python' for r in results)

def test_chat_context_management(chat_manager):
    """測試對話上下文管理"""
    conversation_id = "test_conv_1"
    
    # 創建對話
    chat_manager.create_conversation(conversation_id)
    
    # 添加消息
    chat_manager.add_message(
        conversation_id=conversation_id,
        role="user",
        content="什麼是機器學習？"
    )
    
    chat_manager.add_message(
        conversation_id=conversation_id,
        role="assistant",
        content="機器學習是一種讓計算機能夠從數據中學習的技術。"
    )
    
    # 獲取上下文
    context = chat_manager.get_context(conversation_id)
    
    assert 'history' in context
    assert len(context['history']) == 2
    assert context['history'][0]['role'] == 'user'

def test_end_to_end_conversation(vector_store, retriever, chat_manager):
    """測試端到端的對話流程"""
    # 準備知識庫
    docs = [
        {
            "id": "kb1",
            "content": "機器學習是一種通過數據訓練來提高系統性能的方法",
            "metadata": {"category": "AI"}
        },
        {
            "id": "kb2",
            "content": "深度學習是機器學習的一個子領域，使用多層神經網絡進行學習",
            "metadata": {"category": "AI"}
        }
    ]
    
    for doc in docs:
        vector_store.add_document(doc['id'], doc['content'], doc['metadata'])
    
    # 創建對話
    conversation_id = "test_conv_2"
    chat_manager.create_conversation(conversation_id)
    
    # 模擬對話流程
    user_messages = [
        "什麼是機器學習？",
        "深度學習和機器學習有什麼關係？"
    ]
    
    for msg in user_messages:
        # 添加用戶消息
        chat_manager.add_message(
            conversation_id=conversation_id,
            role="user",
            content=msg
        )
        
        # 獲取上下文
        context = chat_manager.get_context(conversation_id)
        
        # 驗證上下文
        assert 'documents' in context
        assert 'history' in context
        assert len(context['documents']) > 0
        
        # 模擬助手回覆
        chat_manager.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content="基於檢索的回覆"
        )
    
    # 獲取對話統計
    stats = chat_manager.get_conversation_stats(conversation_id)
    
    assert stats['total_messages'] == 4
    assert stats['user_messages'] == 2
    assert stats['assistant_messages'] == 2

def test_persistence(test_data_dir, chat_manager):
    """測試對話持久化"""
    conversation_id = "test_conv_3"
    
    # 創建並添加消息
    chat_manager.create_conversation(conversation_id)
    chat_manager.add_message(
        conversation_id=conversation_id,
        role="user",
        content="測試消息"
    )
    
    # 保存對話
    save_path = str(test_data_dir / "conversations.json")
    chat_manager.save_conversations(save_path)
    
    # 創建新的管理器並加載
    new_chat_manager = ChatManager(
        retriever=chat_manager.retriever,
        max_context_length=1000,
        max_history_turns=5
    )
    new_chat_manager.load_conversations(save_path)
    
    # 驗證加載的對話
    loaded_conv = new_chat_manager.get_context(conversation_id)
    assert len(loaded_conv['history']) == 1
    assert loaded_conv['history'][0]['content'] == "測試消息" 