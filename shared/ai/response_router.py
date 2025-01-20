from typing import List, Dict, Optional
import logging
from shared.ai.knowledge_base import KnowledgeBase
from shared.utils.web_search import WebSearch
from shared.config.config import Config
from shared.ai.query_analyzer import QueryAnalyzer

logger = logging.getLogger(__name__)

class ResponseRouter:
    """智能路由系統"""
    
    def __init__(self):
        self.config = Config()
        self.knowledge_base = KnowledgeBase()
        self.web_search = WebSearch()
        self.query_analyzer = QueryAnalyzer()
        
        # 預設權重設定
        self.default_weights = {
            'knowledge_base': 0.4,  # 知識庫權重
            'web_search': 0.3,      # 網路搜尋權重
            'conversation': 0.2,     # 對話歷史權重
            'role_prompt': 0.1      # 角色設定權重
        }
    
    async def get_context(
        self,
        query: str,
        role_settings: Dict,
        conversation_history: List[Dict] = None
    ) -> Dict:
        """獲取回應所需的上下文"""
        try:
            # 1. 分析查詢意圖和類型
            query_info = self._analyze_query(query)
            
            # 2. 根據設定和查詢類型調整權重
            weights = self._adjust_weights(
                query_info,
                role_settings
            )
            
            # 3. 收集各來源資訊
            context_parts = {}
            
            # 知識庫查詢
            if weights['knowledge_base'] > 0:
                kb_results = self.knowledge_base.query(
                    query,
                    top_k=3,
                    threshold=0.5
                )
                if kb_results:
                    context_parts['knowledge_base'] = {
                        'content': self.knowledge_base.format_context(kb_results),
                        'weight': weights['knowledge_base']
                    }
            
            # 網路搜尋
            if weights['web_search'] > 0:
                web_results = await self.web_search.search(
                    query,
                    max_results=3
                )
                if web_results:
                    context_parts['web_search'] = {
                        'content': self._format_web_results(web_results),
                        'weight': weights['web_search']
                    }
            
            # 對話歷史
            if weights['conversation'] > 0 and conversation_history:
                relevant_history = self._get_relevant_history(
                    query,
                    conversation_history
                )
                if relevant_history:
                    context_parts['conversation'] = {
                        'content': self._format_history(relevant_history),
                        'weight': weights['conversation']
                    }
            
            # 4. 組合上下文
            final_context = self._combine_context(context_parts)
            
            return {
                'success': True,
                'context': final_context,
                'weights': weights,
                'sources': list(context_parts.keys())
            }
            
        except Exception as e:
            logger.error(f"生成上下文時發生錯誤：{str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_query(self, query: str) -> Dict:
        """分析查詢意圖和類型"""
        return self.query_analyzer.analyze(query)
    
    def _adjust_weights(
        self,
        query_info: Dict,
        role_settings: Dict
    ) -> Dict:
        """根據查詢類型和角色設定調整權重"""
        weights = self.default_weights.copy()
        
        # 根據角色設定調整
        if role_settings.get('knowledge_base', {}).get('enabled'):
            weights['knowledge_base'] *= role_settings['knowledge_base']['weight']
        else:
            weights['knowledge_base'] = 0
            
        if role_settings.get('web_search', {}).get('enabled'):
            weights['web_search'] *= role_settings['web_search']['weight']
        else:
            weights['web_search'] = 0
        
        # 根據查詢類型調整
        if query_info['requires_recent_info']:
            weights['web_search'] *= 1.5
        if query_info['is_personal']:
            weights['conversation'] *= 1.5
        
        # 重新歸一化權重
        total = sum(weights.values())
        if total > 0:
            weights = {k: v/total for k, v in weights.items()}
        
        return weights
    
    def _get_relevant_history(
        self,
        query: str,
        history: List[Dict],
        max_turns: int = 5
    ) -> List[Dict]:
        """獲取相關的對話歷史"""
        # TODO: 實現更智能的歷史篩選
        return history[-max_turns:]
    
    def _format_web_results(self, results: List[Dict]) -> str:
        """格式化網路搜尋結果"""
        formatted = "根據網路搜尋結果：\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"{result['snippet']}\n"
            formatted += f"來源：{result['url']}\n\n"
        return formatted.strip()
    
    def _format_history(self, history: List[Dict]) -> str:
        """格式化對話歷史"""
        formatted = "根據之前的對話：\n\n"
        for msg in history:
            role = "用戶" if msg['role'] == 'user' else "助手"
            formatted += f"{role}：{msg['content']}\n"
        return formatted.strip()
    
    def _combine_context(self, parts: Dict[str, Dict]) -> str:
        """組合最終上下文"""
        # 按權重排序
        sorted_parts = sorted(
            parts.items(),
            key=lambda x: x[1]['weight'],
            reverse=True
        )
        
        combined = []
        for _, part in sorted_parts:
            combined.append(part['content'])
        
        return "\n\n".join(combined) 