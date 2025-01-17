from .line_bot import LineBot
from .webhook import WebhookHandler
from shared.config.config import Config
import logging

logger = logging.getLogger(__name__)

def start_webhook_server():
    """啟動 Webhook 服務器"""
    try:
        # 初始化 Line Bot
        line_bot = LineBot()
        
        # 初始化並啟動 Webhook 處理器
        webhook_handler = WebhookHandler(line_bot)
        webhook_handler.run(
            host=Config.HOST,
            port=Config.PORT
        )
    except Exception as e:
        logger.error(f"Failed to start webhook server: {e}")
        raise

if __name__ == "__main__":
    start_webhook_server() 