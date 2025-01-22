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
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.default_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
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
            logger.info(f"正在處理 URL: {url}")
            
            # 檢查 URL 格式
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                logger.info(f"已修正 URL 格式: {url}")
            
            # 獲取網頁內容
            content = self._fetch_webpage(url)
            if not content:
                return {"success": False, "error": "無法獲取網頁內容"}
            
            # 解析網頁
            parsed_content = self._parse_content(content)
            logger.info(f"成功解析網頁，標題: {parsed_content.get('title', '無標題')}")
            
            return {
                "success": True,
                "url": url,
                "content": parsed_content
            }
            
        except Exception as e:
            logger.error(f"處理失敗: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _fetch_webpage(self, url: str) -> Optional[str]:
        """獲取網頁內容"""
        try:
            # 基本請求頭
            headers = {
                'User-Agent': self.config.get('user_agent', self.default_user_agent),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # 如果是 Yahoo News，添加特殊處理
            if 'news.yahoo' in url:
                # 移除 guce 相關參數
                url = url.split('?')[0]
                # 添加 Yahoo 特定的請求頭
                headers.update({
                    'Referer': 'https://news.yahoo.com/',
                    'Cookie': 'B=1'  # 基本的 Yahoo cookie
                })
            
            logger.info(f"正在發送請求到: {url}")
            response = requests.get(
                url,
                headers=headers,
                timeout=self.config['timeout'],
                verify=True
            )
            response.raise_for_status()
            
            # 檢查並設置正確的編碼
            if response.encoding.lower() == 'iso-8859-1':
                response.encoding = response.apparent_encoding
            elif not response.encoding and response.apparent_encoding:
                response.encoding = response.apparent_encoding
            
            logger.info(f"成功獲取網頁內容，狀態碼: {response.status_code}, 編碼: {response.encoding}")
            
            # 檢查內容是否為空
            if not response.text.strip():
                logger.error("獲取到的內容為空")
                return None
                
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"獲取網頁失敗: {str(e)}", exc_info=True)
            return None
    
    def _parse_content(self, html_content: str) -> Dict[str, Any]:
        """解析網頁內容"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 1. 清理干擾元素
            noise_tags = [
                'script', 'style', 'meta', 'link', 'iframe', 'nav', 'footer', 
                'header', 'aside', 'sidebar', 'advertisement', 'noscript',
                'button', 'form', 'input'
            ]
            for tag in noise_tags:
                for element in soup.find_all(tag):
                    element.decompose()
            
            # 移除常見的干擾內容區塊
            noise_classes = [
                'related', 'recommend', 'similar', 'sidebar', 'ad', 'advertisement',
                'social', 'share', 'hot', 'popular', 'footer', 'header', 'menu', 'nav',
                '相關', '推薦', '熱門', '分享', '廣告', '導航', '頁尾', '頁首', 'comments',
                'taboola', 'outbrain', 'sponsored', 'promotion', 'wafer-caas'
            ]
            
            # 2. 提取標題
            title = ""
            # 按優先順序嘗試不同的標題元素
            title_candidates = [
                soup.find('meta', property='og:title'),
                soup.find('meta', attrs={'name': 'title'}),
                soup.find('h1', class_=lambda x: x and any(word in str(x).lower() for word in ['title', 'heading', '標題', 'headline'])),
                soup.find('h1', {'data-test-locator': 'headline'}),  # Yahoo News 特定
                soup.find('h1'),
                soup.find('title')
            ]
            for candidate in title_candidates:
                if candidate:
                    if candidate.name == 'meta':
                        title = candidate.get('content', '')
                    else:
                        title = candidate.get_text(strip=True)
                    if title:
                        break
            
            # 3. 提取主要內容
            main_content = ""
            
            # Yahoo News 特定處理
            if soup.find('div', {'data-test-locator': 'articleBody'}):
                content_element = soup.find('div', {'data-test-locator': 'articleBody'})
                main_content = content_element.get_text(separator='\n', strip=True)
            else:
                # 常見的文章內容標識
                content_indicators = [
                    'article', 'content', 'post', 'entry', 'main', 'body', 'text',
                    'article-content', 'post-content', 'entry-content', 'main-content',
                    'article-body', 'story-body', 'news-content', 'caas-body',
                    'wafer-caas-body'
                ]
                
                # 按優先順序嘗試不同的內容提取方法
                content_element = None
                
                # 1. 先找有明確內容標識的元素
                for indicator in content_indicators:
                    # 嘗試 class
                    content_element = soup.find(['article', 'div'], class_=lambda x: x and indicator.lower() in str(x).lower())
                    if content_element:
                        break
                    # 嘗試 id
                    content_element = soup.find(['article', 'div'], id=lambda x: x and indicator.lower() in str(x).lower())
                    if content_element:
                        break
                
                # 2. 如果沒找到，尋找最可能的內容區塊
                if not content_element:
                    # 找出所有段落和文章區塊
                    candidates = []
                    for element in soup.find_all(['article', 'div']):
                        # 檢查是否包含足夠的文本內容
                        text = element.get_text(strip=True)
                        if len(text) > 200 and not any(noise in str(element.get('class', [])).lower() for noise in noise_classes):
                            candidates.append(element)
                    
                    if candidates:
                        # 選擇文本最長的區塊
                        content_element = max(candidates, key=lambda x: len(x.get_text(strip=True)))
                
                # 3. 從內容元素中提取文本
                if content_element:
                    # 移除可能的干擾元素
                    for element in content_element.find_all(class_=lambda x: x and any(noise in str(x).lower() for noise in noise_classes)):
                        element.decompose()
                    
                    # 提取段落
                    paragraphs = content_element.find_all('p')
                    if paragraphs:
                        main_content = '\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
                    else:
                        main_content = content_element.get_text(separator='\n', strip=True)
                else:
                    # 如果還是沒找到，使用所有段落
                    paragraphs = soup.find_all('p')
                    if paragraphs:
                        main_content = '\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
            
            # 4. 清理和格式化文本
            if main_content:
                # 基本清理
                main_content = re.sub(r'\s*\n\s*', '\n', main_content)  # 清理空行
                main_content = re.sub(r' +', ' ', main_content)         # 清理多餘空格
                main_content = re.sub(r'([。！？」』：；])\s*\n*\s*', r'\1\n', main_content)  # 在句尾添加換行
                
                # 移除短行
                lines = [line.strip() for line in main_content.split('\n') if len(line.strip()) > 20]
                main_content = '\n'.join(lines)
            
            logger.info(f"成功解析網頁內容，標題長度: {len(title)}, 內容長度: {len(main_content)}")
            
            if not main_content:
                logger.warning("未能提取到主要內容")
            
            return {
                'title': title,
                'text': main_content[:self.config['max_content_length']],
                'length': len(main_content)
            }
            
        except Exception as e:
            logger.error(f"解析網頁失敗: {str(e)}", exc_info=True)
            return {
                'title': "解析失敗",
                'text': f"無法解析網頁內容: {str(e)}",
                'length': 0
            } 