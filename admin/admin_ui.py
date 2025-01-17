import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils.role_manager import RoleManager
from shared.utils.ngrok_manager import NgrokManager
from shared.ai.conversation_manager import ConversationManager
from shared.database.database import SessionLocal
from pathlib import Path
from dotenv import dotenv_values

def show_system_status():
    st.header("系統狀態")
    st.write("目前版本：1.0.0")
    
    # 顯示系統資訊
    col1, col2 = st.columns(2)
    with col1:
        st.info("系統設定 (System Settings)")
        st.write("- 資料庫類型：SQLite")
        st.write("- AI 模型：Gemini Pro")
        st.write("- 日誌級別：INFO")
    
    with col2:
        st.info("運行狀態 (Runtime Status)")
        st.write("- 資料庫連接：正常")
        st.write("- API 連接：正常")
        st.write("- Webhook：未啟動")

def show_role_management(role_manager):
    st.header("角色管理 (Role Management)")
    
    # 導入預設角色
    with st.expander("預設角色管理 (Default Roles)", expanded=True):
        st.write("預設角色包含基本的對話設定和提示詞")
        if st.button("導入預設角色 (Import Default Roles)"):
            if role_manager.import_default_roles():
                st.success("✅ 預設角色已導入")
                st.experimental_rerun()
            else:
                st.error("❌ 導入失敗")
    
    # 創建新角色
    with st.expander("創建新角色 (Create New Role)", expanded=False):
        with st.form("create_role"):
            st.write("請填寫新角色的基本資訊：")
            role_id = st.text_input("角色ID (英文) (Role ID)", help="唯一標識符，例如：custom_helper")
            name = st.text_input("角色名稱 (Role Name)", help="顯示名稱，例如：客服助手")
            description = st.text_area("角色描述 (Description)", help="角色的主要功能和特點")
            prompt = st.text_area("提示詞 (System Prompt)", help="設定角色的行為和回應方式")
            
            st.write("進階設定：")
            col1, col2 = st.columns(2)
            with col1:
                temperature = st.slider(
                    "溫度 (Temperature)", 
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
                web_search = st.checkbox(
                    "啟用網路搜尋 (Enable Web Search)",
                    help="允許使用網路資訊回答問題"
                )
            
            if st.form_submit_button("創建角色 (Create)"):
                settings = {
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                    "web_search": web_search
                }
                if role_manager.create_role(role_id, name, description, prompt, settings):
                    st.success("✅ 角色已創建")
                    st.experimental_rerun()
                else:
                    st.error("❌ 創建失敗")
    
    # 顯示和編輯現有角色
    st.subheader("現有角色列表 (Existing Roles)")
    roles = role_manager.list_roles()
    
    if not roles:
        st.warning("⚠️ 尚未創建任何角色，請先導入預設角色或創建新角色")
        return
    
    for role_id, role in roles.items():
        with st.expander(f"{role.name} ({role_id})", expanded=False):
            with st.form(f"edit_role_{role_id}"):
                st.write("基本資訊：")
                name = st.text_input("名稱 (Name)", value=role.name)
                description = st.text_area("描述 (Description)", value=role.description)
                prompt = st.text_area("提示詞 (Prompt)", value=role.prompt)
                
                st.write("參數設定：")
                col1, col2 = st.columns(2)
                with col1:
                    temperature = st.slider(
                        "溫度 (Temperature)",
                        0.0, 1.0,
                        value=role.settings.get('temperature', 0.7)
                    )
                    max_tokens = st.number_input(
                        "最大 Token 數 (Max Tokens)",
                        100, 4000,
                        value=role.settings.get('max_tokens', 1000)
                    )
                with col2:
                    top_p = st.slider(
                        "Top P",
                        0.0, 1.0,
                        value=role.settings.get('top_p', 0.9)
                    )
                    web_search = st.checkbox(
                        "啟用網路搜尋 (Web Search)",
                        value=role.settings.get('web_search', False)
                    )
                
                # 測試對話
                if st.button("測試對話 (Test Chat)", key=f"test_{role_id}"):
                    with st.spinner("正在準備測試..."):
                        try:
                            db = SessionLocal()
                            conversation_manager = ConversationManager(db)
                            test_message = "你好，請簡單介紹一下你自己。"
                            
                            response = conversation_manager.handle_message(
                                "admin_test",
                                test_message,
                                role_id
                            )
                            
                            st.write("測試對話：")
                            st.write(f"問：{test_message}")
                            st.write(f"答：{response}")
                        except Exception as e:
                            st.error(f"測試失敗：{str(e)}")
                        finally:
                            db.close()
                
                col3, col4 = st.columns(2)
                with col3:
                    if st.form_submit_button("更新 (Update)"):
                        settings = {
                            "temperature": temperature,
                            "top_p": top_p,
                            "max_tokens": max_tokens,
                            "web_search": web_search
                        }
                        if role_manager.update_role(
                            role_id, name, description, prompt, settings
                        ):
                            st.success("✅ 角色已更新")
                            st.experimental_rerun()
                        else:
                            st.error("❌ 更新失敗")
                
                with col4:
                    if st.form_submit_button("刪除 (Delete)", type="primary"):
                        if role_manager.delete_role(role_id):
                            st.success("✅ 角色已刪除")
                            st.experimental_rerun()
                        else:
                            st.error("❌ 刪除失敗")

def show_api_settings():
    st.header("API Keys 設定 (API Settings)")
    
    with st.form("api_settings"):
        st.subheader("Google AI")
        google_api_key = st.text_input(
            "Google API Key",
            value=Config.GOOGLE_API_KEY or "",
            type="password",
            help="用於 Gemini 模型"
        )
        
        st.subheader("OpenAI")
        openai_api_key = st.text_input(
            "OpenAI API Key",
            value=Config.OPENAI_API_KEY or "",
            type="password",
            help="用於 GPT-3.5/GPT-4 模型"
        )
        
        st.subheader("Anthropic")
        claude_api_key = st.text_input(
            "Claude API Key",
            value=Config.CLAUDE_API_KEY or "",
            type="password",
            help="用於 Claude 模型"
        )
        
        # 模型選擇
        st.subheader("預設模型設定 (Default Model Settings)")
        default_model = st.selectbox(
            "選擇預設模型",
            options=["gemini-pro", "gpt-3.5-turbo", "gpt-4", "claude-3-opus"],
            index=0,
            help="設定系統默認使用的 AI 模型"
        )
        
        if st.form_submit_button("保存設定 (Save Settings)"):
            try:
                # 更新 .env 文件
                env_updates = {
                    "GOOGLE_API_KEY": google_api_key,
                    "OPENAI_API_KEY": openai_api_key,
                    "CLAUDE_API_KEY": claude_api_key,
                    "DEFAULT_MODEL": default_model
                }
                
                update_env_file(env_updates)
                st.success("✅ API Keys 已更新")
                
                # 顯示模型可用性
                st.write("模型可用性測試：")
                if google_api_key:
                    test_gemini(google_api_key)
                if openai_api_key:
                    test_openai(openai_api_key)
                if claude_api_key:
                    test_claude(claude_api_key)
                    
            except Exception as e:
                st.error(f"❌ 保存失敗：{str(e)}")

def update_env_file(updates: dict):
    """更新 .env 文件"""
    env_path = Path(__file__).parent.parent / '.env'
    
    # 讀取現有的 .env 文件
    if env_path.exists():
        current_env = dotenv_values(env_path)
    else:
        current_env = {}
    
    # 更新值
    current_env.update(updates)
    
    # 寫回文件
    with open(env_path, 'w', encoding='utf-8') as f:
        for key, value in current_env.items():
            f.write(f"{key}={value}\n")

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

def main():
    st.set_page_config(
        page_title="Line AI Assistant - 管理介面",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("Line AI Assistant 管理介面")
    
    role_manager = RoleManager()
    
    # 側邊欄
    st.sidebar.title("功能選單 (Menu)")
    menu = st.sidebar.selectbox(
        "選擇功能 (Select Function)",
        ["系統狀態 (System Status)", 
         "API Keys 設定 (API Settings)", 
         "角色管理 (Role Management)",
         "文件管理 (Document Management)",
         "專案控制 (Project Control)"]
    )
    
    if "系統狀態" in menu:
        show_system_status()
    elif "API Keys" in menu:
        show_api_settings()
    elif "角色管理" in menu:
        show_role_management(role_manager)
    elif "文件管理" in menu:
        st.header("文件管理 (Document Management)")
        st.info("📝 文件管理功能開發中...")
    elif "專案控制" in menu:
        st.header("專案控制 (Project Control)")
        if st.button("啟動 LINE Bot (Start LINE Bot)"):
            try:
                ngrok = NgrokManager()
                webhook_url = ngrok.start()
                st.success(f"✅ LINE Bot 已啟動\nWebhook URL: {webhook_url}")
            except Exception as e:
                st.error(f"❌ 啟動失敗：{str(e)}")

if __name__ == "__main__":
    main() 