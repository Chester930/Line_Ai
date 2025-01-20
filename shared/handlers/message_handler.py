import logging
from linebot import LineBotApi
from linebot.models import TextSendMessage
from shared.config.config import Config

logger = logging.getLogger(__name__)

class MessageHandler:
    """訊息處理器"""
    
    def __init__(self, line_bot_api: LineBotApi):
        self.line_bot_api = line_bot_api
        self.config = Config.get_instance()
    
    def handle_text_message(self, event):
        """處理文字訊息"""
        try:
            # 回覆相同的訊息
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text)
            )
        except Exception as e:
            logger.error(f"處理訊息失敗: {str(e)}") 