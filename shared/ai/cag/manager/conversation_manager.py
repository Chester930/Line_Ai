from typing import Dict, List, Optional
import logging
from datetime import datetime
from shared.database.crud import ConversationCRUD, MessageCRUD
from .context_manager import ContextManager

logger = logging.getLogger(__name__)

class ConversationManager:
    """對話管理器，負責管理對話流程和狀態"""
    
    def __init__(self):
        self.conversation_crud = ConversationCRUD()
        self.message_crud = MessageCRUD()
        self.context_manager = ContextManager()
    
    async def process_message(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[int] = None,
        model: str = "gemini-pro"
    ) -> Dict:
        """處理用戶消息"""
        try:
            # 獲取或創建對話
            if not conversation_id:
                conversation = self.conversation_crud.create_conversation(
                    user_id,
                    model
                )
                conversation_id = conversation.id
            
            # 保存用戶消息
            self.message_crud.add_message(
                conversation_id,
                "user",
                message
            )
            
            # 獲取上下文
            context = await self.context_manager.get_context(
                conversation_id,
                message
            )
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"處理消息時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_response(
        self,
        conversation_id: int,
        response: str
    ) -> bool:
        """保存 AI 回應"""
        try:
            self.message_crud.add_message(
                conversation_id,
                "assistant",
                response
            )
            return True
        except Exception as e:
            logger.error(f"保存回應時發生錯誤：{str(e)}")
            return False
    
    def get_conversation_history(
        self,
        conversation_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """獲取對話歷史"""
        try:
            messages = self.message_crud.get_conversation_messages(
                conversation_id,
                limit
            )
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"獲取對話歷史時發生錯誤：{str(e)}")
            return []
