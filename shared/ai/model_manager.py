import os
import logging
from typing import List, Dict, Optional
import google.generativeai as genai
from shared.config.config import Config
from shared.utils.role_manager import RoleManager
import io

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self):
        self.api_key = Config.GOOGLE_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.role_manager = RoleManager()
        
    def _prepare_prompt(self, role_id: str, user_input: str, context: List[Dict] = None) -> str:
        """準備提示詞"""
        role = self.role_manager.get_role(role_id)
        if not role:
            raise ValueError(f"找不到角色: {role_id}")
        
        # 構建完整提示詞
        system_prompt = role.prompt
        
        # 如果有上下文，添加到提示詞中
        context_text = ""
        if context:
            context_text = "\n\n相關上下文：\n" + "\n".join(
                f"[{item['type']}] {item['content']}"
                for item in context
            )
        
        # 組合最終提示詞
        final_prompt = f"{system_prompt}\n\n{context_text}\n\n用戶：{user_input}\n\n助手："
        return final_prompt
    
    async def generate_response(
        self,
        role_id: str,
        user_input: str,
        context: List[Dict] = None,
        stream: bool = False
    ) -> str:
        """生成回應"""
        try:
            # 獲取角色設定
            role = self.role_manager.get_role(role_id)
            if not role:
                raise ValueError(f"找不到角色: {role_id}")
            
            # 準備提示詞
            prompt = self._prepare_prompt(role_id, user_input, context)
            
            # 設置生成參數
            generation_config = {
                "temperature": role.settings.get("temperature", 0.7),
                "top_p": role.settings.get("top_p", 0.9),
                "max_output_tokens": role.settings.get("max_tokens", 2000),
            }
            
            # 生成回應
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config,
                stream=stream
            )
            
            if stream:
                return response  # 返回流式響應對象
            else:
                return response.text  # 返回完整文本
                
        except Exception as e:
            logger.error(f"生成回應時發生錯誤: {str(e)}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """計算文本的 token 數量"""
        try:
            return len(self.model.count_tokens(text).tokens)
        except Exception as e:
            logger.error(f"計算 tokens 時發生錯誤: {str(e)}")
            return 0

    def describe_image(self, image) -> str:
        """使用 Gemini Vision API 描述圖片"""
        try:
            # 將 PIL Image 轉換為 bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format)
            img_byte_arr = img_byte_arr.getvalue()
            
            # 使用 Gemini Vision API
            model = genai.GenerativeModel('gemini-pro-vision')
            response = model.generate_content([
                "請詳細描述這張圖片的內容，包括主要物件、場景、顏色等細節。",
                img_byte_arr
            ])
            
            return response.text
        except Exception as e:
            logger.error(f"圖片描述失敗：{str(e)}")
            return "無法描述圖片內容"