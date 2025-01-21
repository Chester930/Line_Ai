import logging
from typing import Dict, Any
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic
from shared.config.config import Config

logger = logging.getLogger(__name__)

class ChatTester:
    """獨立的對話測試類，不依賴 LINE 或用戶系統"""
    
    def __init__(self):
        # 初始化 AI 模型客戶端
        self.setup_ai_clients()
        self.chat_history = []  # 添加對話歷史記錄
    
    def setup_ai_clients(self):
        """設置 AI 模型客戶端"""
        try:
            if Config.GOOGLE_API_KEY:
                import google.generativeai as genai
                genai.configure(api_key=Config.GOOGLE_API_KEY)
        except ImportError:
            logger.warning("Google AI 套件未安裝")
        
        try:
            if Config.OPENAI_API_KEY:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        except ImportError:
            logger.warning("OpenAI 套件未安裝")
        
        try:
            if Config.CLAUDE_API_KEY:
                from anthropic import Anthropic
                self.anthropic_client = Anthropic(api_key=Config.CLAUDE_API_KEY)
        except ImportError:
            logger.warning("Anthropic 套件未安裝")
    
    async def generate_response(
        self,
        message: str,
        role_prompt: str,
        settings: Dict[str, Any],
        keep_history: bool = True  # 添加是否保留歷史的選項
    ) -> str:
        """生成回應"""
        try:
            # 根據模型類型選擇對應的處理方法
            if settings.get('model', '').startswith('gemini'):
                response = await self._generate_gemini_response(message, role_prompt, settings)
            elif settings.get('model', '').startswith('gpt'):
                response = await self._generate_openai_response(message, role_prompt, settings)
            elif settings.get('model', '').startswith('claude'):
                response = await self._generate_claude_response(message, role_prompt, settings)
            else:
                return "未指定有效的模型類型"
            
            # 更新對話歷史
            if keep_history:
                self.chat_history.append({"role": "user", "content": message})
                self.chat_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            logger.error(f"生成回應時發生錯誤：{str(e)}")
            return f"生成回應時發生錯誤：{str(e)}"
    
    async def _generate_gemini_response(self, message: str, role_prompt: str, settings: Dict[str, Any]) -> str:
        """使用 Gemini 生成回應"""
        try:
            # 從 settings 中取出 model，其他參數用於 generation_config
            model_name = settings.pop('model', 'gemini-pro')
            model = genai.GenerativeModel(model_name)
            
            # 創建有效的 generation_config
            generation_config = {
                'temperature': settings.get('temperature', 0.7),
                'top_p': settings.get('top_p', 0.9),
                'max_output_tokens': settings.get('max_tokens', 1000),
                'candidate_count': 1
            }
            
            # 構建完整的對話歷史
            history = []
            if self.chat_history:
                for msg in self.chat_history:
                    if msg["role"] == "user":
                        history.append({"role": "user", "parts": [msg["content"]]})
                    else:
                        history.append({"role": "model", "parts": [msg["content"]]})
            
            chat = model.start_chat(history=history)
            response = chat.send_message(
                f"{role_prompt}\n\n用戶: {message}",
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini 生成回應時發生錯誤：{str(e)}")
            return f"Gemini 生成回應時發生錯誤：{str(e)}"
    
    async def _generate_openai_response(self, message: str, role_prompt: str, settings: Dict[str, Any]) -> str:
        """使用 OpenAI 生成回應"""
        messages = [{"role": "system", "content": role_prompt}]
        
        # 添加歷史對話
        messages.extend(self.chat_history)
        
        # 添加當前消息
        messages.append({"role": "user", "content": message})
        
        response = self.openai_client.chat.completions.create(
            model=settings.get('model', 'gpt-3.5-turbo'),
            messages=messages,
            temperature=settings.get('temperature', 0.7),
            max_tokens=settings.get('max_tokens', 1000),
            top_p=settings.get('top_p', 0.9)
        )
        return response.choices[0].message.content
    
    async def _generate_claude_response(self, message: str, role_prompt: str, settings: Dict[str, Any]) -> str:
        """使用 Claude 生成回應"""
        messages = [{"role": "system", "content": role_prompt}]
        
        # 添加歷史對話
        messages.extend(self.chat_history)
        
        # 添加當前消息
        messages.append({"role": "user", "content": message})
        
        response = self.anthropic_client.messages.create(
            model=settings.get('model', 'claude-3-opus-20240229'),
            messages=messages,
            temperature=settings.get('temperature', 0.7),
            max_tokens=settings.get('max_tokens', 1000),
            top_p=settings.get('top_p', 0.9)
        )
        return response.content[0].text
    
    def clear_history(self):
        """清除對話歷史"""
        self.chat_history = []
    
    def get_history(self) -> list:
        """獲取對話歷史"""
        return self.chat_history 