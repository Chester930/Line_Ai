from typing import Dict, Any, List
import requests
from ..utils.plugin_manager import BasePlugin
import logging
from ..config.config import Config

logger = logging.getLogger(__name__)

class WebSearchPlugin(BasePlugin):
    """網路搜尋插件"""
    
    def __init__(self):
        super().__init__(name="web_search", version="1.0.0")
        self.config = {
            "enabled": True,
            "engine": "DuckDuckGo",
            "max_results": 3,
            "weight": 0.3,
            "timeout": 10
        }
        self._load_api_keys()
    
    def _load_api_keys(self):
        """載入 API 金鑰"""
        config = Config()
        self.api_keys = {
            "google_api_key": config.get("GOOGLE_SEARCH_API_KEY", ""),
            "google_cx": config.get("GOOGLE_SEARCH_CX", ""),
            "bing_api_key": config.get("BING_SEARCH_API_KEY", ""),
        }
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            # 檢查必要的配置
            required_fields = ['engine', 'max_results', 'timeout']
            for field in required_fields:
                if field not in self.config:
                    logger.error(f"缺少必要配置: {field}")
                    return False
            
            # 如果使用 DuckDuckGo，不需要檢查 API 金鑰
            engine = self.config['engine']
            if engine == "DuckDuckGo":
                return True
                
            # 檢查其他搜尋引擎的 API 金鑰
            if engine == "Google" and (not self.api_keys['google_api_key'] or not self.api_keys['google_cx']):
                logger.warning("缺少 Google Search API 配置，將使用 DuckDuckGo")
                self.config['engine'] = "DuckDuckGo"
            elif engine == "Bing" and not self.api_keys['bing_api_key']:
                logger.warning("缺少 Bing Search API 配置，將使用 DuckDuckGo")
                self.config['engine'] = "DuckDuckGo"
            
            return True
        except Exception as e:
            logger.error(f"初始化失敗: {e}")
            return False
    
    def execute(self, query: str) -> List[Dict[str, Any]]:
        """執行搜尋"""
        if not self.enabled:
            logger.warning("插件未啟用")
            return []
        
        try:
            engine = self.config['engine']
            max_results = self.config['max_results']
            timeout = self.config['timeout']
            
            if engine == "Google":
                return self._google_search(query, max_results, timeout)
            elif engine == "Bing":
                return self._bing_search(query, max_results, timeout)
            elif engine == "DuckDuckGo":
                return self._duckduckgo_search(query, max_results, timeout)
            else:
                logger.error(f"不支援的搜尋引擎: {engine}")
                return []
        except Exception as e:
            logger.error(f"搜尋失敗: {e}")
            return []
    
    def _google_search(self, query: str, max_results: int, timeout: int) -> List[Dict[str, Any]]:
        """Google 搜尋實現"""
        try:
            api_key = self.api_keys['google_api_key']
            cx = self.api_keys['google_cx']
            
            if not api_key or not cx:
                logger.error("Google Search API 配置不完整")
                return []
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': cx,
                'q': query,
                'num': min(max_results, 10)  # Google API 最多返回10筆結果
            }
            
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            
            results = []
            for item in response.json().get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'Google'
                })
            
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Google 搜尋請求失敗: {e}")
            return []
        except Exception as e:
            logger.error(f"Google 搜尋處理失敗: {e}")
            return []
    
    def _bing_search(self, query: str, max_results: int, timeout: int) -> List[Dict[str, Any]]:
        """Bing 搜尋實現"""
        try:
            api_key = self.api_keys['bing_api_key']
            
            if not api_key:
                logger.error("Bing Search API 配置不完整")
                return []
            
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {
                'Ocp-Apim-Subscription-Key': api_key
            }
            params = {
                'q': query,
                'count': min(max_results, 50)  # Bing API 最多返回50筆結果
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            
            results = []
            for item in response.json().get('webPages', {}).get('value', []):
                results.append({
                    'title': item.get('name', ''),
                    'link': item.get('url', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'Bing'
                })
            
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Bing 搜尋請求失敗: {e}")
            return []
        except Exception as e:
            logger.error(f"Bing 搜尋處理失敗: {e}")
            return []
    
    def _duckduckgo_search(self, query: str, max_results: int, timeout: int) -> List[Dict[str, Any]]:
        """DuckDuckGo 搜尋實現"""
        try:
            # DuckDuckGo 不需要 API 金鑰，使用其公開 API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # 添加即時回答（如果有）
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', ''),
                    'link': data.get('AbstractURL', ''),
                    'snippet': data.get('Abstract', ''),
                    'source': 'DuckDuckGo'
                })
            
            # 添加相關文章
            for article in data.get('RelatedTopics', [])[:max_results]:
                if 'Text' in article and 'FirstURL' in article:
                    results.append({
                        'title': article.get('Text', '').split(' - ')[0],
                        'link': article.get('FirstURL', ''),
                        'snippet': article.get('Text', ''),
                        'source': 'DuckDuckGo'
                    })
            
            return results[:max_results]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"DuckDuckGo 搜尋請求失敗: {e}")
            return []
        except Exception as e:
            logger.error(f"DuckDuckGo 搜尋處理失敗: {e}")
            return [] 