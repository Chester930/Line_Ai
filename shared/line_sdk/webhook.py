from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from .line_bot import LineBot
from .exceptions import WebhookError
import logging
import json

logger = logging.getLogger(__name__)

class WebhookHandler:
    def __init__(self, line_bot: LineBot):
        """初始化 Webhook 處理器"""
        self.line_bot = line_bot
        self.app = FastAPI(title="Line AI Webhook")
        self._setup_routes()
        
    def _setup_routes(self):
        """設置路由"""
        @self.app.post("/webhook")
        async def handle_webhook(request: Request):
            """處理來自 Line 的 Webhook 請求"""
            try:
                # 獲取 X-Line-Signature header
                signature = request.headers.get('X-Line-Signature', '')
                if not signature:
                    raise WebhookError("Missing signature", 400)
                
                # 讀取請求內容
                body = await request.body()
                body_str = body.decode('utf-8')
                
                # 記錄webhook請求
                logger.info(f"Webhook received - Signature: {signature}")
                logger.debug(f"Webhook body: {body_str}")
                
                # 處理webhook
                if not self.line_bot.handle_webhook(signature, body_str):
                    raise WebhookError("Invalid webhook request", 400)
                
                return JSONResponse(content={"status": "success"})
                
            except WebhookError as e:
                logger.error(f"Webhook error: {str(e)}")
                return JSONResponse(
                    status_code=e.status_code or 400,
                    content={"error": str(e)}
                )
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Internal server error"}
                )
                
        @self.app.get("/health")
        async def health_check():
            """健康檢查端點"""
            return {"status": "healthy"}
            
    def run(self, host: str = "0.0.0.0", port: int = 5000):
        """運行 Webhook 服務器"""
        import uvicorn
        logger.info(f"Starting webhook server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)
