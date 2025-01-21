MODEL_DESCRIPTIONS = {
    "OpenAI 模型": {
        "GPT-4o": {
            "name": "GPT-4o",
            "description": "OpenAI 最新的多功能旗艦模型，具備最高智能水平和多樣化能力",
            "features": ["強大的推理能力", "複雜任務處理", "多領域專業知識", "即時互動"],
            "use_cases": ["專業諮詢", "深度分析", "創意寫作", "多步驟任務"],
            "model_ids": {
                "openai": "gpt-4o"
            }
        },
        "GPT-4o-mini": {
            "name": "GPT-4o-mini",
            "description": "快速、經濟實惠的小型模型，適合專注的任務處理",
            "features": ["快速響應", "資源佔用低", "專注任務處理"],
            "use_cases": ["簡單對話", "特定領域任務", "快速查詢"],
            "model_ids": {
                "openai": "gpt-4o-mini"
            }
        },
        "o1": {
            "name": "o1",
            "description": "專注於複雜推理的高級模型，擅長多步驟任務",
            "features": ["強大推理能力", "多步驟任務處理", "邏輯分析"],
            "use_cases": ["複雜問題解決", "邏輯推理", "決策分析"],
            "model_ids": {
                "openai": "o1"
            }
        },
        "o1-mini": {
            "name": "o1-mini",
            "description": "o1 的輕量版本，保持核心推理能力",
            "features": ["基礎推理能力", "快速響應", "資源效率"],
            "use_cases": ["基礎推理任務", "快速分析", "簡單決策"],
            "model_ids": {
                "openai": "o1-mini"
            }
        },
        "GPT-4o Realtime": {
            "name": "GPT-4o Realtime",
            "description": "支援即時文本和音頻輸入輸出的 GPT-4o 版本",
            "features": ["即時互動", "音頻處理", "多模態輸入輸出"],
            "use_cases": ["即時對話", "語音互動", "實時翻譯"],
            "model_ids": {
                "openai": "gpt-4o-realtime"
            }
        },
        "GPT-4o Audio": {
            "name": "GPT-4o Audio",
            "description": "通過 REST API 支援音頻輸入輸出的 GPT-4o 版本",
            "features": ["音頻處理", "API 集成", "語音互動"],
            "use_cases": ["語音應用", "音頻處理", "語音助手"],
            "model_ids": {
                "openai": "gpt-4o-audio"
            }
        },
        "GPT-4 Turbo": {
            "name": "GPT-4 Turbo",
            "description": "先前的高智能模型系列，仍具備強大能力",
            "features": ["強大的推理能力", "複雜任務處理", "多領域知識"],
            "use_cases": ["專業諮詢", "深度分析", "創意寫作"],
            "model_ids": {
                "openai": "gpt-4-turbo-preview"
            }
        },
        "GPT-3.5 Turbo": {
            "name": "GPT-3.5 Turbo",
            "description": "適合簡單任務的快速模型，已被 GPT-4o-mini 取代",
            "features": ["快速響應", "資源佔用低", "基礎對話"],
            "use_cases": ["簡單對話", "基礎查詢", "文本處理"],
            "model_ids": {
                "openai": "gpt-3.5-turbo"
            }
        }
    },
    
    "Google Gemini 模型": {
        "Gemini 2.0 Flash": {
            "name": "Gemini 2.0 Flash",
            "description": "Google 最新的多模態模型，支援多種輸入和輸出格式",
            "features": [
                "多模態輸入（音訊、圖片、影片、文字）",
                "多模態輸出（文字、圖片*、音訊*）",
                "新一代處理速度",
                "強大的生成能力"
            ],
            "use_cases": ["通用任務", "多模態處理", "即時應用"],
            "model_ids": {
                "google": "gemini-2.0-flash-exp"
            },
            "note": "* 圖片和音訊輸出功能即將推出"
        },
        "Gemini 1.5 Flash": {
            "name": "Gemini 1.5 Flash",
            "description": "快速且多功能的模型，適合各種任務",
            "features": [
                "多模態輸入支援",
                "快速響應",
                "靈活應用"
            ],
            "use_cases": ["通用任務", "快速處理", "多模態應用"],
            "model_ids": {
                "google": "gemini-1.5-flash"
            }
        },
        "Gemini 1.5 Flash-8B": {
            "name": "Gemini 1.5 Flash-8B",
            "description": "輕量級模型，適合大量簡單任務處理",
            "features": [
                "多模態輸入支援",
                "高效能處理",
                "適合批量任務"
            ],
            "use_cases": ["批量處理", "簡單任務", "效率優先"],
            "model_ids": {
                "google": "gemini-1.5-flash-8b"
            }
        },
        "Gemini 1.5 Pro": {
            "name": "Gemini 1.5 Pro",
            "description": "專業版本，適合需要深度思考的複雜任務",
            "features": [
                "強大的推理能力",
                "複雜任務處理",
                "多模態理解"
            ],
            "use_cases": ["複雜推理", "專業分析", "深度任務"],
            "model_ids": {
                "google": "gemini-1.5-pro"
            }
        },
        "Gemini 1.0 Pro": {
            "name": "Gemini 1.0 Pro",
            "description": "適合文字和程式碼處理的通用模型",
            "features": [
                "自然語言處理",
                "程式碼生成",
                "多輪對話"
            ],
            "use_cases": ["程式開發", "文字處理", "對話應用"],
            "model_ids": {
                "google": "gemini-1.0-pro"
            },
            "deprecated": True,
            "deprecated_date": "2024-02-15"
        },
        "Text Embedding": {
            "name": "Text Embedding",
            "description": "專門用於文字嵌入的模型",
            "features": [
                "文字向量化",
                "相似度計算",
                "語義分析"
            ],
            "use_cases": ["文本分析", "相似度比較", "搜索優化"],
            "model_ids": {
                "google": "text-embedding-004"
            }
        },
        "AQA": {
            "name": "AQA (Air Quality Assurance)",
            "description": "專注於提供可靠來源解答的模型",
            "features": [
                "高準確度",
                "來源可靠",
                "答案品質保證"
            ],
            "use_cases": ["事實查證", "專業諮詢", "可靠資訊提供"],
            "model_ids": {
                "google": "aqa"
            }
        }
    },
    
    "Claude 模型": {
        "Claude 3 Opus": {
            "name": "Claude 3 Opus",
            "description": "Anthropic 最新的旗艦模型，具備強大的分析和推理能力",
            "features": ["多模態理解", "高效能處理", "複雜任務處理"],
            "use_cases": ["專業諮詢", "深度分析", "複雜問題解決"],
            "model_ids": {
                "anthropic": "claude-3-opus-20240229"
            }
        },
        "Claude 3 Sonnet": {
            "name": "Claude 3 Sonnet",
            "description": "Anthropic 最新的旗艦模型，具備強大的分析和推理能力",  # 與 Claude 3 Opus 共用說明
            "features": ["多模態理解", "高效能處理", "複雜任務處理"],
            "use_cases": ["專業諮詢", "深度分析", "複雜問題解決"],
            "model_ids": {
                "anthropic": "claude-3-sonnet-20240229"
            }
        }
    },
    
    "專業工具模型": {
        "DALL·E": {
            "name": "DALL·E",
            "description": "能夠根據自然語言提示生成和編輯圖像的模型",
            "features": ["圖像生成", "圖像編輯", "創意設計"],
            "use_cases": ["藝術創作", "設計原型", "視覺概念"]
        },
        "TTS": {
            "name": "TTS (Text-to-Speech)",
            "description": "將文本轉換為自然語音的模型系列",
            "features": ["文本轉語音", "自然發音", "多語言支援"],
            "use_cases": ["有聲內容", "語音助手", "無障礙應用"]
        },
        "Whisper": {
            "name": "Whisper",
            "description": "將音頻轉換為文本的模型",
            "features": ["語音識別", "多語言支援", "噪音處理"],
            "use_cases": ["語音轉錄", "字幕生成", "會議記錄"]
        },
        "Embeddings": {
            "name": "Embeddings",
            "description": "將文本轉換為數值形式的模型系列",
            "features": ["文本向量化", "語義分析", "相似度計算"],
            "use_cases": ["文本分類", "搜索優化", "推薦系統"]
        },
        "Moderation": {
            "name": "Moderation",
            "description": "檢測文本是否包含敏感或不安全內容的模型",
            "features": ["內容審核", "敏感詞檢測", "安全過濾"],
            "use_cases": ["內容管理", "社區監控", "安全審查"]
        }
    }
}

def get_model_info(model_name: str) -> dict:
    """獲取指定模型的詳細信息"""
    for category in MODEL_DESCRIPTIONS.values():
        if model_name in category:
            return category[model_name]
    return None

def get_available_models(category: str = None) -> list:
    """獲取可用的模型列表"""
    if category and category in MODEL_DESCRIPTIONS:
        return list(MODEL_DESCRIPTIONS[category].keys())
    return [model for category in MODEL_DESCRIPTIONS.values() for model in category.keys()]

def is_model_deprecated(model_name: str) -> bool:
    """檢查模型是否已被淘汰"""
    model_info = get_model_info(model_name)
    return model_info.get('deprecated', False) if model_info else False 