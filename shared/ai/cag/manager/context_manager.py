from typing import Dict, List, Optional
import logging
from datetime import datetime
from shared.database.crud import MessageCRUD
from shared.ai.query_analyzer import QueryAnalyzer

logger = logging.getLogger(__name__)

class ContextManager:
    """上下文管理器，負責維護和管理對話上下文"""
    
    def __init__(self):
        self.message_crud = MessageCRUD()
        self.query_analyzer = QueryAnalyzer()
        self.context_window = 10  # 預設上下文窗口大小
        
    async def get_context(
        self,
        conversation_id: int,
        query: str,
        max_tokens: int = 2000
    ) -> Dict:
        """獲取相關上下文"""
        try:
            # 分析查詢
            query_info = self.query_analyzer.analyze(query)
            
            # 獲取歷史消息
            messages = self.message_crud.get_conversation_messages(
                conversation_id,
                limit=self.context_window
            )
            
            # 根據查詢類型過濾和組織上下文
            relevant_context = self._filter_relevant_context(
                messages,
                query_info,
                max_tokens
            )
            
            return {
                "success": True,
                "context": relevant_context,
                "query_info": query_info
            }
            
        except Exception as e:
            logger.error(f"獲取上下文時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _filter_relevant_context(
        self,
        messages: List[Dict],
        query_info: Dict,
        max_tokens: int
    ) -> List[Dict]:
        """過濾相關上下文"""
        relevant_messages = []
        current_tokens = 0
        
        for message in reversed(messages):  # 從最新的開始
            # 估算 token 數量
            estimated_tokens = len(message.content.split()) * 1.3
            
            if current_tokens + estimated_tokens > max_tokens:
                break
                
            # 根據查詢類型判斷相關性
            if self._is_relevant(message, query_info):
                relevant_messages.append({
                    "role": message.role,
                    "content": message.content,
                    "timestamp": message.created_at.isoformat()
                })
                current_tokens += estimated_tokens
        
        return list(reversed(relevant_messages))  # 恢復時間順序
    
    def _is_relevant(self, message: Dict, query_info: Dict) -> bool:
        """判斷消息是否相關"""
        # 1. 時間相關性
        if query_info.get("requires_recent_info"):
            # 只返回最近的消息
            return True
            
        # 2. 關鍵詞相關性
        message_keywords = set(
            jieba.analyse.extract_tags(message.content)
        )
        query_keywords = set(
            kw for kw, _ in query_info.get("keywords", [])
        )
        
        # 如果有關鍵詞重疊，認為相關
        if message_keywords & query_keywords:
            return True
            
        # 3. 對話流相關性
        if message.role == "assistant" and query_info.get("is_followup"):
            return True
            
        return False
    
    def update_context_window(self, size: int):
        """更新上下文窗口大小"""
        if 1 <= size <= 20:  # 限制範圍
            self.context_window = size
            return True
        return False
