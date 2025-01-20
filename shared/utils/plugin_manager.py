import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.config_path = Path("config/plugins.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """載入插件配置"""
        if not self.config_path.exists():
            default_config = {
                "web_search": {
                    "enabled": True,
                    "engine": "Google",
                    "max_results": 3,
                    "weight": 0.3,
                    "timeout": 10
                },
                "knowledge_base": {
                    "enabled": True,
                    "embedding_model": "sentence-transformers",
                    "chunk_size": 500,
                    "weight": 0.5,
                    "similarity_threshold": 0.7
                }
            }
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入插件配置失敗: {e}")
            return {}
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """儲存插件配置"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"儲存插件配置失敗: {e}")
            return False
    
    def get_plugin_config(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """獲取插件配置"""
        return self.config.get(plugin_name)
    
    def update_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """更新插件配置"""
        try:
            self.config[plugin_name] = config
            return self._save_config(self.config)
        except Exception as e:
            logger.error(f"更新插件配置失敗: {e}")
            return False
    
    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """檢查插件是否啟用"""
        plugin_config = self.get_plugin_config(plugin_name)
        return plugin_config.get('enabled', False) if plugin_config else False 