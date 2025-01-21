from typing import Dict, Any, List, Optional
import requests
from ..utils.plugin_manager import BasePlugin
import logging
from youtube_transcript_api import YouTubeTranscriptApi
import re

logger = logging.getLogger(__name__)

class YouTubeSubtitlePlugin(BasePlugin):
    """YouTube 字幕插件"""
    
    def __init__(self):
        super().__init__(name="youtube_subtitle", version="1.0.0")
        self.config = {
            "enabled": True,
            "preferred_languages": ["zh-TW", "zh-CN", "en"],  # 字幕語言優先順序
            "max_results": 10,  # 搜尋結果數量
            "chunk_size": 500,  # 字幕分段大小
            "include_auto_subtitles": False  # 是否包含自動生成的字幕
        }
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            # 檢查必要的配置
            required_fields = ['preferred_languages', 'max_results', 'chunk_size']
            for field in required_fields:
                if field not in self.config:
                    logger.error(f"缺少必要配置: {field}")
                    return False
            return True
        except Exception as e:
            logger.error(f"初始化失敗: {e}")
            return False
    
    def execute(self, video_url: str) -> Dict[str, Any]:
        """處理 YouTube 影片"""
        if not self.enabled:
            logger.warning("插件未啟用")
            return {"success": False, "error": "插件未啟用"}
        
        try:
            # 解析影片 ID
            video_id = self._extract_video_id(video_url)
            if not video_id:
                return {"success": False, "error": "無效的 YouTube 網址"}
            
            # 獲取字幕
            subtitles = self._get_subtitles(video_id)
            if not subtitles:
                return {"success": False, "error": "無法獲取字幕"}
            
            # 處理字幕內容
            processed_subtitles = self._process_subtitles(subtitles)
            
            return {
                "success": True,
                "video_id": video_id,
                "subtitles": processed_subtitles
            }
            
        except Exception as e:
            logger.error(f"處理失敗: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """從 URL 中提取影片 ID"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu.be\/)([^&\n?]*)',
            r'(?:youtube\.com\/embed\/)([^&\n?]*)',
            r'(?:youtube\.com\/v\/)([^&\n?]*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _get_subtitles(self, video_id: str) -> Optional[List[Dict[str, Any]]]:
        """獲取字幕"""
        try:
            # 獲取可用的字幕列表
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 按照優先順序尋找字幕
            for lang in self.config['preferred_languages']:
                try:
                    # 嘗試獲取指定語言的字幕
                    transcript = transcript_list.find_transcript([lang])
                    if not transcript.is_generated or self.config['include_auto_subtitles']:
                        return transcript.fetch()
                except:
                    continue
            
            # 如果找不到優先語言的字幕，使用預設字幕
            try:
                transcript = transcript_list.find_transcript(['en'])
                if not transcript.is_generated or self.config['include_auto_subtitles']:
                    return transcript.fetch()
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"獲取字幕失敗: {e}")
            return None
    
    def _process_subtitles(self, subtitles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """處理字幕內容"""
        processed = []
        current_chunk = []
        current_text = ""
        
        for subtitle in subtitles:
            # 添加時間戳和文本
            item = {
                'start': subtitle['start'],
                'duration': subtitle['duration'],
                'text': subtitle['text']
            }
            
            # 根據配置的大小分段
            if len(current_text) + len(subtitle['text']) > self.config['chunk_size']:
                # 保存當前分段
                if current_chunk:
                    processed.append({
                        'start_time': current_chunk[0]['start'],
                        'end_time': current_chunk[-1]['start'] + current_chunk[-1]['duration'],
                        'text': current_text.strip(),
                        'segments': current_chunk
                    })
                # 開始新的分段
                current_chunk = [item]
                current_text = subtitle['text']
            else:
                current_chunk.append(item)
                current_text += " " + subtitle['text']
        
        # 處理最後一個分段
        if current_chunk:
            processed.append({
                'start_time': current_chunk[0]['start'],
                'end_time': current_chunk[-1]['start'] + current_chunk[-1]['duration'],
                'text': current_text.strip(),
                'segments': current_chunk
            })
        
        return processed[:self.config['max_results']] 