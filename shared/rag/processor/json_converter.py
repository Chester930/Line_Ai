import json
import logging
from typing import Dict, Any, List
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class JsonConverter:
    """將文檔內容轉換為標準化的 JSON 格式"""
    
    def __init__(self):
        self.current_version = "1.0"
    
    def convert_to_json(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """將文件信息轉換為標準化的 JSON 格式"""
        try:
            # 分割內容為段落
            paragraphs = self._split_content(file_info['content'])
            
            # 提取結構化信息
            structure = self._extract_structure(paragraphs)
            
            # 創建 JSON 文檔
            document = {
                "document": {
                    "metadata": {
                        "id": file_info['content_hash'],
                        "version": self.current_version,
                        "original_file": {
                            "name": file_info['file_name'],
                            "type": file_info['file_type'],
                            "size": file_info['file_size'],
                            "path": file_info['file_path'],
                            "created_at": file_info['metadata']['original_file']['created_at'],
                            "modified_at": file_info['metadata']['original_file']['modified_at']
                        },
                        "processing": {
                            "processed_at": file_info['processed_at'],
                            "processor_version": self.current_version
                        }
                    },
                    "content": {
                        "title": structure['title'],
                        "sections": structure['sections'],
                        "paragraphs": paragraphs,
                        "statistics": self._calculate_statistics(paragraphs)
                    }
                }
            }
            
            return document
            
        except Exception as e:
            logger.error(f"JSON 轉換失敗: {str(e)}")
            raise
    
    def _split_content(self, content: str) -> List[Dict[str, Any]]:
        """將內容分割為段落"""
        paragraphs = []
        current_type = "text"
        
        # 分割內容
        raw_paragraphs = content.split('\n\n')
        
        for idx, para in enumerate(raw_paragraphs):
            para = para.strip()
            if not para:
                continue
                
            # 判斷段落類型
            if para.startswith('==='):
                current_type = "heading"
            elif '|' in para:
                current_type = "table"
            elif para.startswith('註釋:'):
                current_type = "note"
            else:
                current_type = "text"
            
            paragraphs.append({
                "id": f"p_{idx}",
                "type": current_type,
                "content": para,
                "position": idx
            })
        
        return paragraphs
    
    def _extract_structure(self, paragraphs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """提取文檔結構"""
        structure = {
            "title": "",
            "sections": []
        }
        
        current_section = None
        
        for para in paragraphs:
            content = para['content']
            
            # 提取標題
            if not structure['title'] and content.startswith('標題:'):
                structure['title'] = content.replace('標題:', '').strip()
                continue
            
            # 識別章節
            if para['type'] == 'heading':
                if current_section:
                    structure['sections'].append(current_section)
                
                current_section = {
                    "id": f"s_{len(structure['sections'])}",
                    "title": content.strip('= '),
                    "paragraphs": []
                }
            elif current_section:
                current_section['paragraphs'].append(para['id'])
        
        # 添加最後一個章節
        if current_section:
            structure['sections'].append(current_section)
        
        return structure
    
    def _calculate_statistics(self, paragraphs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """計算文檔統計信息"""
        stats = {
            "total_paragraphs": len(paragraphs),
            "paragraph_types": {},
            "total_characters": 0,
            "total_words": 0
        }
        
        for para in paragraphs:
            # 統計段落類型
            para_type = para['type']
            stats['paragraph_types'][para_type] = stats['paragraph_types'].get(para_type, 0) + 1
            
            # 統計字符和詞數
            content = para['content']
            stats['total_characters'] += len(content)
            stats['total_words'] += len(re.findall(r'\w+', content))
        
        return stats
