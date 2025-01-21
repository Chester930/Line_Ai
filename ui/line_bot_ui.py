from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from shared.config.config import Config
from shared.utils.ngrok_manager import NgrokManager
import logging

app = Flask(__name__)
ngrok_manager = NgrokManager()

# 創建 Config 實例
config = Config()

# 使用實例來獲取設定
line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)

logger = logging.getLogger(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # TODO: 實現消息處理邏輯
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )

@app.route("/status")
def status():
    """檢查服務狀態"""
    return jsonify({"status": "running"})

@app.route("/webhook-url")
def webhook_url():
    """獲取當前 webhook URL"""
    url = ngrok_manager.get_public_url()
    if url:
        return jsonify({"url": url})
    return jsonify({"url": None}), 404

def start_line_bot():
    """啟動 LINE Bot 服務"""
    try:
        # 驗證必要的設定
        config.validate()
        
        # 啟動 ngrok
        logger.info("正在啟動 ngrok...")
        webhook_url = ngrok_manager.start()
        
        if webhook_url:
            logger.info(f"=== LINE Bot Webhook URL ===\n{webhook_url}/callback")
            
            # 啟動 Flask 服務
            logger.info("正在啟動 Flask 服務...")
            app.run(host='127.0.0.1', port=5000, threaded=True)
        else:
            raise RuntimeError("無法獲取 ngrok URL")
            
    except Exception as e:
        logger.error(f"啟動服務失敗: {str(e)}")
        ngrok_manager.stop()  # 確保清理
        raise

if __name__ == "__main__":
    start_line_bot()