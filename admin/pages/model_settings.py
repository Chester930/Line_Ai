import streamlit as st
from shared.config.config import Config
from shared.ai.model_manager import ModelManager

def show_page():
    """AI 模型設定頁面"""
    st.header("AI 模型設定 (AI Model Settings)")
    
    try:
        config = Config()
        model_manager = ModelManager()
    except Exception as e:
        st.error(f"初始化設定時發生錯誤: {str(e)}")
        return
    
    # API Keys 設定
    with st.expander("API Keys 設定", expanded=True):
        show_api_keys_settings(config)
    
    # 模型選擇和設定
    with st.expander("模型設定", expanded=True):
        show_model_settings(model_manager)
    
    # 模型測試
    with st.expander("模型測試", expanded=True):
        show_model_test(model_manager)

def show_api_keys_settings(config: Config):
    """顯示 API Keys 設定"""
    with st.form("api_keys_form"):
        # Google API 設定
        st.write("Google API 設定 (Google API Settings)")
        google_api_key = st.text_input(
            "Google API Key",
            value=config.GOOGLE_API_KEY or "",
            type="password",
            help="設定 Google API Key 以使用 Gemini 模型"
        )
        
        # OpenAI API 設定
        st.write("OpenAI API 設定 (OpenAI API Settings)")
        openai_api_key = st.text_input(
            "OpenAI API Key",
            value=config.OPENAI_API_KEY or "",
            type="password",
            help="設定 OpenAI API Key 以使用 GPT 模型"
        )
        
        # Claude API 設定
        st.write("Claude API 設定 (Claude API Settings)")
        claude_api_key = st.text_input(
            "Claude API Key",
            value=config.CLAUDE_API_KEY or "",
            type="password",
            help="設定 Claude API Key 以使用 Claude 模型"
        )
        
        if st.form_submit_button("儲存設定"):
            try:
                config.update_settings({
                    'GOOGLE_API_KEY': google_api_key,
                    'OPENAI_API_KEY': openai_api_key,
                    'CLAUDE_API_KEY': claude_api_key
                })
                st.success("✅ 設定已儲存")
            except Exception as e:
                st.error(f"❌ 儲存失敗: {str(e)}")

def show_model_settings(model_manager: ModelManager):
    """顯示模型設定"""
    with st.form("model_settings_form"):
        # 預設模型選擇
        default_model = st.selectbox(
            "預設 AI 模型 (Default AI Model)",
            ["gemini-pro", "gpt-4", "gpt-3.5-turbo", "claude-3-opus"],
            help="選擇預設使用的 AI 模型"
        )
        
        # 模型參數設定
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.slider(
                "Temperature",
                0.0, 1.0, 0.7,
                help="控制回應的創造性，越高越有創意"
            )
            max_tokens = st.number_input(
                "最大 Token 數 (Max Tokens)",
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
        
        if st.form_submit_button("儲存模型設定"):
            try:
                model_manager.update_settings({
                    'default_model': default_model,
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                    'top_p': top_p,
                    'presence_penalty': presence_penalty
                })
                st.success("✅ 模型設定已更新")
            except Exception as e:
                st.error(f"❌ 更新失敗: {str(e)}")

def show_model_test(model_manager: ModelManager):
    """顯示模型測試"""
    test_model = st.selectbox(
        "選擇要測試的模型",
        ["gemini-pro", "gpt-4", "gpt-3.5-turbo", "claude-3-opus"]
    )
    
    test_prompt = st.text_area(
        "測試提示詞",
        value="你好，請簡單自我介紹。",
        help="輸入測試用的提示詞"
    )
    
    if st.button("開始測試"):
        with st.spinner("正在生成回應..."):
            try:
                response = model_manager.test_model(
                    model=test_model,
                    prompt=test_prompt
                )
                st.write("模型回應：")
                st.write(response)
            except Exception as e:
                st.error(f"❌ 測試失敗: {str(e)}")