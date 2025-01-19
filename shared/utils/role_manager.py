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
        self.base_prompts = data.get('base_prompts', [])  # 共用 prompts 的 ID 列表
        self.role_prompt = data.get('role_prompt', '')    # 角色特定的 prompt
        self.settings = data.get('settings', {
            'temperature': 0.7,
            'top_p': 0.9,
            'max_tokens': 1000,
            'web_search': False
        })
    
    @property
    def prompt(self) -> str:
        """組合所有 prompts"""
        combined_prompt = ""
        if hasattr(self, '_base_prompts_content'):
            for base_prompt in self._base_prompts_content:
                combined_prompt += f"{base_prompt}\n\n"
        combined_prompt += self.role_prompt
        return combined_prompt.strip()

class RoleManager:
    """角色管理器"""
    
    # 預設的 Prompts 定義
    DEFAULT_PROMPTS = {
        "language": {
            "chinese": {
                "type": "Language",
                "description": "流暢的中文對話",
                "content": "請使用流暢的正體中文進行對話，表達要自然、專業。使用台灣用語和用詞習慣。",
                "is_default": True
            },
            "english": {
                "type": "Language",
                "description": "Professional English",
                "content": "Communicate in fluent English. Use professional terminology when appropriate.",
                "is_default": True
            }
        },
        "tone": {
            "professional": {
                "type": "Tone",
                "description": "專業正式的語氣",
                "content": "使用專業且正式的語氣進行對話，保持適度的距離感，用詞要精準且專業。",
                "is_default": True
            },
            "friendly": {
                "type": "Tone",
                "description": "親切友善的語氣",
                "content": "用親切、友善的語氣交談，讓使用者感到溫暖和放鬆。",
                "is_default": True
            }
        },
        # ... 其他預設 prompts
    }
    
    def __init__(self):
        # 創建 Config 實例
        self.config = Config()
        
        # 使用實例屬性而不是類屬性
        self.config_dir = os.path.join(self.config.DATA_DIR, "config")
        self.roles_file = os.path.join(self.config_dir, "roles.json")
        self.prompts_file = os.path.join(self.config_dir, "custom_prompts.json")
        
        # 確保目錄存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 分別存儲預設和自定義的 prompts
        self.prompts_file = os.path.join(self.config_dir, "custom_prompts.json")
        
        # 加載 prompts
        self.custom_prompts = self._load_prompts()
        self.prompts = self._merge_prompts()
        
        # 加載角色配置
        self._roles_data = self._load_roles()
        # 將 JSON 數據轉換為 Role 對象
        self.roles = {
            role_id: Role(role_id, data) 
            for role_id, data in self._roles_data.items()
        }
        
        # 為每個角色加載共用 prompts 內容
        self._load_base_prompts_for_roles()
    
    def _merge_prompts(self) -> Dict:
        """合併預設和自定義的 prompts"""
        merged = {}
        
        # 添加預設 prompts
        for category, prompts in self.DEFAULT_PROMPTS.items():
            for prompt_id, data in prompts.items():
                full_id = f"default_{category}_{prompt_id}"
                merged[full_id] = {
                    **data,
                    "category": category,
                    "usage_count": 0
                }
        
        # 添加自定義 prompts
        for prompt_id, data in self.custom_prompts.items():
            merged[prompt_id] = data
        
        return merged
    
    def _load_prompts(self) -> Dict:
        """加載共用 prompts"""
        if os.path.exists(self.prompts_file):
            try:
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加載共用 prompts 失敗: {str(e)}")
                return {}
        return {}
    
    def _save_prompts(self) -> bool:
        """保存共用 prompts"""
        try:
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_prompts, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存共用 prompts 失敗: {str(e)}")
            return False
    
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
    
    def _load_base_prompts_for_roles(self):
        """為每個角色加載共用 prompts 內容"""
        for role in self.roles.values():
            role._base_prompts_content = [
                self.prompts.get(prompt_id, '')
                for prompt_id in role.base_prompts
            ]
    
    def create_prompt(self, prompt_id: str, content: str, description: str = "", 
                     prompt_type: str = "Others", category: str = "custom") -> bool:
        """創建新的自定義 prompt"""
        if prompt_id in self.prompts:
            return False
        
        # 只保存自定義的 prompts
        self.custom_prompts[prompt_id] = {
            'content': content,
            'description': description,
            'type': prompt_type,
            'category': category,
            'usage_count': 0,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'is_default': False
        }
        
        # 更新合併的 prompts
        self.prompts = self._merge_prompts()
        return self._save_prompts()
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """刪除 prompt（只能刪除自定義的）"""
        if prompt_id not in self.prompts:
            return False
        
        prompt_data = self.prompts[prompt_id]
        if prompt_data.get('is_default', False):
            return False  # 不能刪除預設 prompt
        
        # 檢查是否有角色正在使用
        for role in self.roles.values():
            if prompt_id in role.base_prompts.values():
                return False
        
        del self.custom_prompts[prompt_id]
        self.prompts = self._merge_prompts()
        return self._save_prompts()
    
    def update_prompt_usage(self, prompt_id: str) -> None:
        """更新 prompt 使用次數"""
        if prompt_id in self.prompts:
            self.prompts[prompt_id]['usage_count'] = self.prompts[prompt_id].get('usage_count', 0) + 1
            self._save_prompts()
    
    def create_role(self, role_id: str, name: str, description: str, 
                   role_prompt: str, base_prompts: Dict[str, str] = None,
                   settings: Dict = None) -> bool:
        """
        創建新角色
        base_prompts: 格式為 {"category": "prompt_id"}
        例如: {
            "language": "chinese",
            "tone": "professional",
            "format": "structured"
        }
        """
        try:
            if role_id in self.roles:
                return False
            
            # 驗證每個類別最多只能選一個 prompt
            if base_prompts:
                categories = set()
                for prompt_id in base_prompts.values():
                    prompt_data = self.prompts.get(prompt_id)
                    if not prompt_data:
                        raise ValueError(f"Prompt {prompt_id} 不存在")
                    category = prompt_data['category']
                    if category in categories:
                        raise ValueError(f"類別 {category} 只能選擇一個 prompt")
                    categories.add(category)
            
            role_data = {
                'name': name,
                'description': description,
                'role_prompt': role_prompt,
                'base_prompts': base_prompts or {},
                'settings': settings or {}
            }
            
            self.roles[role_id] = Role(role_id, role_data)
            self._load_base_prompts_for_roles()
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
        # 首先導入預設的共用 prompts
        default_prompts = {
            "chinese_language": {
                "type": "Language",
                "description": "使用中文對話",
                "content": "請使用流暢的中文與使用者對話，保持自然且專業的表達方式。",
                "usage_count": 0,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "friendly_tone": {
                "type": "Tone",
                "description": "友善的對話語氣",
                "content": "在對話中保持友善、親切的語氣，讓使用者感到舒適。",
                "usage_count": 0,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        for prompt_id, data in default_prompts.items():
            if prompt_id not in self.prompts:
                self.prompts[prompt_id] = data
        self._save_prompts()
        
        # 然後導入預設角色
        default_roles = {
            "fk_helper": {
                "name": "Fight.K 小幫手",
                "description": "一般性諮詢助手",
                "base_prompts": ["chinese_language", "friendly_tone"],
                "role_prompt": "你是「Fight.K 小幫手」，負責回答關於 Fight.K 的一般性問題。",
                "settings": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000,
                    "web_search": True
                }
            }
        }
        
        try:
            for role_id, data in default_roles.items():
                if role_id not in self.roles:
                    self.roles[role_id] = Role(role_id, data)
            
            self._load_base_prompts_for_roles()
            return self._save_roles()
        except Exception as e:
            logger.error(f"導入預設角色失敗: {str(e)}")
            return False
    
    def get_prompts_by_category(self, category: str) -> Dict:
        """獲取特定類別的所有 prompts"""
        return {
            k: v for k, v in self.prompts.items()
            if v.get('category') == category
        }
    
    def get_available_prompts(self) -> Dict:
        """獲取所有可用的 prompts（包括預設和自定義）"""
        return self.prompts