import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from shared.database.crud import UserCRUD, ConversationCRUD
from shared.ai.model_manager import ModelManager
from shared.utils.role_manager import RoleManager

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, db: Session):
        self.db = db
        self.model_manager = ModelManager()
        self.role_manager = RoleManager()
    
    async def handle_message(
        self,
        line_user_id: str,
        message: str,
        role_id: Optional[str] = None
    ) -> str:
        """處理用戶消息"""
        try:
            # 獲取或創建用戶
            user = UserCRUD.get_user_by_line_id(self.db, line_user_id)
            if not user:
                raise ValueError(f"找不到用戶: {line_user_id}")
            
            # 如果沒有指定角色，使用用戶默認角色
            if not role_id:
                user_settings = user.settings
                role_id = user_settings.default_role_id if user_settings else "fk_helper"
            
            # 創建新對話或獲取現有對話
            conversation = ConversationCRUD.create_conversation(
                self.db, user.id, role_id
            )
            
            # 保存用戶消息
            user_message = ConversationCRUD.add_message(
                self.db,
                conversation.id,
                "user",
                message,
                self.model_manager.count_tokens(message)
            )
            
            # 獲取對話上下文
            context = self._get_conversation_context(conversation.id)
            
            # 生成回應
            response = await self.model_manager.generate_response(
                role_id,
                message,
                context
            )
            
            # 保存助手回應
            assistant_message = ConversationCRUD.add_message(
                self.db,
                conversation.id,
                "assistant",
                response,
                self.model_manager.count_tokens(response)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"處理消息時發生錯誤: {str(e)}")
            return f"抱歉，處理您的消息時發生錯誤：{str(e)}"
    
    def _get_conversation_context(self, conversation_id: int, limit: int = 5) -> List[Dict]:
        """獲取對話上下文"""
        # TODO: 實現上下文獲取邏輯
        return []