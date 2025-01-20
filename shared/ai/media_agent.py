import logging
import io
import google.generativeai as genai
import speech_recognition as sr
from PIL import Image
from typing import Dict, Any, Optional
import asyncio
from shared.config.config import Config

logger = logging.getLogger(__name__)

class MediaAgent:
    """媒體處理代理，負責將圖片和音訊轉換為文字描述"""
    
    def __init__(self):
        config = Config()  # 創建實例
        self.api_key = config.GOOGLE_API_KEY
        if not self.api_key:
            logger.warning("未設定 Google API Key")
        genai.configure(api_key=self.api_key)
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
        self.recognizer = sr.Recognizer()
        
    async def process_media_async(
        self,
        media_content: Any,
        media_type: str
    ) -> Dict:
        """非同步處理媒體內容
        
        Args:
            media_content: 媒體內容（PIL.Image 或 bytes）
            media_type: 媒體類型 ('image' 或 'audio')
            
        Returns:
            Dict: {
                'success': bool,
                'text': str,
                'error': Optional[str]
            }
        """
        try:
            if media_type == 'image':
                return await self._process_image_async(media_content)
            elif media_type == 'audio':
                return await self._process_audio_async(media_content)
            else:
                return {
                    'success': False,
                    'text': '',
                    'error': f'不支援的媒體類型：{media_type}'
                }
        except Exception as e:
            logger.error(f"處理媒體時發生錯誤：{str(e)}")
            return {
                'success': False,
                'text': '',
                'error': str(e)
            }
    
    async def _process_image_async(self, image: Image.Image) -> Dict:
        """處理圖片"""
        try:
            # 將圖片轉換為 bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format or 'PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # 使用 Gemini Vision API 生成描述
            response = await self.vision_model.generate_content_async([
                "請詳細描述這張圖片的內容，包括：\n"
                "1. 主要物件和人物\n"
                "2. 場景和背景\n"
                "3. 顏色和視覺特徵\n"
                "4. 任何文字或標誌\n"
                "請用中文回答，並保持簡潔明瞭。",
                img_byte_arr
            ])
            
            return {
                'success': True,
                'text': response.text,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"處理圖片時發生錯誤：{str(e)}")
            return {
                'success': False,
                'text': '',
                'error': f"圖片處理失敗：{str(e)}"
            }
    
    async def _process_audio_async(self, audio_data: bytes) -> Dict:
        """處理音訊"""
        try:
            # 使用 asyncio.to_thread 將同步處理轉為非同步
            result = await asyncio.to_thread(
                self._process_audio_sync,
                audio_data
            )
            return result
            
        except Exception as e:
            logger.error(f"處理音訊時發生錯誤：{str(e)}")
            return {
                'success': False,
                'text': '',
                'error': f"音訊處理失敗：{str(e)}"
            }
    
    def _process_audio_sync(self, audio_data: bytes) -> Dict:
        """同步處理音訊"""
        try:
            # 創建臨時音訊檔案
            temp_wav = io.BytesIO(audio_data)
            
            # 使用 speech_recognition 進行辨識
            with sr.AudioFile(temp_wav) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(
                    audio,
                    language='zh-TW'  # 設定為中文
                )
            
            return {
                'success': True,
                'text': text,
                'error': None
            }
            
        except sr.UnknownValueError:
            return {
                'success': False,
                'text': '',
                'error': '無法識別音訊內容'
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'text': '',
                'error': f'語音識別服務錯誤：{str(e)}'
            } 