import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, List
from shared.config.config import Config

logger = logging.getLogger(__name__)

class Role:
    def __init__(self, role_id: str, data: Dict):
        self.id = role_id
        self.name = data.get('name', '')
        self.description = data.get('description', '')
        self.prompt = data.get('prompt', '')
        self.settings = data.get('settings', {
            'temperature': 0.7,
            'top_p': 0.9,
            'max_tokens': 1000,
            'web_search': False
        })

class RoleManager:
    """角色管理器"""
    
    def __init__(self):
        # 創建 Config 實例
        self.config = Config()
        
        # 使用實例屬性而不是類屬性
        self.config_dir = os.path.join(self.config.DATA_DIR, "config")
        self.roles_file = os.path.join(self.config_dir, "roles.json")
        
        # 確保目錄存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 加載角色配置
        self._roles_data = self._load_roles()
        # 將 JSON 數據轉換為 Role 對象
        self.roles = {
            role_id: Role(role_id, data) 
            for role_id, data in self._roles_data.items()
        }
    
    def _load_roles(self) -> Dict:
        """從文件加載角色配置"""
        if os.path.exists(self.roles_file):
            try:
                with open(self.roles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加載角色配置失敗: {str(e)}")
                return {}
        return {}
    
    def _save_roles(self) -> bool:
        """保存角色配置到文件"""
        try:
            # 將 Role 對象轉換回字典格式
            roles_data = {
                role_id: {
                    'name': role.name,
                    'description': role.description,
                    'prompt': role.prompt,
                    'settings': role.settings
                }
                for role_id, role in self.roles.items()
            }
            
            with open(self.roles_file, 'w', encoding='utf-8') as f:
                json.dump(roles_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存角色配置失敗: {str(e)}")
            return False
    
    def create_role(self, role_id: str, name: str, description: str, 
                   prompt: str, settings: Dict = None) -> bool:
        """創建新角色"""
        try:
            if role_id in self.roles:
                return False
            
            role_data = {
                'name': name,
                'description': description,
                'prompt': prompt,
                'settings': settings or {}
            }
            
            # 創建 Role 對象
            self.roles[role_id] = Role(role_id, role_data)
            return self._save_roles()
        except Exception as e:
            logger.error(f"創建角色失敗: {str(e)}")
            return False
    
    def update_role(self, role_id: str, name: str = None, description: str = None,
                   prompt: str = None, settings: Dict = None) -> bool:
        """更新角色設定"""
        try:
            if role_id not in self.roles:
                return False
            
            role = self.roles[role_id]
            if name is not None:
                role.name = name
            if description is not None:
                role.description = description
            if prompt is not None:
                role.prompt = prompt
            if settings is not None:
                role.settings.update(settings)
            
            return self._save_roles()
        except Exception as e:
            logger.error(f"更新角色失敗: {str(e)}")
            return False
    
    def delete_role(self, role_id: str) -> bool:
        """刪除角色"""
        try:
            if role_id not in self.roles:
                return False
            
            del self.roles[role_id]
            return self._save_roles()
        except Exception as e:
            logger.error(f"刪除角色失敗: {str(e)}")
            return False
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """獲取角色"""
        return self.roles.get(role_id)
    
    def list_roles(self) -> Dict[str, Role]:
        """列出所有角色"""
        return self.roles
    
    def import_default_roles(self) -> bool:
        """導入預設角色"""
        default_roles = {
            "fk_helper": {
                "name": "Fight.K 小幫手",
                "description": "一般性諮詢助手，可以回答關於 Fight.K 的基本問題",
                "prompt": "您是「Fight.K 小幫手」，負責回答關於 Fight.K 的一般性問題。請使用友善的語氣，並盡可能提供具體的資訊。",
                "settings": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000,
                    "web_search": True
                }
            },
            "fk_teacher": {
                "name": "Fight.K 教師",
                "description": "專門解答 Fight.K 課程相關問題",
                "prompt": "您是「Fight.K 教師」，精通 Fight.K 的課程內容和教學理念。請依據教材內容提供準確的解答。",
                "settings": {
                    "temperature": 0.5,
                    "top_p": 0.8,
                    "max_tokens": 1500,
                    "web_search": False
                }
            }
        }
        
        try:
            for role_id, data in default_roles.items():
                if role_id not in self.roles:
                    self.roles[role_id] = Role(role_id, data)
            
            return self._save_roles()
        except Exception as e:
            logger.error(f"導入預設角色失敗: {str(e)}")
            return False 