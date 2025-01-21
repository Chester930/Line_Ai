import streamlit as st
from pathlib import Path
from dotenv import dotenv_values
from shared.config.config import Config
from shared.ai.model_manager import ModelManager

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

def show_page():
    """AI 模型設定頁面"""
    st.header("AI 模型設定 (Model Settings)")
    
    # 初始化設定
    config = Config()
    
    # 使用 form 確保設定一次性更新
    with st.form("model_settings"):
        # OpenAI 設定
        st.subheader("OpenAI 設定")
        openai_api_key = st.text_input(
            "OpenAI API Key",
            value=config.OPENAI_API_KEY if config.OPENAI_API_KEY else "",
            type="password"
        )
        
        # Google 設定
        st.subheader("Google 設定")
        google_api_key = st.text_input(
            "Google API Key",
            value=config.GOOGLE_API_KEY if config.GOOGLE_API_KEY else "",
            type="password"
        )
        
        # Anthropic 設定
        st.subheader("Anthropic 設定")
        anthropic_api_key = st.text_input(
            "Anthropic API Key",
            value=config.ANTHROPIC_API_KEY if config.ANTHROPIC_API_KEY else "",
            type="password"
        )
        
        # 模型參數設定
        st.subheader("模型參數設定 (Model Parameters)")
        col1, col2 = st.columns(2)
        
        with col1:
            model_temperature = st.slider(
                "預設溫度 (Default Temperature)",
                min_value=0.0,
                max_value=1.0,
                value=float(config.MODEL_TEMPERATURE),
                step=0.1,
                help="控制回應的創造性程度，較高的值會產生更多樣化的回應"
            )
            
            max_tokens = st.number_input(
                "最大 Token 數 (Max Tokens)",
                min_value=100,
                max_value=4000,
                value=int(config.MAX_TOKENS),
                help="單次回應的最大 token 數量"
            )
        
        with col2:
            top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=float(config.TOP_P),
                step=0.1,
                help="控制回應的多樣性"
            )
            
            presence_penalty = st.slider(
                "Presence Penalty",
                min_value=-2.0,
                max_value=2.0,
                value=float(config.PRESENCE_PENALTY),
                step=0.1,
                help="控制模型對已出現內容的重複程度"
            )
        
        # 模型選擇
        st.subheader("預設模型選擇 (Default Model)")
        default_model = st.selectbox(
            "選擇預設模型",
            options=["gemini-pro", "gpt-3.5-turbo", "claude-3-sonnet"],
            index=0 if config.DEFAULT_MODEL == "gemini-pro" else 1 if config.DEFAULT_MODEL == "gpt-3.5-turbo" else 2
        )
        
        # 儲存按鈕
        if st.form_submit_button("儲存設定"):
            try:
                # 更新設定
                config.update_config({
                    "OPENAI_API_KEY": openai_api_key,
                    "GOOGLE_API_KEY": google_api_key,
                    "ANTHROPIC_API_KEY": anthropic_api_key,
                    "MODEL_TEMPERATURE": str(model_temperature),
                    "MAX_TOKENS": str(max_tokens),
                    "TOP_P": str(top_p),
                    "PRESENCE_PENALTY": str(presence_penalty),
                    "DEFAULT_MODEL": default_model
                })
                
                st.success("✅ 設定已更新")
                
                # 顯示提示
                if not any([openai_api_key, google_api_key, anthropic_api_key]):
                    st.warning("⚠️ 請至少設定一個 API Key")
                
            except Exception as e:
                st.error(f"❌ 更新設定時發生錯誤：{str(e)}")
    
    # 顯示目前狀態
    st.subheader("API 狀態 (API Status)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        openai_status = "✅ 已設定" if config.OPENAI_API_KEY else "❌ 未設定"
        st.info(f"OpenAI API: {openai_status}")
    
    with col2:
        google_status = "✅ 已設定" if config.GOOGLE_API_KEY else "❌ 未設定"
        st.info(f"Google API: {google_status}")
    
    with col3:
        anthropic_status = "✅ 已設定" if config.ANTHROPIC_API_KEY else "❌ 未設定"
        st.info(f"Anthropic API: {anthropic_status}")

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