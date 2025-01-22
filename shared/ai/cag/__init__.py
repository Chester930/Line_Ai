from typing import Dict, Optional, List
import logging
from .manager.context_manager import ContextManager
from .manager.conversation_manager import ConversationManager
from .router.query_router import QueryRouter
from shared.database.models import Role
from shared.config.config import Config

logger = logging.getLogger(__name__)

class CAGSystem:
    """Context-Aware Generation System
    整合上下文管理、對話管理和查詢路由的系統
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.context_manager = ContextManager()
        self.conversation_manager = ConversationManager()
        self.query_router = QueryRouter()
        
    async def process_query(
        self,
        user_id: int,
        query: str,
        conversation_id: Optional[int] = None,
        role: Optional[Role] = None,
        available_plugins: Optional[List[str]] = None,
        model: str = "gemini-pro"
    ) -> Dict:
        """處理用戶查詢"""
        try:
            # 1. 路由查詢
            routing_result = self.query_router.route_query(
                query=query,
                available_plugins=available_plugins or [],
                role=role
            )
            
            if not routing_result["success"]:
                return routing_result
            
            # 2. 處理對話上下文
            conversation_result = await self.conversation_manager.process_message(
                user_id=user_id,
                message=routing_result["routing"]["modified_query"],
                conversation_id=conversation_id,
                model=model
            )
            
            if not conversation_result["success"]:
                return conversation_result
            
            # 3. 整合結果
            return {
                "success": True,
                "conversation_id": conversation_result["conversation_id"],
                "context": conversation_result["context"],
                "routing": routing_result["routing"],
                "model": model
            }
            
        except Exception as e:
            logger.error(f"處理查詢時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def save_response(
        self,
        conversation_id: int,
        response: str
    ) -> Dict:
        """保存 AI 回應"""
        try:
            success = self.conversation_manager.save_response(
                conversation_id,
                response
            )
            
            return {
                "success": success,
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            logger.error(f"保存回應時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_conversation_history(
        self,
        conversation_id: int,
        limit: int = 10
    ) -> Dict:
        """獲取對話歷史"""
        try:
            history = self.conversation_manager.get_conversation_history(
                conversation_id,
                limit
            )
            
            return {
                "success": True,
                "history": history,
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            logger.error(f"獲取對話歷史時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_context_window(self, size: int) -> Dict:
        """更新上下文窗口大小"""
        try:
            success = self.context_manager.update_context_window(size)
            
            return {
                "success": success,
                "window_size": size if success else None
            }
            
        except Exception as e:
            logger.error(f"更新上下文窗口時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def register_custom_routing_rule(
        self,
        plugin_name: str,
        pattern: str
    ) -> Dict:
        """註冊自定義路由規則"""
        try:
            success = self.query_router.register_custom_rule(
                plugin_name,
                pattern
            )
            
            return {
                "success": success,
                "plugin": plugin_name,
                "pattern": pattern
            }
            
        except Exception as e:
            logger.error(f"註冊路由規則時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

__all__ = ['CAGSystem']
