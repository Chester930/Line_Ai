from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from linebot.v3.exceptions import InvalidSignatureError

from shared.config.config import Config
import logging

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LineBot:
    def __init__(self):
        """初始化 Line Bot"""
        # 驗證配置
        Config.validate()
        
        # 初始化 Line Bot SDK
        self.configuration = Configuration(
            access_token=Config.LINE_CHANNEL_ACCESS_TOKEN
        )
        self.handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)
        
        # 初始化 API 客戶端
        self.api_client = ApiClient(self.configuration)
        self.messaging_api = MessagingApi(self.api_client)
        
        # 設置消息處理器
        self._setup_handlers()
        
    def _setup_handlers(self):
        """設置消息處理器"""
        @self.handler.add(MessageEvent, message=TextMessageContent)
        def handle_text_message(event):
            """處理文字消息"""
            try:
                self.messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=event.message.text)]
                    )
                )
            except Exception as e:
                logger.error(f"Error handling message: {e}")
    
    def handle_webhook(self, signature: str, body: str):
        """處理 webhook 請求"""
        try:
            self.handler.handle(body, signature)
            return True
        except InvalidSignatureError:
            logger.error("Invalid signature")
            return False
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return False
            
    def __del__(self):
        """清理資源"""
        if hasattr(self, 'api_client'):
            self.api_client.close()