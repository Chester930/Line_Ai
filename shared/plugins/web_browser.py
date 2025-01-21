from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from ..utils.plugin_manager import BasePlugin
import logging
import re

logger = logging.getLogger(__name__)

class WebBrowserPlugin(BasePlugin):
    """網頁瀏覽插件"""
    
    def __init__(self):
        super().__init__(name="web_browser", version="1.0.0")
        self.config = {
            "enabled": True,
            "timeout": 10,
            "max_content_length": 50000,  # 最大內容長度（字符）
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            required_fields = ['timeout', 'max_content_length']
            for field in required_fields:
                if field not in self.config:
                    logger.error(f"缺少必要配置: {field}")
                    return False
            return True
        except Exception as e:
            logger.error(f"初始化失敗: {e}")
            return False
    
    def execute(self, url: str) -> Dict[str, Any]:
        """訪問並解析網頁"""
        if not self.enabled:
            logger.warning("插件未啟用")
            return {"success": False, "error": "插件未啟用"}
        
        try:
            # 檢查 URL 格式
            if not self._is_valid_url(url):
                return {"success": False, "error": "無效的URL格式"}
            
            # 獲取網頁內容
            content = self._fetch_webpage(url)
            if not content:
                return {"success": False, "error": "無法獲取網頁內容"}
            
            # 解析網頁
            parsed_content = self._parse_content(content)
            
            return {
                "success": True,
                "url": url,
                "content": parsed_content
            }
            
        except Exception as e:
            logger.error(f"處理失敗: {e}")
            return {"success": False, "error": str(e)}
    
    def _is_valid_url(self, url: str) -> bool:
        """檢查 URL 是否有效"""
        url_pattern = re.compile(
            r'^https?://'  # http:// 或 https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    def _fetch_webpage(self, url: str) -> Optional[str]:
        """獲取網頁內容"""
        try:
            headers = {'User-Agent': self.config['user_agent']}
            response = requests.get(
                url,
                headers=headers,
                timeout=self.config['timeout'],
                verify=True  # 驗證 SSL 證書
            )
            response.raise_for_status()
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"獲取網頁失敗: {e}")
            return None
    
    def _parse_content(self, html_content: str) -> Dict[str, Any]:
        """解析網頁內容"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除腳本和樣式標籤
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 獲取標題
            title = soup.title.string if soup.title else ""
            
            # 獲取主要文本內容
            text = soup.get_text(separator='\n', strip=True)
            
            # 獲取所有鏈接
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):  # 只保留完整的URL
                    links.append({
                        'text': link.get_text(strip=True),
                        'url': href
                    })
            
            # 限制內容長度
            if len(text) > self.config['max_content_length']:
                text = text[:self.config['max_content_length']] + "..."
            
            return {
                'title': title,
                'text': text,
                'links': links[:10],  # 限制返回的鏈接數量
                'length': len(text)
            }
            
        except Exception as e:
            logger.error(f"解析網頁失敗: {e}")
            return {
                'title': "",
                'text': "",
                'links': [],
                'length': 0
            } 