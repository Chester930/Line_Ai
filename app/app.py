from flask import Flask
from shared.config.config import Config
from .line_bot.bot import create_bot

def create_app() -> Flask:
    """創建 Flask 應用
    
    Returns:
        Flask: Flask 應用實例
    """
    app = Flask(__name__)
    
    # 載入配置
    app.config.from_object(Config)
    
    # 創建 LINE Bot
    bot = create_bot(app)
    
    # 註冊首頁路由
    @app.route('/')
    def index():
        return 'LINE Bot is running!'
    
    return app

def run_app():
    """運行應用"""
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )

if __name__ == '__main__':
    run_app() 