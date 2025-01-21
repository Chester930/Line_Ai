import streamlit as st
from shared.config.config import Config
from shared.ai.model_manager import ModelManager

def show_page():
    """AI 模型設定頁面"""
    st.header("AI 模型設定 (AI Model Settings)")
    
    config = Config()
    model_manager = ModelManager()
    
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