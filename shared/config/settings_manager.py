import json
import os
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SettingsManager:
    def __init__(self):
        self.config_dir = "config"
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.api_keys_file = os.path.join(self.config_dir, "api_keys.json")
        self.roles_file = os.path.join(self.config_dir, "roles.json")
        
        # 確保配置目錄存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 初始化設定
        self.settings = self._load_json(self.settings_file, {
            "initialized": False,
            "last_updated": None
        })
        
        self.api_keys = self._load_json(self.api_keys_file, {
            "line_channel_secret": "",
            "line_channel_access_token": "",
            "google_api_key": "",
            "ngrok_auth_token": ""
        })
        
        self.roles = self._load_json(self.roles_file, {})

    def _load_json(self, file_path: str, default_value: Dict) -> Dict:
        """載入 JSON 檔案"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default_value
        except Exception as e:
            logger.error(f"載入 {file_path} 時發生錯誤: {str(e)}")
            return default_value

    def _save_json(self, file_path: str, data: Dict) -> bool:
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

    def get_api_key(self, key_name: str) -> Optional[str]:
        """獲取特定的 API Key"""
        return self.api_keys.get(key_name)

    def update_role(self, role_id: str, role_data: Dict) -> bool:
        """更新角色設定"""
        try:
            self.roles[role_id] = role_data
            return self._save_json(self.roles_file, self.roles)
        except Exception as e:
            logger.error(f"更新角色設定時發生錯誤: {str(e)}")
            return False

    def get_role(self, role_id: str) -> Optional[Dict]:
        """獲取角色設定"""
        return self.roles.get(role_id)

    def list_roles(self) -> Dict:
        """列出所有角色"""
        return self.roles

    def delete_role(self, role_id: str) -> bool:
        """刪除角色"""
        try:
            if role_id in self.roles:
                del self.roles[role_id]
                return self._save_json(self.roles_file, self.roles)
            return False
        except Exception as e:
            logger.error(f"刪除角色時發生錯誤: {str(e)}")
            return False

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

    def import_default_roles(self):
        """導入預設角色設定"""
        try:
            default_roles_path = os.path.join(
                os.path.dirname(__file__), 
                "default_roles.json"
            )
            
            if os.path.exists(default_roles_path):
                with open(default_roles_path, 'r', encoding='utf-8') as f:
                    default_roles = json.load(f)
                    
                # 更新現有角色，保留自定義設定
                for role_id, role_data in default_roles.items():
                    if role_id not in self.roles:
                        self.roles[role_id] = role_data
                    else:
                        # 合併設定，保留自定義值
                        current_role = self.roles[role_id]
                        for key, value in role_data.items():
                            if key not in current_role:
                                current_role[key] = value
                
                return self._save_json(self.roles_file, self.roles)
            return False
        except Exception as e:
            logger.error(f"導入預設角色時發生錯誤: {str(e)}")
            return False 