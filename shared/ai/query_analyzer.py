from typing import Dict, List
import re
import jieba
import jieba.analyse
from datetime import datetime
from shared.config.config import Config

class QueryAnalyzer:
    """查詢分析器"""
    
    def __init__(self):
        self.config = Config()
        # 載入自定義詞典
        self._load_custom_dict()
        
        # 關鍵詞模式
        self.patterns = {
            'time_related': r'最近|現在|目前|最新|最後|剛才|最近|今天|昨天|明天',
            'calculation': r'計算|算出|求|等於|加|減|乘|除|總共|平均',
            'personal': r'我|我的|你|你的|我們|他|她|他們|自己',
            'comparison': r'比較|差異|區別|不同|相同|一樣|差別',
            'definition': r'是什麼|定義|解釋|說明|介紹|意思是|代表',
            'procedure': r'如何|怎麼|步驟|方法|流程|操作|使用'
        }
    
    def analyze(self, query: str) -> Dict:
        """分析查詢"""
        # 基本分析結果
        analysis = {
            'type': 'general',
            'requires_recent_info': False,
            'requires_calculation': False,
            'is_personal': False,
            'is_comparison': False,
            'is_definition': False,
            'is_procedure': False,
            'keywords': [],
            'confidence': 0.0
        }
        
        # 提取關鍵詞
        keywords = jieba.analyse.extract_tags(
            query,
            topK=5,
            withWeight=True
        )
        analysis['keywords'] = keywords
        
        # 模式匹配
        for pattern_name, pattern in self.patterns.items():
            if re.search(pattern, query):
                if pattern_name == 'time_related':
                    analysis['requires_recent_info'] = True
                elif pattern_name == 'calculation':
                    analysis['requires_calculation'] = True
                elif pattern_name == 'personal':
                    analysis['is_personal'] = True
                elif pattern_name == 'comparison':
                    analysis['is_comparison'] = True
                elif pattern_name == 'definition':
                    analysis['is_definition'] = True
                elif pattern_name == 'procedure':
                    analysis['is_procedure'] = True
        
        # 確定查詢類型
        analysis['type'] = self._determine_query_type(analysis)
        
        # 計算置信度
        analysis['confidence'] = self._calculate_confidence(analysis)
        
        return analysis
    
    def _determine_query_type(self, analysis: Dict) -> str:
        """確定查詢類型"""
        if analysis['requires_calculation']:
            return 'calculation'
        elif analysis['is_definition']:
            return 'definition'
        elif analysis['is_procedure']:
            return 'procedure'
        elif analysis['is_comparison']:
            return 'comparison'
        elif analysis['requires_recent_info']:
            return 'recent_info'
        elif analysis['is_personal']:
            return 'personal'
        return 'general'
    
    def _calculate_confidence(self, analysis: Dict) -> float:
        """計算分析結果的置信度"""
        confidence = 0.0
        
        # 根據關鍵詞權重
        if analysis['keywords']:
            max_weight = max(weight for _, weight in analysis['keywords'])
            confidence += max_weight * 0.4
        
        # 根據模式匹配結果
        pattern_matches = sum([
            analysis['requires_recent_info'],
            analysis['requires_calculation'],
            analysis['is_personal'],
            analysis['is_comparison'],
            analysis['is_definition'],
            analysis['is_procedure']
        ])
        if pattern_matches > 0:
            confidence += 0.3
        
        # 根據查詢類型
        if analysis['type'] != 'general':
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _load_custom_dict(self):
        """載入自定義詞典"""
        # TODO: 從配置文件載入自定義詞典
        pass 