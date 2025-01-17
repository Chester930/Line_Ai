import os
import json
import logging
from datetime import datetime
from shared.config.config import Config

logger = logging.getLogger(__name__)

class SettingsManager:
    def __init__(self):
        self.config_dir = os.path.join(Config.DATA_DIR, "config")
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.api_keys_file = os.path.join(self.config_dir, "api_keys.json")
        
        # 初始化設定
        self.settings = self._load_json(self.settings_file, {
            "initialized": False,
            "last_updated": None
        })
        
        self.api_keys = self._load_json(self.api_keys_file, {
            "line_channel_secret": "",
            "line_channel_access_token": "",
            "ngrok_auth_token": "",
            "google_api_key": ""
        })
    
    def _load_json(self, file_path: str, default_value: dict) -> dict:
        """載入 JSON 檔案"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default_value
        except Exception as e:
            logger.error(f"載入 {file_path} 時發生錯誤: {str(e)}")
            return default_value
    
    def _save_json(self, file_path: str, data: dict) -> bool:
        """儲存 JSON 檔案"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"儲存 {file_path} 時發生錯誤: {str(e)}")
            return False
    
    def update_api_keys(self, **keys) -> bool:
        """更新 API Keys"""
        try:
            for key, value in keys.items():
                if key in self.api_keys:
                    self.api_keys[key] = value
            
            success = self._save_json(self.api_keys_file, self.api_keys)
            if success:
                self.settings["last_updated"] = datetime.now().isoformat()
                self._save_json(self.settings_file, self.settings)
            return success
        except Exception as e:
            logger.error(f"更新 API Keys 時發生錯誤: {str(e)}")
            return False
    
    def get_api_key(self, key_name: str) -> str:
        """獲取特定的 API Key"""
        return self.api_keys.get(key_name, "")
    
    def is_initialized(self) -> bool:
        """檢查是否已完成初始化設定"""
        return self.settings.get("initialized", False)
    
    def mark_initialized(self) -> bool:
        """標記為已初始化"""
        try:
            self.settings["initialized"] = True
            self.settings["last_updated"] = datetime.now().isoformat()
            return self._save_json(self.settings_file, self.settings)
        except Exception as e:
            logger.error(f"標記初始化狀態時發生錯誤: {str(e)}")
            return False 