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
        self.config = Config()
        
        # 根據選擇的模型和可用的 API key 初始化對應的客戶端
        self.clients = {}
        
        # 只在有 API key 時初始化對應的客戶端
        if self.config.GOOGLE_API_KEY:
            genai.configure(api_key=self.config.GOOGLE_API_KEY)
            self.clients['google'] = genai
            
        if self.config.OPENAI_API_KEY:
            self.clients['openai'] = OpenAI(api_key=self.config.OPENAI_API_KEY)
            
        if self.config.CLAUDE_API_KEY:
            self.clients['anthropic'] = Anthropic(api_key=self.config.CLAUDE_API_KEY)
        
        # 初始化資料庫操作類
        self.user_crud = UserCRUD()
        self.conversation_crud = ConversationCRUD()
        self.message_crud = MessageCRUD()
        
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
    
    async def get_response(self, user_id: str, message: str, model: str = None, **kwargs):
        """根據選擇的模型獲取回應"""
        try:
            # 確定使用哪個客戶端
            if model.startswith('gemini-'):
                if 'google' not in self.clients:
                    raise ValueError("Google API key not configured")
                return self._get_gemini_response(self.clients['google'], message, model, **kwargs)
                
            elif model.startswith('gpt-'):
                if 'openai' not in self.clients:
                    raise ValueError("OpenAI API key not configured")
                client = self.clients['openai']
                return await self._get_openai_response(client, message, model, **kwargs)
                
            elif model.startswith('claude-'):
                if 'anthropic' not in self.clients:
                    raise ValueError("Claude API key not configured")
                client = self.clients['anthropic']
                return await self._get_claude_response(client, message, model, **kwargs)
                
            else:
                raise ValueError(f"Unsupported model: {model}")
        except Exception as e:
            logger.error(f"生成回應失敗: {str(e)}")
            raise
    
    def _get_gemini_response(self, client, message: str, model: str, **kwargs):
        """使用 Gemini 生成回應 (同步方法)"""
        model = client.GenerativeModel(model)
        response = model.generate_content(message)
        return response.text
    
    async def _get_openai_response(self, client, message: str, model: str, **kwargs):
        """使用 OpenAI 生成回應"""
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            **kwargs
        )
        return response.choices[0].message.content
    
    async def _get_claude_response(self, client, message: str, model: str, **kwargs):
        """使用 Anthropic Claude 生成回應"""
        response = await client.messages.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            **kwargs
        )
        return response.content[0].text