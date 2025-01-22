import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Body, Query, Path
from pydantic import BaseModel, Field, validator
from ..config.config_manager import ConfigManager
from ..vector.vector_store import VectorStore
from ..retriever.retriever import Retriever
from ..chat.chat_manager import ChatManager

logger = logging.getLogger(__name__)

# API 請求/響應模型
class DocumentUploadResponse(BaseModel):
    """文檔上傳響應"""
    doc_id: str
    file_name: str
    content_hash: str
    status: str
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SearchRequest(BaseModel):
    """搜索請求"""
    query: str = Field(..., min_length=1)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    top_k: Optional[int] = Field(default=5, ge=1, le=100)
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('查詢不能為空')
        return v.strip()

class SearchResponse(BaseModel):
    """搜索響應"""
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    total_results: int
    processing_time: float

class ChatRequest(BaseModel):
    """對話請求"""
    conversation_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('消息不能為空')
        return v.strip()

class ChatResponse(BaseModel):
    """對話響應"""
    conversation_id: str
    response: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    processing_time: float

class ConfigUpdateRequest(BaseModel):
    """配置更新請求"""
    config: Dict[str, Any]
    
    @validator('config')
    def validate_config(cls, v):
        if not v:
            raise ValueError('配置不能為空')
        return v

# 添加新的請求/響應模型
class DocumentListResponse(BaseModel):
    """文檔列表響應"""
    documents: List[Dict[str, Any]]
    total: int

class DocumentDeleteResponse(BaseModel):
    """文檔刪除響應"""
    status: str
    doc_id: str

class BatchSearchRequest(BaseModel):
    """批量搜索請求"""
    queries: List[str] = Field(..., min_items=1, max_items=10)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    top_k: Optional[int] = Field(default=5, ge=1, le=100)

class DocumentUpdateRequest(BaseModel):
    """文檔更新請求"""
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('content')
    def validate_content(cls, v):
        if v is not None and not v.strip():
            raise ValueError('內容不能為空')
        return v.strip() if v else None

class DocumentUpdateResponse(BaseModel):
    """文檔更新響應"""
    doc_id: str
    status: str
    content_hash: str
    timestamp: str
    metadata: Dict[str, Any]

# API 實現
class RagAPI:
    """RAG 系統 API"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化 API
        
        Args:
            config_path: 配置文件路徑
        """
        try:
            # 初始化組件
            self.config_manager = ConfigManager(config_path)
            self.vector_store = VectorStore(**self.config_manager.get_component_config("vector_store").dict())
            self.retriever = Retriever(
                vector_store=self.vector_store,
                **self.config_manager.get_component_config("retriever").dict()
            )
            self.chat_manager = ChatManager(
                retriever=self.retriever,
                **self.config_manager.get_component_config("chat_manager").dict()
            )
            
            # 創建 FastAPI 應用
            self.app = FastAPI(
                title="RAG System API",
                description="基於檢索增強的對話系統 API",
                version="1.0.0"
            )
            
            # 註冊路由
            self._register_routes()
            
        except Exception as e:
            logger.error(f"API 初始化失敗: {str(e)}")
            raise
    
    def _register_routes(self):
        """註冊 API 路由"""
        
        @self.app.post("/documents/upload", response_model=DocumentUploadResponse)
        async def upload_document(
            file: UploadFile = File(...),
            metadata: Optional[Dict[str, Any]] = Body(default=None)
        ):
            """上傳文檔"""
            start_time = datetime.utcnow()
            try:
                # 驗證文件大小
                content = await file.read()
                if len(content) > 10 * 1024 * 1024:  # 10MB 限制
                    raise HTTPException(status_code=400, detail="文件大小超過限制")
                
                # 驗證文件類型
                allowed_types = ["text/plain", "application/pdf", "application/msword"]
                if file.content_type not in allowed_types:
                    raise HTTPException(status_code=400, detail="不支持的文件類型")
                
                # 添加到向量存儲
                doc_id = f"doc_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                doc_metadata = {
                    "file_name": file.filename,
                    "content_type": file.content_type,
                    "size": len(content),
                    "upload_time": start_time.isoformat()
                }
                if metadata:
                    doc_metadata.update(metadata)
                
                self.vector_store.add_document(
                    doc_id=doc_id,
                    content=content.decode('utf-8'),
                    metadata=doc_metadata
                )
                
                return {
                    "doc_id": doc_id,
                    "file_name": file.filename,
                    "content_hash": self.vector_store.doc_mapping[doc_id]['content_hash'],
                    "status": "success",
                    "timestamp": start_time.isoformat(),
                    "metadata": doc_metadata
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"上傳文檔失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"處理文檔失敗: {str(e)}")
        
        @self.app.post("/search", response_model=SearchResponse)
        async def search(request: SearchRequest):
            """搜索文檔"""
            start_time = datetime.utcnow()
            try:
                # 執行搜索
                results = self.retriever.retrieve(
                    query=request.query,
                    filters=request.filters,
                    top_k=request.top_k
                )
                
                end_time = datetime.utcnow()
                processing_time = (end_time - start_time).total_seconds()
                
                return {
                    "results": results,
                    "metadata": {
                        "query": request.query,
                        "filters": request.filters,
                        "timestamp": start_time.isoformat()
                    },
                    "total_results": len(results),
                    "processing_time": processing_time
                }
                
            except Exception as e:
                logger.error(f"搜索失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"搜索失敗: {str(e)}")
        
        @self.app.post("/chat", response_model=ChatResponse)
        async def chat(request: ChatRequest):
            """對話"""
            start_time = datetime.utcnow()
            try:
                # 添加用戶消息
                self.chat_manager.add_message(
                    conversation_id=request.conversation_id,
                    role="user",
                    content=request.message,
                    metadata=request.metadata
                )
                
                # 獲取上下文
                context = self.chat_manager.get_context(request.conversation_id)
                
                # 檢索相關文檔
                relevant_docs = self.retriever.retrieve(
                    query=request.message,
                    top_k=3  # 獲取前3個最相關的文檔
                )
                
                # 構建提示詞
                prompt = self._build_chat_prompt(
                    query=request.message,
                    context=context,
                    relevant_docs=relevant_docs
                )
                
                # 生成回覆
                response = self._generate_response(prompt)
                
                # 添加助手回覆
                self.chat_manager.add_message(
                    conversation_id=request.conversation_id,
                    role="assistant",
                    content=response,
                    metadata={
                        "relevant_docs": [doc["doc_id"] for doc in relevant_docs],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                end_time = datetime.utcnow()
                processing_time = (end_time - start_time).total_seconds()
                
                return {
                    "conversation_id": request.conversation_id,
                    "response": response,
                    "context": context,
                    "metadata": {
                        "timestamp": start_time.isoformat(),
                        "user_message": request.message,
                        "relevant_docs": relevant_docs
                    },
                    "processing_time": processing_time
                }
                
            except Exception as e:
                logger.error(f"對話失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"對話失敗: {str(e)}")
        
        @self.app.get("/conversations/{conversation_id}/history")
        async def get_conversation_history(
            conversation_id: str = Path(..., min_length=1),
            limit: Optional[int] = Query(None, ge=1, le=100)
        ):
            """獲取對話歷史"""
            try:
                context = self.chat_manager.get_context(conversation_id)
                if limit:
                    context["history"] = context["history"][-limit:]
                return context
                
            except Exception as e:
                logger.error(f"獲取對話歷史失敗: {str(e)}")
                return {"history": [], "metadata": {}}  # 返回空歷史而不是錯誤
        
        @self.app.delete("/conversations/{conversation_id}")
        async def delete_conversation(conversation_id: str = Path(..., min_length=1)):
            """刪除對話"""
            try:
                self.chat_manager.clear_conversation(conversation_id)
                return {
                    "status": "success",
                    "message": f"成功刪除對話 {conversation_id}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"刪除對話失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"刪除對話失敗: {str(e)}")
        
        @self.app.get("/config")
        async def get_config():
            """獲取配置"""
            try:
                return self.config_manager.get_config_summary()
            except Exception as e:
                logger.error(f"獲取配置失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"獲取配置失敗: {str(e)}")
        
        @self.app.post("/config")
        async def update_config(request: ConfigUpdateRequest):
            """更新配置"""
            try:
                # 更新配置
                self.config_manager.update_config(request.config)
                
                # 驗證配置
                errors = self.config_manager.validate_config()
                if errors:
                    raise ValueError("\n".join(errors))
                
                # 重新初始化組件
                self.vector_store = VectorStore(**self.config_manager.get_component_config("vector_store").dict())
                self.retriever = Retriever(
                    vector_store=self.vector_store,
                    **self.config_manager.get_component_config("retriever").dict()
                )
                self.chat_manager = ChatManager(
                    retriever=self.retriever,
                    **self.config_manager.get_component_config("chat_manager").dict()
                )
                
                return {
                    "status": "success",
                    "message": "配置更新成功",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"更新配置失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"更新配置失敗: {str(e)}")
        
        @self.app.get("/health")
        async def health_check():
            """健康檢查"""
            try:
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "components": {
                        "vector_store": {
                            "total_docs": self.vector_store.index.ntotal,
                            "dimension": self.vector_store.dimension
                        },
                        "conversations": {
                            "active": len(self.chat_manager.conversations),
                            "total_messages": sum(len(conv["history"]) for conv in self.chat_manager.conversations.values())
                        }
                    },
                    "version": "1.0.0"
                }
            except Exception as e:
                logger.error(f"健康檢查失敗: {str(e)}")
                return {
                    "status": "unhealthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }

        @self.app.get("/documents", response_model=DocumentListResponse)
        async def list_documents(
            skip: int = Query(0, ge=0),
            limit: int = Query(10, ge=1, le=100)
        ):
            """獲取文檔列表"""
            try:
                docs = list(self.vector_store.doc_mapping.values())
                total = len(docs)
                return {
                    "documents": docs[skip:skip + limit],
                    "total": total
                }
            except Exception as e:
                logger.error(f"獲取文檔列表失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/documents/{doc_id}", response_model=DocumentDeleteResponse)
        async def delete_document(doc_id: str = Path(..., min_length=1)):
            """刪除文檔"""
            try:
                if doc_id not in self.vector_store.doc_mapping:
                    raise HTTPException(status_code=404, detail="文檔不存在")
                
                self.vector_store.delete_document(doc_id)
                return {
                    "status": "success",
                    "doc_id": doc_id
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"刪除文檔失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/search/batch", response_model=List[SearchResponse])
        async def batch_search(request: BatchSearchRequest):
            """批量搜索"""
            try:
                results = []
                start_time = datetime.utcnow()
                
                for query in request.queries:
                    query_results = self.retriever.retrieve(
                        query=query,
                        filters=request.filters,
                        top_k=request.top_k
                    )
                    
                    results.append({
                        "results": query_results,
                        "metadata": {
                            "query": query,
                            "filters": request.filters,
                            "timestamp": start_time.isoformat()
                        },
                        "total_results": len(query_results),
                        "processing_time": 0.0  # 將在最後更新
                    })
                
                end_time = datetime.utcnow()
                processing_time = (end_time - start_time).total_seconds()
                
                # 更新處理時間
                for result in results:
                    result["processing_time"] = processing_time / len(request.queries)
                
                return results
                
            except Exception as e:
                logger.error(f"批量搜索失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/documents/reindex")
        async def reindex_documents():
            """重新索引所有文檔"""
            try:
                start_time = datetime.utcnow()
                total_docs = self.vector_store.index.ntotal
                
                # 重建索引
                self.vector_store.rebuild_index()
                
                end_time = datetime.utcnow()
                processing_time = (end_time - start_time).total_seconds()
                
                return {
                    "status": "success",
                    "total_docs": total_docs,
                    "processing_time": processing_time
                }
            except Exception as e:
                logger.error(f"重新索引失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/documents/{doc_id}", response_model=DocumentUpdateResponse)
        async def update_document(
            doc_id: str = Path(..., min_length=1),
            request: DocumentUpdateRequest = Body(...)
        ):
            """更新文檔"""
            try:
                # 檢查文檔是否存在
                if doc_id not in self.vector_store.doc_mapping:
                    raise HTTPException(status_code=404, detail="文檔不存在")
                
                # 獲取原始文檔
                original_doc = self.vector_store.doc_mapping[doc_id]
                
                # 準備更新數據
                update_data = {}
                if request.content is not None:
                    update_data["content"] = request.content
                if request.metadata:
                    # 合併元數據，保留原有的基本信息
                    new_metadata = original_doc["metadata"].copy()
                    new_metadata.update(request.metadata)
                    new_metadata["updated_at"] = datetime.utcnow().isoformat()
                    update_data["metadata"] = new_metadata
                
                # 如果沒有任何更新數據，返回錯誤
                if not update_data:
                    raise HTTPException(status_code=400, detail="未提供任何更新數據")
                
                # 更新文檔
                self.vector_store.update_document(
                    doc_id=doc_id,
                    **update_data
                )
                
                # 獲取更新後的文檔
                updated_doc = self.vector_store.doc_mapping[doc_id]
                
                return {
                    "doc_id": doc_id,
                    "status": "success",
                    "content_hash": updated_doc["content_hash"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": updated_doc["metadata"]
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"更新文檔失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"更新文檔失敗: {str(e)}")

        @self.app.patch("/documents/{doc_id}/metadata", response_model=DocumentUpdateResponse)
        async def update_document_metadata(
            doc_id: str = Path(..., min_length=1),
            metadata: Dict[str, Any] = Body(...)
        ):
            """更新文檔元數據"""
            try:
                # 檢查文檔是否存在
                if doc_id not in self.vector_store.doc_mapping:
                    raise HTTPException(status_code=404, detail="文檔不存在")
                
                # 獲取原始文檔
                original_doc = self.vector_store.doc_mapping[doc_id]
                
                # 合併元數據
                new_metadata = original_doc["metadata"].copy()
                new_metadata.update(metadata)
                new_metadata["updated_at"] = datetime.utcnow().isoformat()
                
                # 更新文檔元數據
                self.vector_store.update_document(
                    doc_id=doc_id,
                    metadata=new_metadata
                )
                
                # 獲取更新後的文檔
                updated_doc = self.vector_store.doc_mapping[doc_id]
                
                return {
                    "doc_id": doc_id,
                    "status": "success",
                    "content_hash": updated_doc["content_hash"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": updated_doc["metadata"]
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"更新文檔元數據失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"更新文檔元數據失敗: {str(e)}")
    
    def _build_chat_prompt(self, query: str, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> str:
        """構建對話提示詞"""
        # 構建歷史對話部分
        history = context.get("history", [])
        history_text = ""
        for msg in history[-5:]:  # 只使用最近的5條消息
            role = "用戶" if msg["role"] == "user" else "助手"
            history_text += f"{role}: {msg['content']}\n"
        
        # 構建相關文檔部分
        docs_text = ""
        for doc in relevant_docs:
            docs_text += f"文檔內容: {doc['content'][:500]}...\n"  # 限制每個文檔的長度
        
        # 組合最終提示詞
        prompt = f"""基於以下信息回答用戶的問題。如果找不到相關信息，請誠實地說不知道。

相關文檔:
{docs_text}

歷史對話:
{history_text}

用戶: {query}
助手: """
        
        return prompt
    
    def _generate_response(self, prompt: str) -> str:
        """生成回覆"""
        try:
            # TODO: 實現實際的 LLM 調用
            # 這裡暫時返回一個示例回覆
            return "這是一個基於檢索內容的示例回覆。在實際部署時，這裡需要替換為真實的 LLM 調用。"
        except Exception as e:
            logger.error(f"生成回覆失敗: {str(e)}")
            return "抱歉，生成回覆時發生錯誤。請稍後再試。"
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """運行 API 服務"""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port) 