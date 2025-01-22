from typing import Dict, List, Optional
import logging
import re
from shared.database.models import Role
from shared.utils.plugin_manager import PluginManager

logger = logging.getLogger(__name__)

class QueryRouter:
    """查詢路由器，負責分析和路由用戶查詢到適當的處理器"""
    
    def __init__(self):
        self.plugin_manager = PluginManager()
        
        # 定義路由規則
        self.routing_rules = {
            "web_search": [
                r"搜尋\s*(.*)",
                r"查詢\s*(.*)",
                r"找找\s*(.*)",
                r"了解\s*(.*)"
            ],
            "web_browser": [
                r"https?://\S+",
                r"www\.\S+"
            ],
            "youtube": [
                r"https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+",
                r"https?://youtu\.be/[\w-]+"
            ]
        }
    
    def route_query(
        self,
        query: str,
        available_plugins: List[str],
        role: Optional[Role] = None
    ) -> Dict:
        """路由查詢到適當的處理器"""
        try:
            routing_result = {
                "original_query": query,
                "detected_intents": [],
                "selected_plugins": [],
                "modified_query": query
            }
            
            # 檢查角色特定的處理邏輯
            if role:
                self._apply_role_specific_routing(routing_result, role)
            
            # 檢查是否匹配任何插件的處理規則
            for plugin_name, patterns in self.routing_rules.items():
                if plugin_name in available_plugins:
                    for pattern in patterns:
                        matches = re.findall(pattern, query, re.IGNORECASE)
                        if matches:
                            routing_result["detected_intents"].append({
                                "plugin": plugin_name,
                                "matches": matches
                            })
                            routing_result["selected_plugins"].append(plugin_name)
            
            # 根據檢測到的意圖修改查詢
            routing_result = self._modify_query_based_on_intents(routing_result)
            
            return {
                "success": True,
                "routing": routing_result
            }
            
        except Exception as e:
            logger.error(f"路由查詢時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _apply_role_specific_routing(self, routing_result: Dict, role: Role):
        """應用角色特定的路由邏輯"""
        try:
            # 檢查角色是否有特定的插件設置
            role_plugins = role.settings.get("plugins", [])
            if role_plugins:
                routing_result["selected_plugins"].extend(
                    plugin for plugin in role_plugins 
                    if plugin not in routing_result["selected_plugins"]
                )
            
            # 檢查角色是否有特定的查詢修改規則
            query_rules = role.settings.get("query_rules", [])
            for rule in query_rules:
                pattern = rule.get("pattern")
                replacement = rule.get("replacement")
                if pattern and replacement:
                    routing_result["modified_query"] = re.sub(
                        pattern,
                        replacement,
                        routing_result["modified_query"]
                    )
                    
        except Exception as e:
            logger.warning(f"應用角色特定路由時發生錯誤：{str(e)}")
    
    def _modify_query_based_on_intents(self, routing_result: Dict) -> Dict:
        """根據檢測到的意圖修改查詢"""
        modified_query = routing_result["modified_query"]
        
        for intent in routing_result["detected_intents"]:
            plugin_name = intent["plugin"]
            
            if plugin_name == "web_search":
                # 為搜索查詢添加額外上下文
                search_terms = intent["matches"][0]
                modified_query = f"根據網路搜尋 '{search_terms}' 的結果回答"
                
            elif plugin_name == "web_browser":
                # 為網頁內容添加提示
                modified_query += "\n[請根據提供的網頁內容回答]"
                
            elif plugin_name == "youtube":
                # 為 YouTube 內容添加提示
                modified_query += "\n[請根據影片字幕內容回答]"
        
        routing_result["modified_query"] = modified_query
        return routing_result
    
    def register_custom_rule(self, plugin_name: str, pattern: str) -> bool:
        """註冊自定義路由規則"""
        try:
            if plugin_name not in self.routing_rules:
                self.routing_rules[plugin_name] = []
            
            if pattern not in self.routing_rules[plugin_name]:
                self.routing_rules[plugin_name].append(pattern)
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"註冊自定義規則時發生錯誤：{str(e)}")
            return False
