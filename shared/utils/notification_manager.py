import logging
from linebot.models import TextSendMessage
from shared.config.config import Config

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
    
    def send_notification(self, user_id, message):
        try:
            self.line_bot_api.push_message(
                user_id,
                TextSendMessage(text=message)
            )
            return True
        except Exception as e:
            logger.error(f"發送通知失敗: {str(e)}")
            return False