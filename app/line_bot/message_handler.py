import logging
from typing import Dict, Any
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, AudioMessage, FileMessage,
    TextSendMessage, ImageSendMessage
)
from linebot.exceptions import LineBotApiError
from shared.utils.file_processor import FileProcessor
from shared.ai.conversation_manager import ConversationManager
import io

logger = logging.getLogger(__name__)

class LineMessageHandler:
    """LINE 訊息處理器"""
    
    def __init__(self, line_bot_api, conversation_manager: ConversationManager):
        self.line_bot_api = line_bot_api
        self.conversation_manager = conversation_manager
        self.file_processor = FileProcessor()
        
    async def handle_message(self, event: MessageEvent) -> None:
        """處理各種類型的訊息"""
        try:
            if isinstance(event.message, TextMessage):
                await self._handle_text(event)
            elif isinstance(event.message, ImageMessage):
                await self._handle_image(event)
            elif isinstance(event.message, AudioMessage):
                await self._handle_audio(event)
            elif isinstance(event.message, FileMessage):
                await self._handle_file(event)
            else:
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="抱歉，我無法處理這種類型的訊息。")
                )
                
        except Exception as e:
            logger.error(f"處理訊息時發生錯誤：{str(e)}")
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"處理訊息時發生錯誤：{str(e)}")
            )
    
    async def _handle_text(self, event: MessageEvent) -> None:
        """處理文字訊息"""
        response = await self.conversation_manager.get_response(
            event.source.user_id,
            event.message.text
        )
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
    
    async def _handle_image(self, event: MessageEvent) -> None:
        """處理圖片訊息"""
        try:
            # 獲取圖片內容
            message_content = self.line_bot_api.get_message_content(event.message.id)
            image_data = io.BytesIO(message_content.content)
            
            # 處理圖片
            result = await self.file_processor.process_file_with_timeout(
                image_data,
                'image/jpeg',
                timeout=25
            )
            
            if result['success']:
                # 將圖片描述加入對話
                response = await self.conversation_manager.get_response(
                    event.source.user_id,
                    f"[圖片描述] {result['content']['text']}"
                )
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=response)
                )
            else:
                raise ValueError(result['error'])
                
        except Exception as e:
            logger.error(f"處理圖片時發生錯誤：{str(e)}")
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"處理圖片時發生錯誤：{str(e)}")
            )
    
    async def _handle_audio(self, event: MessageEvent) -> None:
        """處理音訊訊息"""
        try:
            # 獲取音訊內容
            message_content = self.line_bot_api.get_message_content(event.message.id)
            audio_data = io.BytesIO(message_content.content)
            
            # 處理音訊
            result = await self.file_processor.process_file_with_timeout(
                audio_data,
                'audio/wav',
                timeout=25
            )
            
            if result['success']:
                # 將語音轉文字加入對話
                response = await self.conversation_manager.get_response(
                    event.source.user_id,
                    f"[語音內容] {result['content']['text']}"
                )
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=response)
                )
            else:
                raise ValueError(result['error'])
                
        except Exception as e:
            logger.error(f"處理音訊時發生錯誤：{str(e)}")
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"處理音訊時發生錯誤：{str(e)}")
            )
    
    async def _handle_file(self, event: MessageEvent) -> None:
        """處理一般檔案"""
        try:
            # 檢查檔案大小
            if event.message.file_size > self.file_processor.MAX_FILE_SIZE:
                raise ValueError(f"檔案大小超過限制（最大 {self.file_processor.MAX_FILE_SIZE/1024/1024}MB）")
            
            # 獲取檔案內容
            message_content = self.line_bot_api.get_message_content(event.message.id)
            file_data = io.BytesIO(message_content.content)
            
            # 處理檔案
            result = await self.file_processor.process_file_with_timeout(
                file_data,
                event.message.file_type,
                timeout=25
            )
            
            if result['success']:
                # 將檔案內容加入對話
                response = await self.conversation_manager.get_response(
                    event.source.user_id,
                    f"[檔案內容] {result['content']['text']}"
                )
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=response)
                )
            else:
                raise ValueError(result['error'])
                
        except Exception as e:
            logger.error(f"處理檔案時發生錯誤：{str(e)}")
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"處理檔案時發生錯誤：{str(e)}")
            ) 