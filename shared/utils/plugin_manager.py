import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BasePlugin(ABC):
    """插件基類"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = False
        self.config = {}
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """執行插件功能"""
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """獲取插件配置"""
        return self.config
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """更新插件配置"""
        self.config.update(config)
        return True

class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.config_path = Path("config/plugins.json")
        self.plugins: Dict[str, BasePlugin] = {}
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
    
    def register_plugin(self, plugin: BasePlugin) -> bool:
        """註冊插件"""
        try:
            plugin_name = plugin.name
            self.plugins[plugin_name] = plugin
            
            # 載入已存在的配置
            if plugin_name in self.config:
                plugin.config = self.config[plugin_name]
                plugin.enabled = plugin.config.get('enabled', False)
            
            return True
        except Exception as e:
            logger.error(f"註冊插件失敗: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """獲取插件實例"""
        return self.plugins.get(plugin_name)
    
    def get_plugin_config(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """獲取插件配置"""
        return self.config.get(plugin_name)
    
    def update_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """更新插件配置"""
        try:
            self.config[plugin_name] = config
            
            # 如果插件已註冊，同時更新插件實例的配置
            if plugin_name in self.plugins:
                self.plugins[plugin_name].update_config(config)
            
            return self._save_config(self.config)
        except Exception as e:
            logger.error(f"更新插件配置失敗: {e}")
            return False
    
    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """檢查插件是否啟用"""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return plugin.enabled
        plugin_config = self.get_plugin_config(plugin_name)
        return plugin_config.get('enabled', False) if plugin_config else False
    
    def get_all_plugins(self) -> List[BasePlugin]:
        """獲取所有已註冊的插件"""
        return list(self.plugins.values()) 