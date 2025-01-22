import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
from pathlib import Path
from ..retriever.retriever import Retriever

logger = logging.getLogger(__name__)

class ChatManager:
    """對話管理器"""
    
    def __init__(self,
                 retriever: Retriever,
                 max_context_length: int = 2000,
                 max_history_turns: int = 10):
        """
        初始化對話管理器
        
        Args:
            retriever: 文檔檢索器實例
            max_context_length: 上下文最大長度
            max_history_turns: 歷史對話最大輪數
        """
        self.retriever = retriever
        self.max_context_length = max_context_length
        self.max_history_turns = max_history_turns
        
        # 初始化對話歷史
        self.conversations = {}
    
    def create_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        創建新對話
        
        Args:
            conversation_id: 對話唯一標識
            
        Returns:
            對話信息
        """
        conversation = {
            'id': conversation_id,
            'created_at': datetime.utcnow().isoformat(),
            'messages': [],
            'context': {
                'documents': [],
                'metadata': {}
            }
        }
        
        self.conversations[conversation_id] = conversation
        return conversation
    
    def add_message(self,
                   conversation_id: str,
                   role: str,
                   content: str,
                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        添加對話消息
        
        Args:
            conversation_id: 對話唯一標識
            role: 發送者角色 (user/assistant/system)
            content: 消息內容
            metadata: 消息元數據
            
        Returns:
            更新後的對話信息
        """
        try:
            # 獲取對話
            conversation = self._get_conversation(conversation_id)
            
            # 創建消息
            message = {
                'id': f"msg_{len(conversation['messages'])}",
                'role': role,
                'content': content,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # 添加消息
            conversation['messages'].append(message)
            
            # 如果是用戶消息,更新上下文
            if role == 'user':
                self._update_context(conversation_id, content)
            
            # 保持歷史消息在限制範圍內
            if len(conversation['messages']) > self.max_history_turns * 2:
                conversation['messages'] = conversation['messages'][-self.max_history_turns * 2:]
            
            return conversation
            
        except Exception as e:
            logger.error(f"添加消息失敗: {str(e)}")
            raise
    
    def get_context(self,
                   conversation_id: str,
                   include_history: bool = True) -> Dict[str, Any]:
        """
        獲取對話上下文
        
        Args:
            conversation_id: 對話唯一標識
            include_history: 是否包含歷史消息
            
        Returns:
            對話上下文
        """
        try:
            conversation = self._get_conversation(conversation_id)
            
            context = {
                'documents': conversation['context']['documents'],
                'metadata': conversation['context']['metadata']
            }
            
            if include_history:
                context['history'] = self._format_history(conversation['messages'])
            
            return context
            
        except Exception as e:
            logger.error(f"獲取上下文失敗: {str(e)}")
            raise
    
    def _get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """獲取對話,如果不存在則創建"""
        if conversation_id not in self.conversations:
            return self.create_conversation(conversation_id)
        return self.conversations[conversation_id]
    
    def _update_context(self,
                       conversation_id: str,
                       query: str) -> None:
        """更新對話上下文"""
        try:
            # 檢索相關文檔
            results = self.retriever.retrieve(query)
            
            # 更新上下文文檔
            conversation = self._get_conversation(conversation_id)
            conversation['context']['documents'] = results
            
            # 更新元數據
            conversation['context']['metadata'].update({
                'last_query': query,
                'last_update': datetime.utcnow().isoformat(),
                'num_documents': len(results)
            })
            
        except Exception as e:
            logger.error(f"更新上下文失敗: {str(e)}")
            raise
    
    def _format_history(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化歷史消息"""
        formatted = []
        total_length = 0
        
        # 從最新的消息開始處理
        for message in reversed(messages):
            # 計算消息長度
            message_length = len(message['content'])
            
            # 如果添加此消息會超過長度限制,則停止
            if total_length + message_length > self.max_context_length:
                break
            
            # 添加消息
            formatted.insert(0, {
                'role': message['role'],
                'content': message['content']
            })
            
            total_length += message_length
        
        return formatted
    
    def get_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """獲取對話統計信息"""
        try:
            conversation = self._get_conversation(conversation_id)
            
            # 計算統計信息
            messages = conversation['messages']
            user_messages = [m for m in messages if m['role'] == 'user']
            assistant_messages = [m for m in messages if m['role'] == 'assistant']
            
            stats = {
                'total_messages': len(messages),
                'user_messages': len(user_messages),
                'assistant_messages': len(assistant_messages),
                'context_documents': len(conversation['context']['documents']),
                'created_at': conversation['created_at'],
                'last_message_at': messages[-1]['timestamp'] if messages else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"獲取對話統計失敗: {str(e)}")
            raise
    
    def clear_conversation(self, conversation_id: str) -> None:
        """清除對話歷史"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def save_conversations(self, file_path: str) -> None:
        """保存所有對話到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存對話失敗: {str(e)}")
            raise
    
    def load_conversations(self, file_path: str) -> None:
        """從文件加載對話"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.conversations = json.load(f)
                
        except Exception as e:
            logger.error(f"加載對話失敗: {str(e)}")
            raise 