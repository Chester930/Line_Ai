import streamlit as st
import sys
import os
import json
from datetime import datetime
import asyncio
from typing import Optional
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils.role_manager import RoleManager
from shared.ai.model_manager import ModelManager
from shared.database.database import SessionLocal
from shared.ai.conversation_manager import ConversationManager

def init_session_state():
    """初始化會話狀態"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_role" not in st.session_state:
        st.session_state.current_role = None
    if "custom_settings" not in st.session_state:
        st.session_state.custom_settings = {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2000,
            "web_search": False
        }

async def generate_response(
    conversation_manager: ConversationManager,
    prompt: str,
    role_id: str
) -> str:
    """異步生成回應"""
    return await conversation_manager.handle_message(
        "studio_user",  # 測試用戶 ID
        prompt,
        role_id
    )

def show_conversation():
    """顯示對話界面"""
    st.header("對話測試")
    
    # 顯示歷史消息
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 輸入框
    if prompt := st.chat_input("輸入訊息..."):
        # 添加用戶消息
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 生成回應
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    db = SessionLocal()
                    conversation_manager = ConversationManager(db)
                    
                    # 使用當前角色和自定義設定
                    role = st.session_state.current_role
                    role.settings.update(st.session_state.custom_settings)
                    
                    # 使用 asyncio 運行異步函數
                    response = asyncio.run(generate_response(
                        conversation_manager,
                        prompt,
                        role.id
                    ))
                    
                    st.markdown(response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                except Exception as e:
                    st.error(f"生成回應時發生錯誤：{str(e)}")
                finally:
                    db.close()

def show_settings():
    """顯示設定面板"""
    st.sidebar.title("Studio 設定")
    
    # 角色選擇
    role_manager = RoleManager()
    roles = role_manager.list_roles()
    role_names = {role_id: role.name for role_id, role in roles.items()}
    
    selected_role = st.sidebar.selectbox(
        "選擇角色",
        list(roles.keys()),
        format_func=lambda x: role_names[x]
    )
    
    st.session_state.current_role = roles[selected_role]
    
    # 參數調整
    st.sidebar.subheader("參數設定")
    custom_settings = st.session_state.custom_settings
    
    custom_settings["temperature"] = st.sidebar.slider(
        "Temperature",
        0.0, 1.0,
        value=custom_settings["temperature"]
    )
    
    custom_settings["top_p"] = st.sidebar.slider(
        "Top P",
        0.0, 1.0,
        value=custom_settings["top_p"]
    )
    
    custom_settings["max_tokens"] = st.sidebar.number_input(
        "最大 Token 數",
        100, 4000,
        value=custom_settings["max_tokens"]
    )
    
    custom_settings["web_search"] = st.sidebar.checkbox(
        "啟用網路搜尋",
        value=custom_settings["web_search"]
    )
    
    # 文件上傳
    st.sidebar.subheader("文件上傳")
    uploaded_file = st.sidebar.file_uploader(
        "上傳參考文件",
        type=["txt", "pdf", "docx"]
    )
    
    if uploaded_file:
        try:
            # TODO: 實現文件處理邏輯
            st.sidebar.success("文件上傳成功")
        except Exception as e:
            st.sidebar.error(f"文件上傳失敗：{str(e)}")
    
    # 對話控制
    st.sidebar.subheader("對話控制")
    if st.sidebar.button("清除對話"):
        st.session_state.messages = []
        st.experimental_rerun()
    
    # 導出對話
    if st.sidebar.button("導出對話"):
        conversation_data = {
            "role": st.session_state.current_role.name,
            "settings": custom_settings,
            "messages": st.session_state.messages,
            "exported_at": datetime.now().isoformat()
        }
        
        # 將對話保存為 JSON 文件
        json_str = json.dumps(conversation_data, ensure_ascii=False, indent=2)
        st.sidebar.download_button(
            "下載 JSON",
            json_str,
            file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def main():
    st.set_page_config(
        page_title="Line AI Studio",
        page_icon="🤖",
        layout="wide"
    )
    
    init_session_state()
    show_settings()
    show_conversation()

if __name__ == "__main__":
    main()