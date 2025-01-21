import streamlit as st
from shared.ai.chat_tester import ChatTester
from shared.config.config import Config

def show_page():
    """對話測試頁面"""
    st.header("對話測試")
    
    # 初始化聊天記錄
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 初始化設定
    config = Config()
    chat_tester = ChatTester()
    
    # 基本設定區
    with st.sidebar:
        st.subheader("對話設定")
        
        # 模型選擇
        model = st.selectbox(
            "選擇模型",
            options=["gemini-pro", "gpt-3.5-turbo", "claude-3-sonnet"],
            index=0
        )
        
        # 溫度設定
        temperature = st.slider(
            "溫度 (Temperature)",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1
        )
    
    # 顯示對話記錄
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 輸入區域
    if prompt := st.chat_input("輸入訊息..."):
        # 添加用戶訊息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # 處理回應
        with st.chat_message("assistant"):
            with st.spinner("AI思考中..."):
                try:
                    # 檢查是否有對應的 API Key
                    if model.startswith("gemini") and not config.GOOGLE_API_KEY:
                        st.error("請先設定 Google API Key")
                        return
                    elif model.startswith("gpt") and not config.OPENAI_API_KEY:
                        st.error("請先設定 OpenAI API Key")
                        return
                    elif model.startswith("claude") and not config.ANTHROPIC_API_KEY:
                        st.error("請先設定 Claude API Key")
                        return
                    
                    # 獲取 AI 回應
                    response = chat_tester.get_response(
                        model=model,
                        messages=st.session_state.messages,
                        temperature=temperature
                    )
                    
                    # 顯示回應
                    st.markdown(response)
                    
                    # 儲存回應
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                except Exception as e:
                    st.error(f"發生錯誤: {str(e)}")
    
    # 清除對話按鈕
    if st.button("清除對話"):
        st.session_state.messages = []
        st.rerun() 