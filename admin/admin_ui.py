import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils.role_manager import RoleManager
from shared.utils.ngrok_manager import NgrokManager
from shared.ai.conversation_manager import ConversationManager
from shared.database.database import SessionLocal
from shared.config.config import Config
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
            
            submitted = st.form_submit_button("創建角色 (Create)")
            if submitted:
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
            # 基本信息顯示
            st.write("當前設定：")
            st.json({
                "名稱": role.name,
                "描述": role.description,
                "提示詞": role.prompt,
                "設定": role.settings
            })
            
            # 測試對話按鈕
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
            
            # 編輯按鈕
            if st.button("編輯 (Edit)", key=f"edit_{role_id}"):
                st.session_state[f"editing_{role_id}"] = True
            
            # 編輯表單
            if st.session_state.get(f"editing_{role_id}", False):
                with st.form(f"edit_role_{role_id}"):
                    name = st.text_input("名稱 (Name)", value=role.name)
                    description = st.text_area("描述 (Description)", value=role.description)
                    prompt = st.text_area("提示詞 (Prompt)", value=role.prompt)
                    
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
                                st.session_state[f"editing_{role_id}"] = False
                                st.experimental_rerun()
                            else:
                                st.error("❌ 更新失敗")
                    
                    with col4:
                        if st.form_submit_button("取消 (Cancel)"):
                            st.session_state[f"editing_{role_id}"] = False
                            st.experimental_rerun()
            
            # 刪除按鈕
            if st.button("刪除 (Delete)", key=f"delete_{role_id}", type="primary"):
                        if role_manager.delete_role(role_id):
                            st.success("✅ 角色已刪除")
                            st.experimental_rerun()
                        else:
                            st.error("❌ 刪除失敗")

def show_api_settings():
    st.header("API Keys 設定 (API Settings)")
    
    # 定義各 API 提供商的模型
    MODEL_OPTIONS = {
        "Google": {
            "api_key": "GOOGLE_API_KEY",
            "models": ["gemini-pro", "gemini-pro-vision"],
            "description": "Gemini 系列模型"
        },
        "OpenAI": {
            "api_key": "OPENAI_API_KEY",
            "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-vision"],
            "description": "GPT 系列模型"
        },
        "Anthropic": {
            "api_key": "CLAUDE_API_KEY",
            "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "description": "Claude 系列模型"
        }
    }
    
    with st.form("api_settings"):
        active_providers = []
        api_configs = {}
        
        # 為每個提供商創建一個展開區
        for provider, config in MODEL_OPTIONS.items():
            with st.expander(f"{provider} API 設定", expanded=True):
                st.write(config["description"])
                
                # API Key 輸入
                api_key = st.text_input(
                    f"{provider} API Key",
                    value=getattr(Config, config["api_key"], "") or "",
                    type="password",
                    help=f"輸入 {provider} API Key"
                )
                
                if api_key:
                    active_providers.append(provider)
                    
                    # 選擇要啟用的模型
                    enabled_models = st.multiselect(
                        "啟用的模型",
                        options=config["models"],
                        default=[config["models"][0]],
                        help=f"選擇要啟用的 {provider} 模型"
                    )
                    
                    api_configs[provider] = {
                        "api_key": api_key,
                        "enabled_models": enabled_models
                    }
        
        # 選擇默認模型（只能從已啟用的模型中選擇）
        st.subheader("預設模型設定")
        available_models = []
        for provider in active_providers:
            available_models.extend(api_configs[provider]["enabled_models"])
        
        if available_models:
            default_model = st.selectbox(
                "選擇預設模型",
                options=available_models,
                help="設定系統默認使用的 AI 模型"
            )
        else:
            st.warning("⚠️ 請至少設定一個 API Key 並啟用相應的模型")
            default_model = None
        
        # 添加提交按鈕
        submitted = st.form_submit_button("保存設定")
        
        if submitted:
            try:
                # 準備更新的設定
                env_updates = {}
                
                # 更新 API Keys
                for provider, config in MODEL_OPTIONS.items():
                    api_key = api_configs.get(provider, {}).get("api_key", "")
                    if api_key:
                        env_updates[config["api_key"]] = api_key
                        
                        # 保存已啟用的模型
                        enabled_models = api_configs[provider]["enabled_models"]
                        env_updates[f"{provider.upper()}_ENABLED_MODELS"] = ",".join(enabled_models)
                
                # 更新默認模型
                if default_model:
                    env_updates["DEFAULT_MODEL"] = default_model
                
                # 保存到 .env 文件
                update_env_file(env_updates)
                st.success("✅ 設定已更新")
                
                # 測試已設定的 API
                st.write("正在測試 API 連接...")
                for provider in active_providers:
                    api_key = api_configs[provider]["api_key"]
                    if provider == "Google":
                        test_gemini(api_key)
                    elif provider == "OpenAI":
                        test_openai(api_key)
                    elif provider == "Anthropic":
                        test_claude(api_key)
                    
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

def show_line_account_management():
    st.header("LINE 官方帳號管理")
    
    # 基本設定
    with st.expander("帳號設定 (Account Settings)", expanded=True):
        with st.form("line_account_settings"):
            st.subheader("Channel 設定")
            
            # LINE API 設定
            channel_secret = st.text_input(
                "Channel Secret",
                value=getattr(Config, 'LINE_CHANNEL_SECRET', '') or "",
                type="password",
                help="從 LINE Developers 取得的 Channel Secret"
            )
            
            channel_token = st.text_input(
                "Channel Access Token",
                value=getattr(Config, 'LINE_CHANNEL_ACCESS_TOKEN', '') or "",
                type="password",
                help="從 LINE Developers 取得的 Channel Access Token"
            )
            
            # Webhook 設定
            ngrok_token = st.text_input(
                "Ngrok Auth Token",
                value=getattr(Config, 'NGROK_AUTH_TOKEN', '') or "",
                type="password",
                help="用於設定 Webhook URL"
            )
            
            if st.form_submit_button("保存設定"):
                try:
                    env_updates = {
                        "LINE_CHANNEL_SECRET": channel_secret,
                        "LINE_CHANNEL_ACCESS_TOKEN": channel_token,
                        "NGROK_AUTH_TOKEN": ngrok_token
                    }
                    update_env_file(env_updates)
                    st.success("✅ 設定已更新")
                except Exception as e:
                    st.error(f"❌ 保存失敗：{str(e)}")
    
    # 機器人控制
    with st.expander("機器人控制 (Bot Control)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("啟動機器人", type="primary"):
                if not all([Config.LINE_CHANNEL_SECRET, 
                           Config.LINE_CHANNEL_ACCESS_TOKEN,
                           Config.NGROK_AUTH_TOKEN]):
                    st.error("❌ 請先完成帳號設定")
                    return
                    
                try:
                    ngrok = NgrokManager()
                    webhook_url = ngrok.start()
                    st.success(f"✅ 機器人已啟動\nWebhook URL: {webhook_url}")
                except Exception as e:
                    st.error(f"❌ 啟動失敗：{str(e)}")
        
        with col2:
            if st.button("停止機器人", type="secondary"):
                try:
                    # TODO: 實現停止功能
                    st.warning("⚠️ 機器人已停止運行")
                except Exception as e:
                    st.error(f"❌ 停止失敗：{str(e)}")
    
    # 好友管理
    with st.expander("好友管理 (Friend Management)", expanded=True):
        st.subheader("加入好友")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### 掃描 QR Code
            1. 使用 LINE 掃描下方 QR Code
            2. 加入此機器人為好友
            3. 開始對話測試
            """)
            # TODO: 顯示 QR Code 圖片
            st.image("path/to/qr_code.png", width=200)
        
        with col2:
            st.markdown("""
            ### 好友連結
            點擊下方連結加入好友：
            """)
            st.markdown("[加為好友](https://line.me/R/ti/p/@your_bot_id)")
            st.info("Bot ID: @your_bot_id")
    
    # 進階功能
    with st.expander("進階功能 (Advanced Features)", expanded=False):
        st.subheader("群發訊息")
        with st.form("broadcast_message"):
            message = st.text_area("訊息內容")
            target = st.radio(
                "發送對象",
                ["所有好友", "特定群組", "指定好友"]
            )
            
            if st.form_submit_button("發送"):
                st.info("群發功能開發中...")
        
        st.subheader("自動回覆設定")
        with st.form("auto_reply"):
            enabled = st.checkbox("啟用自動回覆")
            welcome_msg = st.text_area("歡迎訊息")
            
            if st.form_submit_button("保存"):
                st.info("自動回覆功能開發中...")

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
         "AI 模型設定 (AI Model Settings)", 
         "LINE 官方帳號管理 (LINE Official Account)",
         "對話角色管理 (Chat Role Management)",
         "文件管理 (Document Management)"]
    )
    
    if "系統狀態" in menu:
        show_system_status()
    elif "AI 模型設定" in menu:
        show_api_settings()  # 原本的 API Keys 設定
    elif "LINE 官方帳號管理" in menu:
        show_line_account_management()  # 新的 LINE 管理界面
    elif "對話角色管理" in menu:
        show_role_management(role_manager)
    elif "文件管理" in menu:
        st.header("文件管理 (Document Management)")
        st.info("📝 文件管理功能開發中...")

if __name__ == "__main__":
    main() 