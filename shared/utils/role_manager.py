import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, List, Any
from shared.config.config import Config
from pathlib import Path

logger = logging.getLogger(__name__)

class Role:
    def __init__(self, role_id: str, data: Dict):
        self.id = role_id
        self.name = data.get('name', '')
        self.description = data.get('description', '')
        self.base_prompts = data.get('base_prompts', [])  # 共用 prompts 的 ID 列表
        self.role_prompt = data.get('role_prompt', '')    # 角色特定的 prompt
        self.settings = data.get('settings', {
            'temperature': 0.7,
            'top_p': 0.9,
            'max_tokens': 1000,
            'web_search': False
        })
    
    @property
    def prompt(self) -> str:
        """組合所有 prompts"""
        combined_prompt = ""
        if hasattr(self, '_base_prompts_content'):
            for base_prompt in self._base_prompts_content:
                combined_prompt += f"{base_prompt}\n\n"
        combined_prompt += self.role_prompt
        return combined_prompt.strip()

class RoleManager:
    """角色管理器"""
    
    # 預設的 Prompts 定義
    DEFAULT_PROMPTS = {
        "language": {
            "traditional_chinese": {
                "type": "Language",
                "description": "流暢的繁體中文對話",
                "content": "請使用流暢的正體中文進行對話，表達要自然、專業。使用台灣用語和用詞習慣。回應時請維持繁體中文輸出。",
                "is_default": True
            },
            "simplified_chinese": {
                "type": "Language",
                "description": "流畅的简体中文对话",
                "content": "请使用流畅的简体中文进行对话，表达要自然、专业。使用中国大陆用语和用词习惯。回应时请维持简体中文输出。",
                "is_default": True
            },
            "english": {
                "type": "Language",
                "description": "Professional English Communication",
                "content": "Please communicate in fluent English. Use natural and professional expressions. Maintain English output in all responses.",
                "is_default": True
            },
            "japanese": {
                "type": "Language",
                "description": "自然な日本語での会話",
                "content": "自然で丁寧な日本語でコミュニケーションを取ってください。専門用語が必要な場合は適切に使用し、すべての返答は日本語で行ってください。",
                "is_default": True
            },
            "korean": {
                "type": "Language",
                "description": "자연스러운 한국어 대화",
                "content": "자연스럽고 전문적인 한국어로 대화해 주세요. 모든 응답은 한국어로 유지해 주세요. 필요한 경우 전문 용어를 적절히 사용해 주세요.",
                "is_default": True
            }
        },
        "tone": {
            "default": {
                "type": "Tone",
                "description": "預設語氣 (Default Tone)",
                "content": "使用中性且自然的語氣進行對話，根據上下文靈活調整表達方式。",
                "is_default": True
            },
            "formal": {
                "type": "Tone",
                "description": "正式語氣 (Formal)",
                "content": "使用正式且規範的語言進行溝通，保持專業的表達方式和適當的禮節。",
                "is_default": True
            },
            "informal": {
                "type": "Tone",
                "description": "輕鬆隨意 (Informal)",
                "content": "使用輕鬆自然的語氣交談，像朋友間的對話一樣，但保持適度的禮貌。",
                "is_default": True
            },
            "friendly": {
                "type": "Tone",
                "description": "友善親切 (Friendly)",
                "content": "用溫和親切的語氣交談，展現關懷和善意，讓對話充滿正面能量。",
                "is_default": True
            },
            "warm": {
                "type": "Tone",
                "description": "溫暖體貼 (Warm)",
                "content": "以溫暖關懷的態度進行對話，展現同理心和支持。",
                "is_default": True
            },
            "serious": {
                "type": "Tone",
                "description": "嚴肅認真 (Serious)",
                "content": "使用嚴謹且認真的語氣，強調事情的重要性和專注度。",
                "is_default": True
            },
            "humorous": {
                "type": "Tone",
                "description": "幽默風趣 (Humorous)",
                "content": "在對話中適時加入幽默元素，讓交談更加輕鬆愉快，但不失專業性。",
                "is_default": True
            },
            "empathetic": {
                "type": "Tone",
                "description": "同理共情 (Empathetic)",
                "content": "展現強烈的同理心，理解並認同對方的感受，提供情感上的支持。",
                "is_default": True
            },
            "confident": {
                "type": "Tone",
                "description": "自信堅定 (Confident)",
                "content": "以自信且堅定的語氣表達，展現專業知識和確定性。",
                "is_default": True
            },
            "authoritative": {
                "type": "Tone",
                "description": "權威專業 (Authoritative)",
                "content": "使用專業權威的語氣，展現深厚的知識背景和可信度。",
                "is_default": True
            },
            "clinical": {
                "type": "Tone",
                "description": "客觀中立 (Clinical)",
                "content": "使用客觀且中立的語氣，避免情感色彩，專注於事實陳述。",
                "is_default": True
            },
            "playful": {
                "type": "Tone",
                "description": "俏皮活潑 (Playful)",
                "content": "使用活潑有趣的語氣，讓對話充滿趣味性和創意。",
                "is_default": True
            },
            "optimistic": {
                "type": "Tone",
                "description": "樂觀積極 (Optimistic)",
                "content": "保持積極正面的語氣，強調希望和可能性。",
                "is_default": True
            },
            "sympathetic": {
                "type": "Tone",
                "description": "同情關懷 (Sympathetic)",
                "content": "表達理解和關懷，在對方遇到困難時提供安慰和支持。",
                "is_default": True
            },
            "cold": {
                "type": "Tone",
                "description": "冷淡疏離 (Cold)",
                "content": "使用冷靜且疏離的語氣，保持情感距離，回應簡短直接。",
                "is_default": True
            },
            "cynical": {
                "type": "Tone",
                "description": "憤世嫉俗 (Cynical)",
                "content": "以批判和懷疑的態度表達，指出事物的矛盾和問題。",
                "is_default": True
            },
            "emotional": {
                "type": "Tone",
                "description": "情緒化 (Emotional)",
                "content": "展現強烈的情感表達，讓回應充滿感情色彩。",
                "is_default": True
            },
            "ironic": {
                "type": "Tone",
                "description": "諷刺反諷 (Ironic)",
                "content": "使用反諷的方式表達，透過對比突顯觀點。",
                "is_default": True
            },
            "pessimistic": {
                "type": "Tone",
                "description": "悲觀消極 (Pessimistic)",
                "content": "從消極的角度思考和表達，指出潛在的風險和問題。",
                "is_default": True
            },
            "sarcastic": {
                "type": "Tone",
                "description": "尖銳諷刺 (Sarcastic)",
                "content": "使用尖銳且具有諷刺意味的語氣，強調批評和不認同。",
                "is_default": True
            },
            "tentative": {
                "type": "Tone",
                "description": "猶豫保守 (Tentative)",
                "content": "採用謹慎且保守的表達方式，避免做出明確的判斷或承諾。",
                "is_default": True
            }
        },
        "output_format": {
            "default": {
                "type": "Format",
                "description": "預設格式 (Default Format)",
                "content": "根據內容性質，自動選擇最適合的格式來組織和呈現信息。",
                "is_default": True
            },
            "markdown": {
                "type": "Format",
                "description": "Markdown 格式 (Markdown Format)",
                "content": "使用 Markdown 語法格式化輸出，包含標題、列表、代碼塊、引用等元素。",
                "is_default": True
            },
            "bullet_list": {
                "type": "Format",
                "description": "項目符號列表 (Bullet List)",
                "content": "使用項目符號列表來組織信息，讓內容更有條理且易於閱讀。",
                "is_default": True
            },
            "numbered_list": {
                "type": "Format",
                "description": "編號列表 (Numbered List)",
                "content": "使用編號列表來組織信息，適合表達步驟或排序內容。",
                "is_default": True
            },
            "table": {
                "type": "Format",
                "description": "表格形式 (Table Format)",
                "content": "使用表格來組織和比較數據，適合呈現結構化信息。",
                "is_default": True
            },
            "qa": {
                "type": "Format",
                "description": "問答形式 (Q&A Format)",
                "content": "使用問答形式來組織內容，適合解釋概念和常見問題。",
                "is_default": True
            },
            "paragraph": {
                "type": "Format",
                "description": "段落形式 (Paragraph Format)",
                "content": "使用結構化的段落來組織內容，適合詳細說明和論述。",
                "is_default": True
            }
        },
        "writing_style": {
            "default": {
                "type": "WritingStyle",
                "description": "預設寫作風格 (Default Style)",
                "content": "使用清晰、專業的寫作風格，根據內容需求靈活調整。",
                "is_default": True
            },
            "academic": {
                "type": "WritingStyle",
                "description": "學術寫作 (Academic)",
                "content": "使用嚴謹的學術寫作風格，包含適當的引用和專業術語。",
                "is_default": True
            },
            "creative": {
                "type": "WritingStyle",
                "description": "創意寫作 (Creative)",
                "content": "使用富有創意和想像力的寫作風格，生動有趣。",
                "is_default": True
            },
            "technical": {
                "type": "WritingStyle",
                "description": "技術寫作 (Technical)",
                "content": "使用精確的技術寫作風格，清晰說明細節和步驟。",
                "is_default": True
            },
            "journalistic": {
                "type": "WritingStyle",
                "description": "新聞寫作 (Journalistic)",
                "content": "使用新聞報導的寫作風格，客觀呈現事實。",
                "is_default": True
            }
        },
        "personality": {
            # MBTI 16型人格
            "INTJ": {
                "type": "MBTI",
                "description": "策畫者 (INTJ)",
                "content": "展現邏輯願景型性格，具有強大的理性思考能力，擅長創造新理論與評估不同想法。重視邏輯分析，追求效率與系統改進。",
                "is_default": True
            },
            "INTP": {
                "type": "MBTI", 
                "description": "建築師 (INTP)",
                "content": "展現洞察分析型性格，熱衷於獨立分析和解決複雜問題。喜歡利用獨處時間深入分析和評估不同的構想和理念。",
                "is_default": True
            },
            "ENTJ": {
                "type": "MBTI",
                "description": "陸軍元帥 (ENTJ)", 
                "content": "展現洞察果斷型性格，善於基於長遠目標制定策略，建立和改進工作架構。具備優秀的領導能力。",
                "is_default": True
            },
            "ENTP": {
                "type": "MBTI",
                "description": "發明家 (ENTP)",
                "content": "展現邏輯探索型性格，善於創造複雜的理論體系，喜歡創新和解決問題。思維靈活，適應力強。",
                "is_default": True
            },
            "ISTJ": {
                "type": "MBTI",
                "description": "調查員 (ISTJ)",
                "content": "展現邏輯縝密型性格，做事果斷理性，關注效率。擅長覺察和改正不合理狀況，處事獨立認真。",
                "is_default": True
            },
            "ISFJ": {
                "type": "MBTI",
                "description": "保護者 (ISFJ)",
                "content": "展現感性縝密型性格，喜歡與團隊一起努力，為成員提供協調和幫助。注重細節，富有同理心。",
                "is_default": True
            },
            "ESTJ": {
                "type": "MBTI",
                "description": "監督者 (ESTJ)",
                "content": "展現務實果斷型性格，善於管理和監督，重視傳統與規則。做事有條理，注重結果。",
                "is_default": True
            },
            "ESFJ": {
                "type": "MBTI",
                "description": "協調者 (ESFJ)",
                "content": "展現務實貢獻型性格，善於觀察他人需求並提供幫助。重視和諧關係，具有良好的溝通能力。",
                "is_default": True
            },
            "INFJ": {
                "type": "MBTI",
                "description": "勸導者 (INFJ)",
                "content": "展現感性願景型性格，具有超凡的洞察力和同理心。善於理解他人，喜歡幫助他人發展。",
                "is_default": True
            },
            "INFP": {
                "type": "MBTI",
                "description": "化解者 (INFP)",
                "content": "展現洞察關顧型性格，理想主義者，富有同情心。善於表達創意，重視個人價值觀。",
                "is_default": True
            },
            "ENFJ": {
                "type": "MBTI",
                "description": "教師 (ENFJ)",
                "content": "展現洞察貢獻型性格，富有魅力與同理心。善於激勵他人，樂於幫助他人成長。",
                "is_default": True
            },
            "ENFP": {
                "type": "MBTI",
                "description": "元氣者 (ENFP)",
                "content": "展現感性探索型性格，熱情活潑，充滿創意。善於發現可能性，樂於激勵他人。",
                "is_default": True
            },
            "ISFP": {
                "type": "MBTI",
                "description": "藝術家 (ISFP)",
                "content": "展現務實關顧型性格，具有藝術氣質，對美感敏銳。重視和諧，樂於幫助他人。",
                "is_default": True
            },
            "ISTP": {
                "type": "MBTI",
                "description": "巧匠 (ISTP)",
                "content": "展現務實分析型性格，善於解決實際問題。具有靈活的思維，喜歡動手操作。",
                "is_default": True
            },
            "ESFP": {
                "type": "MBTI",
                "description": "表演者 (ESFP)",
                "content": "展現感性反應型性格，活潑外向，充滿活力。善於社交，樂於娛樂他人。",
                "is_default": True
            },
            "ESTP": {
                "type": "MBTI",
                "description": "創業者 (ESTP)",
                "content": "展現邏輯反應型性格，富有冒險精神，善於解決問題。喜歡挑戰，反應靈敏。",
                "is_default": True
            },

            # 進階個性特質選項
            "outgoing": {
                "type": "Personality",
                "description": "外向活潑 (Outgoing)",
                "content": "展現外向、活潑、開朗的性格，健談熱情，善於社交。",
                "is_default": True
            },
            "straightforward": {
                "type": "Personality",
                "description": "率直爽快 (Straightforward)",
                "content": "展現坦率、率直、爽快的性格，說話直接不拐彎抹角。",
                "is_default": True
            },
            "carefree": {
                "type": "Personality",
                "description": "豁達不拘 (Carefree)",
                "content": "展現豁達、不拘小節的性格，處事靈活有彈性。",
                "is_default": True
            },
            "impulsive": {
                "type": "Personality",
                "description": "衝動急躁 (Impulsive)",
                "content": "展現衝動、魯莽、急躁的性格，行事果斷但欠缺思考。",
                "is_default": True
            },
            "determined": {
                "type": "Personality",
                "description": "堅毅果斷 (Determined)",
                "content": "展現意志堅定、果斷、堅毅不屈的性格，面對困難永不放棄。",
                "is_default": True
            },
            
            # 內向謹慎類
            "introverted": {
                "type": "Personality",
                "description": "內向文靜 (Introverted)",
                "content": "展現內向、文靜、沉默寡言的性格，喜歡獨處思考。",
                "is_default": True
            },
            "meticulous": {
                "type": "Personality",
                "description": "細心謹慎 (Meticulous)",
                "content": "展現細心、謹慎、一絲不苟的性格，做事認真有條理。",
                "is_default": True
            },
            "gentle": {
                "type": "Personality",
                "description": "溫文爾雅 (Gentle)",
                "content": "展現溫文有禮、談吐得體的性格，待人親切和善。",
                "is_default": True
            },
            "mature": {
                "type": "Personality",
                "description": "成熟穩重 (Mature)",
                "content": "展現成熟、穩重、冷靜的性格，處事沉著理性。",
                "is_default": True
            },
            
            # 善良正直類
            "kindhearted": {
                "type": "Personality",
                "description": "善良仁厚 (Kindhearted)",
                "content": "展現善良、宅心仁厚的性格，樂於助人，待人寬厚。",
                "is_default": True
            },
            "honest": {
                "type": "Personality",
                "description": "誠實守信 (Honest)",
                "content": "展現誠實、有信用的性格，言行一致，重信守諾。",
                "is_default": True
            },
            "righteous": {
                "type": "Personality",
                "description": "正直公平 (Righteous)",
                "content": "展現正直、公平無私的性格，堅持原則，不徇私情。",
                "is_default": True
            },
            
            # 負面特質類
            "cunning": {
                "type": "Personality",
                "description": "狡猾陰險 (Cunning)",
                "content": "展現狡猾、陰險、刻薄的性格，心機深沉，喜歡算計。",
                "is_default": True
            },
            "selfish": {
                "type": "Personality",
                "description": "自私自利 (Selfish)",
                "content": "展現自私、心胸狹隘的性格，只顧自身利益，不顧他人感受。",
                "is_default": True
            },

            # 才智能力類
            "intelligent": {
                "type": "Personality",
                "description": "聰明睿智 (Intelligent)",
                "content": "展現聰明、精明、學識淵博的性格，思維敏捷，見解獨到。",
                "is_default": True
            },
            "diligent": {
                "type": "Personality",
                "description": "勤奮好學 (Diligent)",
                "content": "展現勤奮、好學不倦的性格，努力上進，追求知識。",
                "is_default": True
            },
            "humble": {
                "type": "Personality",
                "description": "謙虛謹慎 (Humble)",
                "content": "展現謙虛、謹慎的性格，虛心學習，不驕不躁。",
                "is_default": True
            }
        },
        # ... 其他預設 prompts
    }
    
    def __init__(self):
        self.roles_file = Path("data/config/roles.json")
        self.prompts_file = Path("data/config/prompts.json")
        
        # 初始化基本屬性
        self.roles = {}
        self.custom_prompts = {}
        self.prompts = {}
        
        # 載入資料
        self._init_data()
    
    def _init_data(self):
        """初始化所有數據"""
        try:
            # 載入角色設定
            self.roles = self._load_roles()
            
            # 如果沒有任何角色，創建預設角色
            if not self.roles:
                self.import_default_roles()
            
            # 載入提示詞
            self.custom_prompts = self._load_prompts()
            self.prompts = self._merge_prompts()
            
        except Exception as e:
            logger.error(f"初始化數據失敗: {str(e)}")
            # 使用空的數據結構
            self.roles = {}
            self.custom_prompts = {}
            self.prompts = {}
    
    def _merge_prompts(self) -> Dict:
        """合併預設和自定義的 prompts"""
        merged = {}
        
        # 添加預設 prompts
        for category, prompts in self.DEFAULT_PROMPTS.items():
            for prompt_id, data in prompts.items():
                full_id = f"default_{category}_{prompt_id}"
                merged[full_id] = {
                    **data,
                    "category": category,
                    "usage_count": 0
                }
        
        # 添加自定義 prompts
        for prompt_id, data in self.custom_prompts.items():
            merged[prompt_id] = data
        
        return merged
    
    def _load_prompts(self) -> Dict:
        """加載共用 prompts"""
        if os.path.exists(self.prompts_file):
            try:
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加載共用 prompts 失敗: {str(e)}")
                return {}
        return {}
    
    def _save_prompts(self) -> bool:
        """保存共用 prompts"""
        try:
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_prompts, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存共用 prompts 失敗: {str(e)}")
            return False
    
    def _load_roles(self) -> Dict:
        """載入角色設定"""
        if self.roles_file.exists():
            try:
                with open(self.roles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"載入角色設定失敗: {str(e)}")
                return {}
        return {}
    
    def _save_roles(self) -> bool:
        """保存角色設定"""
        try:
            self.roles_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.roles_file, 'w', encoding='utf-8') as f:
                json.dump(self.roles, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存角色設定失敗: {str(e)}")
            return False
    
    def create_prompt(self, prompt_id: str, content: str, description: str = "", 
                     prompt_type: str = "Others", category: str = "custom") -> bool:
        """創建新的自定義 prompt"""
        if prompt_id in self.prompts:
            return False
        
        # 只保存自定義的 prompts
        self.custom_prompts[prompt_id] = {
            'content': content,
            'description': description,
            'type': prompt_type,
            'category': category,
            'usage_count': 0,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'is_default': False
        }
        
        # 更新合併的 prompts
        self.prompts = self._merge_prompts()
        return self._save_prompts()
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """刪除 prompt（只能刪除自定義的）"""
        if prompt_id not in self.prompts:
            return False
        
        prompt_data = self.prompts[prompt_id]
        if prompt_data.get('is_default', False):
            return False  # 不能刪除預設 prompt
        
        # 檢查是否有角色正在使用
        for role_id, role_data in self.roles.items():
            if prompt_id in role_data['base_prompts']:
                return False
        
        del self.custom_prompts[prompt_id]
        self.prompts = self._merge_prompts()
        return self._save_prompts()
    
    def update_prompt_usage(self, prompt_id: str) -> None:
        """更新 prompt 使用次數"""
        if prompt_id in self.prompts:
            self.prompts[prompt_id]['usage_count'] = self.prompts[prompt_id].get('usage_count', 0) + 1
            self._save_prompts()
    
    def create_role(self, role_id: str, name: str, description: str, role_prompt: str,
                    base_prompts: list = None, settings: dict = None) -> bool:
        """創建新角色"""
        try:
            # 檢查 role_id 是否已存在
            if role_id in self.roles:
                logger.warning(f"角色 ID {role_id} 已存在")
                return False
            
            # 驗證 base_prompts
            if base_prompts is None:
                base_prompts = []
            
            # 驗證所有的 prompt_id 是否存在
            available_prompts = self.get_available_prompts()
            for prompt_id in base_prompts:
                if prompt_id not in available_prompts:
                    logger.warning(f"Prompt ID {prompt_id} 不存在")
                    return False
            
            # 使用預設設定
            default_settings = {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1000,
                "web_search": False
            }
            
            # 合併用戶提供的設定
            if settings:
                default_settings.update(settings)
            
            # 創建新角色
            self.roles[role_id] = {
                'name': name,
                'description': description,
                'prompt': role_prompt,
                'settings': default_settings,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # 保存到文件
            self._save_roles()
            logger.info(f"成功創建角色: {role_id}")
            return True
            
        except Exception as e:
            logger.error(f"創建角色失敗: {str(e)}")
            return False
    
    def update_role(self, role_id: str, name: str = None, description: str = None,
                   prompt: str = None, settings: Dict = None) -> bool:
        """更新角色設定"""
        try:
            if role_id not in self.roles:
                return False
            
            role_data = self.roles[role_id]
            if name is not None:
                role_data['name'] = name
            if description is not None:
                role_data['description'] = description
            if prompt is not None:
                role_data['prompt'] = prompt
            if settings is not None:
                role_data['settings'].update(settings)
            
            role_data['updated_at'] = datetime.now().isoformat()
            
            return self._save_roles()
        except Exception as e:
            logger.error(f"更新角色失敗: {str(e)}")
            return False
    
    def delete_role(self, role_id: str) -> bool:
        """刪除角色"""
        try:
            if role_id not in self.roles:
                return False
            
            del self.roles[role_id]
            return self._save_roles()
        except Exception as e:
            logger.error(f"刪除角色失敗: {str(e)}")
            return False
    
    def get_role(self, role_id: str) -> Optional[Dict]:
        """獲取單個角色"""
        role_data = self.roles.get(role_id)
        if role_data:
            return {
                'id': role_id,
                'name': role_data.get('name', role_id),
                'prompt': role_data.get('prompt', ''),
                'settings': role_data.get('settings', {}),
                'created_at': role_data.get('created_at'),
                'updated_at': role_data.get('updated_at')
            }
        return None
    
    def list_roles(self) -> Dict[str, Dict]:
        """列出所有角色"""
        return self.roles
    
    def import_default_roles(self) -> bool:
        """導入預設角色"""
        # 首先導入預設的共用 prompts
        default_prompts = {
            "chinese_language": {
                "type": "Language",
                "description": "使用中文對話",
                "content": "請使用流暢的中文與使用者對話，保持自然且專業的表達方式。",
                "usage_count": 0,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "friendly_tone": {
                "type": "Tone",
                "description": "友善的對話語氣",
                "content": "在對話中保持友善、親切的語氣，讓使用者感到舒適。",
                "usage_count": 0,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        for prompt_id, data in default_prompts.items():
            if prompt_id not in self.prompts:
                self.prompts[prompt_id] = data
        self._save_prompts()
        
        # 然後導入預設角色
        default_roles = {
            "fk_helper": {
                "name": "Fight.K 小幫手",
                "description": "一般性諮詢助手",
                "base_prompts": ["chinese_language", "friendly_tone"],
                "role_prompt": "你是「Fight.K 小幫手」，負責回答關於 Fight.K 的一般性問題。",
                "settings": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000,
                    "web_search": True
                }
            }
        }
        
        try:
            for role_id, data in default_roles.items():
                if role_id not in self.roles:
                    self.roles[role_id] = data
            
            return self._save_roles()
        except Exception as e:
            logger.error(f"導入預設角色失敗: {str(e)}")
            return False
    
    def get_prompts_by_category(self, category: str) -> Dict:
        """獲取特定類別的所有 prompts"""
        if category == "mbti":
            return {k: v for k, v in self.DEFAULT_PROMPTS["personality"].items() 
                   if v.get('type') == "MBTI"}
        elif category == "personality":
            return {k: v for k, v in self.DEFAULT_PROMPTS["personality"].items() 
                   if v.get('type') == "Personality"}
        else:
            return self.DEFAULT_PROMPTS.get(category, {})
    
    def get_available_prompts(self) -> Dict:
        """獲取所有可用的 prompts（包括預設和自定義）"""
        return self.prompts
    
    def get_all_roles(self) -> List[Dict[str, Any]]:
        """獲取所有角色"""
        return [
            {
                'id': role_id,
                'name': role_data.get('name', role_id),
                'prompt': role_data.get('role_prompt', ''),
                'settings': role_data.get('settings', {}),
                'created_at': role_data.get('created_at'),
                'updated_at': role_data.get('updated_at')
            }
            for role_id, role_data in self.roles.items()
        ]