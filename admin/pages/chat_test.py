import streamlit as st
import asyncio
from shared.ai.chat_tester import ChatTester
from shared.utils.role_manager import RoleManager
from shared.ai.model_manager import ModelManager

def show_page():
    """對話測試頁面"""
    st.header("對話測試")
    
    # 初始化必要的管理器
    chat_tester = ChatTester()
    role_manager = RoleManager()
    model_manager = ModelManager()
    
    # 側邊設定
    with st.sidebar:
        show_test_settings(role_manager, model_manager)
    
    # 主要對話區域
    show_chat_interface(chat_tester)

def show_test_settings(role_manager: RoleManager, model_manager: ModelManager):
    """顯示測試設定"""
    st.subheader("測試設定")
    
    # 選擇角色
    roles = role_manager.list_roles()
    selected_role = st.selectbox(
        "選擇角色",
        options=list(roles.keys()),
        format_func=lambda x: roles[x].name
    )
    
    # 選擇模型
    selected_model = st.selectbox(
        "選擇模型",
        ["gpt-4-turbo-preview", "gemini-pro", "claude-3-opus"]
    )
    
    # 模型參數
    temperature = st.slider(
        "Temperature",
        0.0, 1.0, 0.7
    )
    
    max_tokens = st.number_input(
        "Max Tokens",
        100, 4000, 1000
    )
    
    # 功能開關
    enable_kb = st.checkbox("啟用知識庫", value=True)
    enable_web = st.checkbox("啟用網路搜尋", value=False)
    
    # 儲存設定到 session state
    if st.button("應用設定"):
        st.session_state.chat_settings = {
            'role_id': selected_role,
            'model': selected_model,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'enable_kb': enable_kb,
            'enable_web': enable_web
        }
        st.success("設定已更新")

def show_chat_interface(chat_tester: ChatTester):
    """顯示對話介面"""
    # 初始化對話歷史
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 顯示對話歷史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 輸入區域
    if prompt := st.chat_input("輸入訊息..."):
        # 添加用戶訊息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 獲取 AI 回應
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    settings = st.session_state.get('chat_settings', {})
                    response = asyncio.run(chat_tester.get_response(
                        prompt,
                        role_id=settings.get('role_id'),
                        model=settings.get('model'),
                        temperature=settings.get('temperature', 0.7),
                        max_tokens=settings.get('max_tokens', 1000),
                        enable_kb=settings.get('enable_kb', True),
                        enable_web=settings.get('enable_web', False)
                    ))
                    st.markdown(response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                except Exception as e:
                    st.error(f"生成回應時發生錯誤: {str(e)}")
    
    # 清除對話按鈕
    if st.button("清除對話"):
        st.session_state.messages = []
        st.rerun() 