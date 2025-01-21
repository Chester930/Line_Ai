import streamlit as st
from pathlib import Path
from dotenv import dotenv_values
from shared.config.config import Config
from shared.ai.model_manager import ModelManager
from shared.config.model_descriptions import MODEL_DESCRIPTIONS, get_model_info

def test_gemini(api_key: str):
    """測試 Gemini API"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        st.success("✅ Gemini API 連接正常")
    except Exception as e:
        st.error(f"❌ Gemini API 測試失敗：{str(e)}")

def test_openai(api_key: str):
    """測試 OpenAI API"""
    try:
        import openai
        openai.api_key = api_key
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}]
        )
        st.success("✅ OpenAI API 連接正常")
    except Exception as e:
        st.error(f"❌ OpenAI API 測試失敗：{str(e)}")

def test_claude(api_key: str):
    """測試 Claude API"""
    try:
        import anthropic
        client = anthropic.Client(api_key=api_key)
        response = client.messages.create(
            model="claude-3-opus-20240229",
            messages=[{"role": "user", "content": "Hello"}]
        )
        st.success("✅ Claude API 連接正常")
    except Exception as e:
        st.error(f"❌ Claude API 測試失敗：{str(e)}")

def update_env_file(updates: dict):
    """更新 .env 文件"""
    env_path = Path(__file__).parent.parent.parent / '.env'
    
    if env_path.exists():
        current_env = dotenv_values(env_path)
    else:
        current_env = {}
    
    current_env.update(updates)
    
    with open(env_path, 'w', encoding='utf-8') as f:
        for key, value in current_env.items():
            f.write(f"{key}={value}\n")

def is_model_available(model_name: str, category: str, config: Config) -> bool:
    """檢查模型是否可用"""
    if not model_name or not category:
        return False
        
    if category == "OpenAI 模型":
        return bool(config.OPENAI_API_KEY)
    elif category == "Google Gemini 模型":
        return bool(config.GOOGLE_API_KEY)
    elif category == "Claude 模型":
        return bool(config.ANTHROPIC_API_KEY)
    return False

def get_provider(model_name: str) -> str:
    """根據模型名稱獲取供應商"""
    if not model_name:
        return None
    if "GPT" in model_name:
        return "OpenAI 模型"
    elif "Gemini" in model_name:
        return "Google Gemini 模型"
    elif "Claude" in model_name:
        return "Claude 模型"
    return None

def show_page():
    """AI 模型設定頁面"""
    st.header("AI 模型設定")
    config = Config()
    
    # 添加自定義 CSS
    st.markdown("""
        <style>
        /* 美化下拉選單 */
        .stSelectbox {
            margin-bottom: 1rem;
        }
        
        /* 添加懸浮效果 */
        .model-info {
            transition: all 0.3s ease;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        
        .model-info:hover {
            background-color: rgba(255, 255, 255, 0.05);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        /* 美化狀態標籤 */
        .model-status {
            padding: 0.2rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.8rem;
            margin-left: 0.5rem;
        }
        
        .status-enabled {
            background-color: #28a745;
            color: white;
        }
        
        .status-disabled {
            background-color: #dc3545;
            color: white;
        }
        
        .status-deprecated {
            background-color: #ffc107;
            color: black;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # API Keys 設定表單
    with st.form("api_keys_form"):
        st.subheader("API Keys 設定")
        
        openai_api_key = st.text_input(
            "OpenAI API Key",
            value=config.OPENAI_API_KEY if config.OPENAI_API_KEY else "",
            type="password"
        )
        
        google_api_key = st.text_input(
            "Google API Key",
            value=config.GOOGLE_API_KEY if config.GOOGLE_API_KEY else "",
            type="password"
        )
        
        anthropic_api_key = st.text_input(
            "Anthropic API Key",
            value=config.ANTHROPIC_API_KEY if config.ANTHROPIC_API_KEY else "",
            type="password"
        )
        
        if st.form_submit_button("儲存 API Keys"):
            try:
                config.update_config({
                    "OPENAI_API_KEY": openai_api_key,
                    "GOOGLE_API_KEY": google_api_key,
                    "ANTHROPIC_API_KEY": anthropic_api_key,
                })
                st.success("✅ API Keys 已更新")
            except Exception as e:
                st.error(f"❌ 更新失敗：{str(e)}")
    
    # 模型說明
    st.subheader("模型說明")
    
    # 說明文字
    st.markdown("""
        **模型選擇說明：**
        1. 選擇模型類別（GPT、Gemini、Claude）
        2. 從下拉選單選擇具體模型
        3. 將滑鼠移至模型上可查看詳細說明
        4. 點選確認以設定為使用模型
    """)
    
    tabs = st.tabs(["語言模型", "專業工具模型"])
    
    with tabs[0]:  # 語言模型
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # 先選擇模型類別
            model_categories = {
                "GPT 系列": "OpenAI 模型",
                "Gemini 系列": "Google Gemini 模型",
                "Claude 系列": "Claude 模型"
            }
            
            selected_category = st.selectbox(
                "選擇模型類別",
                options=[""] + list(model_categories.keys()),
                format_func=lambda x: x if x else "請選擇模型類別",
                key="model_category"
            )
            
            selected_model = None  # 初始化選擇的模型變數
            
            # 根據選擇的類別顯示相應的模型
            if selected_category:
                category_key = model_categories[selected_category]
                available_models = [
                    model for model in MODEL_DESCRIPTIONS[category_key].keys()
                ]
                
                selected_model = st.selectbox(
                    "選擇模型",
                    options=[""] + available_models,
                    format_func=lambda x: f"{x} {'✅' if is_model_available(x, category_key, config) else '❌'}" if x else "請選擇具體模型",
                    key="model_selection"
                )
        
        with col2:
            # 顯示模型資訊
            if selected_category and selected_model:
                category_key = model_categories[selected_category]
                if selected_model in MODEL_DESCRIPTIONS[category_key]:
                    model_info = MODEL_DESCRIPTIONS[category_key][selected_model]
                    
                    st.markdown("""
                        <div class="model-info">
                    """, unsafe_allow_html=True)
                    
                    # 模型名稱和描述
                    st.write("### " + model_info["name"])
                    st.write("**描述：**")
                    st.write(model_info["description"])
                    
                    # 模型 ID
                    if "model_ids" in model_info:
                        st.write("**支援平台：**")
                        for platform, model_id in model_info["model_ids"].items():
                            if isinstance(model_id, dict):
                                for version, id_value in model_id.items():
                                    st.write(f"- {platform.upper()} ({version}): `{id_value}`")
                            else:
                                st.write(f"- {platform.upper()}: `{model_id}`")
                    
                    # 如果有棄用信息
                    if model_info.get("deprecated"):
                        st.warning(f"⚠️ 此模型已於 {model_info.get('deprecated_date')} 棄用")
                    
                    # 如果有特別註記
                    if "note" in model_info:
                        st.info(f"ℹ️ {model_info['note']}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # 確認按鈕
                    if st.button("確認使用此模型", key="confirm_model"):
                        try:
                            config.update_config({
                                "DEFAULT_MODEL": selected_model
                            })
                            st.success(f"✅ 已設定 {selected_model} 為預設模型")
                        except Exception as e:
                            st.error(f"❌ 設定失敗：{str(e)}")
    
    with tabs[1]:  # 專業工具模型
        st.info("🚧 專業工具模型功能開發中")
    
    # 模型參數設定
    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider(
            "Temperature",
            0.0, 1.0, 0.7,
            help="控制回應的創造性"
        )
        max_tokens = st.number_input(
            "Max Tokens",
            100, 4000, 1000,
            help="單次回應的最大長度"
        )
    
    with col2:
        top_p = st.slider(
            "Top P",
            0.0, 1.0, 0.9,
            help="控制回應的多樣性"
        )
        presence_penalty = st.slider(
            "Presence Penalty",
            -2.0, 2.0, 0.0,
            help="控制模型對新主題的關注度"
        )
    
    if st.button("儲存模型設定"):
        # TODO: 實現設定儲存邏輯
        st.success("模型設定已更新")

def show_api_keys_settings(config: Config):
    """顯示 API Keys 設定"""
    st.subheader("API Keys 設定")
    
    with st.form("api_keys_form"):
        # OpenAI API Key
        openai_key = st.text_input(
            "OpenAI API Key",
            value=config.OPENAI_API_KEY or "",
            type="password"
        )
        
        # Google API Key
        google_key = st.text_input(
            "Google API Key",
            value=config.GOOGLE_API_KEY or "",
            type="password"
        )
        
        # Anthropic API Key
        anthropic_key = st.text_input(
            "Anthropic API Key",
            value=config.ANTHROPIC_API_KEY or "",
            type="password"
        )
        
        if st.form_submit_button("儲存設定"):
            try:
                # TODO: 實現設定儲存邏輯
                st.success("設定已更新")
            except Exception as e:
                st.error(f"更新失敗: {str(e)}")

def show_model_settings(model_manager: ModelManager):
    """顯示模型設定"""
    st.subheader("模型設定")
    
    # 預設模型選擇
    default_model = st.selectbox(
        "預設模型",
        ["gpt-4-turbo-preview", "gemini-pro", "claude-3-opus"]
    )
    
    # 模型參數設定
    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider(
            "Temperature",
            0.0, 1.0, 0.7,
            help="控制回應的創造性"
        )
        max_tokens = st.number_input(
            "Max Tokens",
            100, 4000, 1000,
            help="單次回應的最大長度"
        )
    
    with col2:
        top_p = st.slider(
            "Top P",
            0.0, 1.0, 0.9,
            help="控制回應的多樣性"
        )
        presence_penalty = st.slider(
            "Presence Penalty",
            -2.0, 2.0, 0.0,
            help="控制模型對新主題的關注度"
        )
    
    if st.button("儲存模型設定"):
        # TODO: 實現設定儲存邏輯
        st.success("模型設定已更新")

def show_model_test(model_manager: ModelManager):
    """顯示模型測試"""
    st.subheader("模型測試")
    
    test_model = st.selectbox(
        "選擇要測試的模型",
        ["gpt-4-turbo-preview", "gemini-pro", "claude-3-opus"]
    )
    
    test_prompt = st.text_area(
        "測試提示詞",
        value="你好，請簡單自我介紹。"
    )
    
    if st.button("測試"):
        with st.spinner("正在生成回應..."):
            try:
                # TODO: 實現實際的模型測試
                response = "這是一個測試回應..."
                st.write("模型回應：")
                st.write(response)
            except Exception as e:
                st.error(f"測試失敗: {str(e)}")

# 添加自定義 CSS
st.markdown("""
    <style>
    .model-info {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .model-info h3 {
        margin-bottom: 1rem;
        color: #ffffff;
    }
    
    .model-info p {
        margin-bottom: 0.5rem;
        color: #e0e0e0;
    }
    
    .model-info code {
        background-color: rgba(0, 0, 0, 0.2);
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        font-family: monospace;
        color: #a0e0ff;
    }
    
    .stWarning, .stInfo {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)