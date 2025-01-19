import logging
from typing import List, Dict, Optional, Any
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic
from shared.config.config import Config
from shared.database.crud import UserCRUD, ConversationCRUD, MessageCRUD

logger = logging.getLogger(__name__)

class ConversationManager:
    """對話管理器"""
    
    def __init__(self):
        # 初始化資料庫操作類
        self.user_crud = UserCRUD()
        self.conversation_crud = ConversationCRUD()
        self.message_crud = MessageCRUD()
        
        # 初始化 AI 客戶端
        self._init_ai_clients()
        
        # 模型配置
        self.model_configs = {
            'gemini-pro': {
                'client': 'gemini',
                'max_tokens': 4096,
                'temperature': 0.7
            },
            'gpt-4-turbo-preview': {
                'client': 'openai',
                'max_tokens': 4096,
                'temperature': 0.7
            },
            'claude-3-sonnet-20240229': {
                'client': 'anthropic',
                'max_tokens': 4096,
                'temperature': 0.7
            }
        }
    
    def _init_ai_clients(self):
        """初始化 AI 服務客戶端"""
        # Gemini
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.gemini = genai.GenerativeModel('gemini-pro')
        
        # OpenAI
        self.openai = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Anthropic
        self.anthropic = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    
    async def get_response(
        self,
        line_user_id: str,
        message: str,
        model: str = 'gemini-pro'
    ) -> str:
        """獲取 AI 回應
        
        Args:
            line_user_id: LINE 用戶 ID
            message: 用戶訊息
            model: AI 模型名稱
            
        Returns:
            str: AI 回應內容
        """
        try:
            # 獲取或創建用戶
            user = self.user_crud.get_by_line_id(line_user_id)
            if not user:
                user = self.user_crud.create_user(line_user_id)
            
            # 更新最後活動時間
            self.user_crud.update_last_active(user.id)
            
            # 獲取或創建對話
            conversations = self.conversation_crud.get_user_conversations(user.id)
            if not conversations:
                conversation = self.conversation_crud.create_conversation(
                    user.id,
                    model
                )
            else:
                conversation = conversations[0]
            
            # 添加用戶訊息
            self.message_crud.add_message(
                conversation.id,
                'user',
                message
            )
            
            # 獲取對話歷史
            history = self.message_crud.get_conversation_messages(
                conversation.id,
                limit=10
            )
            
            # 生成 AI 回應
            response = await self._generate_response(
                message,
                history,
                model
            )
            
            # 添加 AI 回應
            self.message_crud.add_message(
                conversation.id,
                'assistant',
                response
            )
            
            return response
            
        except Exception as e:
            logger.error(f"生成回應時發生錯誤：{str(e)}")
            return f"抱歉，處理您的訊息時發生錯誤：{str(e)}"
    
    async def _generate_response(
        self,
        message: str,
        history: List[Dict],
        model: str
    ) -> str:
        """生成 AI 回應"""
        try:
            model_config = self.model_configs.get(model)
            if not model_config:
                raise ValueError(f"不支援的模型：{model}")
            
            client = model_config['client']
            
            if client == 'gemini':
                return await self._generate_gemini_response(
                    message,
                    history,
                    model_config
                )
            elif client == 'openai':
                return await self._generate_openai_response(
                    message,
                    history,
                    model_config
                )
            elif client == 'anthropic':
                return await self._generate_anthropic_response(
                    message,
                    history,
                    model_config
                )
            else:
                raise ValueError(f"未知的客戶端類型：{client}")
                
        except Exception as e:
            logger.error(f"生成 AI 回應時發生錯誤：{str(e)}")
            raise
    
    async def _generate_gemini_response(
        self,
        message: str,
        history: List[Dict],
        config: Dict
    ) -> str:
        """使用 Gemini 生成回應"""
        chat = self.gemini.start_chat(history=[
            {'role': msg.role, 'content': msg.content}
            for msg in history
        ])
        response = await chat.send_message_async(
            message,
            generation_config=genai.types.GenerationConfig(
                temperature=config['temperature'],
                max_output_tokens=config['max_tokens']
            )
        )
        return response.text
    
    async def _generate_openai_response(
        self,
        message: str,
        history: List[Dict],
        config: Dict
    ) -> str:
        """使用 OpenAI 生成回應"""
        messages = [
            {'role': msg.role, 'content': msg.content}
            for msg in history
        ]
        messages.append({'role': 'user', 'content': message})
        
        response = await self.openai.chat.completions.create(
            model=config['model'],
            messages=messages,
            temperature=config['temperature'],
            max_tokens=config['max_tokens']
        )
        return response.choices[0].message.content
    
    async def _generate_anthropic_response(
        self,
        message: str,
        history: List[Dict],
        config: Dict
    ) -> str:
        """使用 Anthropic Claude 生成回應"""
        messages = []
        for msg in history:
            role = 'assistant' if msg.role == 'assistant' else 'user'
            messages.append({
                'role': role,
                'content': msg.content
            })
        messages.append({'role': 'user', 'content': message})
        
        response = await self.anthropic.messages.create(
            model=config['model'],
            messages=messages,
            temperature=config['temperature'],
            max_tokens=config['max_tokens']
        )
        return response.content[0].text