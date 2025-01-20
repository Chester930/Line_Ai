from typing import List, Dict, Optional
import aiohttp
import logging
from bs4 import BeautifulSoup
import json
from shared.config.config import Config

logger = logging.getLogger(__name__)

class WebSearch:
    """網路搜尋工具"""
    
    def __init__(self):
        self.config = Config()
        self.search_engines = {
            'google': self._search_google,
            'bing': self._search_bing,
            'duckduckgo': self._search_duckduckgo
        }
        
    async def search(
        self,
        query: str,
        max_results: int = 3,
        engine: str = 'google'
    ) -> List[Dict]:
        """執行網路搜尋"""
        try:
            search_func = self.search_engines.get(engine)
            if not search_func:
                raise ValueError(f"不支援的搜尋引擎：{engine}")
            
            results = await search_func(query, max_results)
            
            # 內容摘要和過濾
            processed_results = []
            for result in results:
                # 提取網頁內容
                content = await self._fetch_page_content(result['url'])
                if content:
                    # 生成摘要
                    summary = self._generate_summary(content, query)
                    result['snippet'] = summary
                    processed_results.append(result)
                
                if len(processed_results) >= max_results:
                    break
            
            return processed_results
            
        except Exception as e:
            logger.error(f"網路搜尋失敗：{str(e)}")
            return []
    
    async def _search_google(
        self,
        query: str,
        max_results: int
    ) -> List[Dict]:
        """使用 Google 搜尋"""
        if not self.config.GOOGLE_SEARCH_API_KEY:
            raise ValueError("未設定 Google Search API Key")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.config.GOOGLE_SEARCH_API_KEY,
            'cx': self.config.GOOGLE_SEARCH_ENGINE_ID,
            'q': query,
            'num': max_results
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if 'items' not in data:
                    return []
                
                return [{
                    'title': item['title'],
                    'url': item['link'],
                    'snippet': item['snippet']
                } for item in data['items']]
    
    async def _fetch_page_content(self, url: str) -> Optional[str]:
        """獲取網頁內容"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 移除不必要的元素
                        for tag in soup(['script', 'style']):
                            tag.decompose()
                        
                        return soup.get_text()
                    return None
        except Exception as e:
            logger.error(f"獲取網頁內容失敗：{str(e)}")
            return None
    
    def _generate_summary(self, content: str, query: str, max_length: int = 200) -> str:
        """生成內容摘要"""
        # TODO: 使用更智能的摘要生成方法
        sentences = content.split('。')
        relevant_sentences = []
        
        for sentence in sentences:
            if any(word in sentence.lower() for word in query.lower().split()):
                relevant_sentences.append(sentence)
                
            if len('。'.join(relevant_sentences)) >= max_length:
                break
        
        return '。'.join(relevant_sentences)[:max_length] + '...' 