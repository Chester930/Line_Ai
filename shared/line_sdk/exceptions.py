class LineBotError(Exception):
    """Line Bot 基礎異常類"""
    def __init__(self, message: str = None, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

class ConfigurationError(LineBotError):
    """配置相關錯誤"""
    def __init__(self, message: str = "Configuration error", missing_fields: list = None):
        self.missing_fields = missing_fields
        if missing_fields:
            message = f"{message}: Missing fields - {', '.join(missing_fields)}"
        super().__init__(message)

class WebhookError(LineBotError):
    """Webhook 處理錯誤"""
    def __init__(self, message: str = "Webhook error", status_code: int = None):
        self.status_code = status_code
        if status_code:
            message = f"{message} (Status code: {status_code})"
        super().__init__(message)

class MessageError(LineBotError):
    """消息處理錯誤"""
    def __init__(self, message: str = "Message error", event_type: str = None):
        self.event_type = event_type
        if event_type:
            message = f"{message} when processing {event_type}"
        super().__init__(message)

class AuthenticationError(LineBotError):
    """認證相關錯誤"""
    pass

class RateLimitError(LineBotError):
    """API 請求限制錯誤"""
    def __init__(self, message: str = "Rate limit exceeded", reset_time: int = None):
        self.reset_time = reset_time
        if reset_time:
            message = f"{message}, reset at {reset_time}"
        super().__init__(message)