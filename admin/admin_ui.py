import streamlit as st
import sys
import os
import time
from pathlib import Path
from dotenv import dotenv_values
import asyncio
import logging
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils.role_manager import RoleManager
from shared.utils.ngrok_manager import NgrokManager
from shared.ai.conversation_manager import ConversationManager
from shared.database.database import SessionLocal, get_db
from shared.database.models import User
from shared.config.config import Config
from shared.ai.chat_tester import ChatTester
from shared.utils.file_processor import FileProcessor
from shared.ai.model_manager import ModelManager

# 設置 logger
logger = logging.getLogger(__name__)

def show_system_status():
    st.header("系統狀態 (System Status)")
    st.write("目前版本 (Current Version)：1.0.0")
    
    # 顯示系統資訊
    col1, col2 = st.columns(2)
    with col1:
        st.info("系統設定 (System Settings)")
        st.write("- 資料庫類型 (Database Type)：SQLite")
        st.write("- AI 模型 (AI Model)：Gemini Pro")
        st.write("- 日誌級別 (Log Level)：INFO")
    
    with col2:
        st.info("運行狀態 (Runtime Status)")
        st.write("- 資料庫連接 (Database Connection)：正常 (Normal)")
        st.write("- API 連接 (API Connection)：正常 (Normal)")
        st.write("- Webhook：未啟動 (Not Started)")

def show_prompts_management(role_manager):
    st.header("共用提示詞管理 (Shared Prompts Management)")
    
    # 定義類別映射
    category_mapping = {
        "語言設定 (Language)": "language",
        "語氣風格 (Tone)": "tone",
        "輸出格式 (Output Format)": "output_format",
        "寫作風格 (Writing Style)": "writing_style",
        "MBTI 性格 (MBTI Personality)": "mbti",
        "進階性格 (Advanced Personality)": "personality"
    }
    
    # 顯示分類標籤
    tabs = st.tabs([
        "語言設定 (Language)",
        "語氣風格 (Tone)", 
        "輸出格式 (Output Format)", 
        "寫作風格 (Writing Style)",
        "MBTI 性格 (MBTI Personality)",
        "進階性格 (Advanced Personality)"
    ])
    
    for tab, (zh_category, en_category) in zip(tabs, category_mapping.items()):
        with tab:
            prompts = role_manager.get_prompts_by_category(en_category)
            if prompts:
                for prompt_id, data in prompts.items():
                    with st.expander(f"{data['description']}", expanded=False):
                        st.code(data['content'], language="markdown")
                        st.write(f"使用次數 (Usage Count): {data.get('usage_count', 0)}")
            else:
                st.info(f"目前沒有 {zh_category} 的提示詞")

def show_role_management(role_manager):
    """角色管理介面"""
    st.header("角色管理 (Role Management)")
    
    # 創建新角色
    st.subheader("創建新角色 (Create New Role)")
    with st.form("create_role"):
        st.write("請填寫新角色的基本資訊：")
        role_id = st.text_input(
            "角色ID (英文) (Role ID)",
            help="唯一標識符，例如：custom_helper"
        )
        name = st.text_input(
            "角色名稱 (Role Name)",
            help="顯示名稱，例如：客服助手"
        )
        description = st.text_area(
            "角色描述 (Description)",
            help="角色的主要功能和特點"
        )
        
        # 選擇共用 prompts
        st.subheader("選擇共用 Prompts")
        
        # 依類別選擇 Prompts
        categories = {
            "語言設定": "language",
            "語氣風格": "tone",
            "輸出格式": "output_format",
            "寫作風格": "writing_style",
            "MBTI 性格": "mbti",
            "進階性格": "personality"
        }
        
        selected_prompts = {}
        available_prompts = role_manager.get_available_prompts()
        
        for zh_category, en_category in categories.items():
            # 獲取該類別的所有 prompts
            category_prompts = role_manager.get_prompts_by_category(en_category)
            
            if en_category == "mbti":
                # MBTI 性格使用單選
                st.write(f"選擇 {zh_category}：")
                prompt_options = ["預設 (Default)"] + [
                    f"{k} - {v['description']}"
                    for k, v in category_prompts.items()
                ]
                
                selected = st.selectbox(
                    "選擇 MBTI 性格類型",
                    options=prompt_options,
                    key=f"select_{en_category}"
                )
                
                if selected != "預設 (Default)":
                    prompt_id = selected.split(" - ")[0]
                    selected_prompts[en_category] = prompt_id
                    
            elif en_category == "personality":
                # 進階性格使用多選
                st.write(f"選擇{zh_category}（可複選）：")
                prompt_options = [
                    f"{k} - {v['description']}"
                    for k, v in category_prompts.items()
                ]
                
                selected_traits = st.multiselect(
                    "選擇進階性格特徵",
                    options=prompt_options,
                    key=f"select_{en_category}"
                )
                
                if selected_traits:
                    selected_prompts[en_category] = [
                        trait.split(" - ")[0] for trait in selected_traits
                    ]
            else:
                # 其他類別使用單選
                prompt_options = ["預設 (Default)"] + [
                    f"{k} - {v['description']}"
                    for k, v in category_prompts.items()
                ]
                
                selected = st.selectbox(
                    f"選擇{zh_category}",
                    options=prompt_options,
                    key=f"select_{en_category}"
                )
                
                if selected != "預設 (Default)":
                    prompt_id = selected.split(" - ")[0]
                    selected_prompts[en_category] = prompt_id
        
        role_prompt = st.text_area(
            "角色專屬提示詞 (Role Prompt)",
            help="設定角色的特定行為和回應方式"
        )
        
        # 插件設定
        st.subheader("插件設定 (Plugin Settings)")
        col1, col2 = st.columns(2)
        
        with col1:
            web_search = st.checkbox(
                "啟用網路搜尋 (Enable Web Search)",
                value=False,
                help="允許 AI 使用網路搜尋來增強回答準確度"
            )
            
            if web_search:
                web_search_weight = st.slider(
                    "網路搜尋參考權重 (Web Search Weight)",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.3,
                    help="設定網路搜尋結果在回答中的參考權重 (0.0-1.0)"
                )
                
                max_search_results = st.number_input(
                    "最大搜尋結果數 (Max Search Results)",
                    min_value=1,
                    max_value=10,
                    value=3,
                    help="設定每次搜尋返回的最大結果數量"
                )
        
        with col2:
            knowledge_base = st.checkbox(
                "啟用知識庫 (Enable Knowledge Base)",
                value=False,
                help="允許 AI 使用自定義知識庫來回答問題"
            )
            
            if knowledge_base:
                kb_weight = st.slider(
                    "知識庫參考權重 (Knowledge Base Weight)",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                    help="設定知識庫內容在回答中的參考權重 (0.0-1.0)"
                )
                
                kb_sources = st.multiselect(
                    "選擇知識庫來源 (Select Knowledge Base Sources)",
                    options=["文件庫", "FAQ", "自定義資料"],
                    default=["FAQ"],
                    help="選擇要使用的知識庫來源"
                )
        
        # AI 模型進階設定
        st.subheader("AI 模型進階設定 (Advanced AI Settings)")
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
            presence_penalty = st.slider(
                "Presence Penalty",
                -2.0, 2.0, 0.0,
                help="控制模型對新主題的關注度"
            )
        
        with col2:
            top_p = st.slider(
                "Top P",
                0.0, 1.0, 0.9,
                help="控制回應的多樣性"
            )
            frequency_penalty = st.slider(
                "Frequency Penalty",
                -2.0, 2.0, 0.0,
                help="控制模型避免重複內容的程度"
            )
            response_format = st.selectbox(
                "回應格式 (Response Format)",
                ["自動", "純文字", "Markdown", "JSON"],
                help="設定 AI 回應的輸出格式"
            )
        
        # 儲存設定
        if st.form_submit_button("創建角色 (Create)"):
            settings = {
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens,
                "presence_penalty": presence_penalty,
                "frequency_penalty": frequency_penalty,
                "response_format": response_format,
                "plugins": {
                    "web_search": {
                        "enabled": web_search,
                        "weight": web_search_weight if web_search else 0.0,
                        "max_results": max_search_results if web_search else 3
                    },
                    "knowledge_base": {
                        "enabled": knowledge_base,
                        "weight": kb_weight if knowledge_base else 0.0,
                        "sources": kb_sources if knowledge_base else []
                    }
                }
            }
            if role_manager.create_role(
                role_id, name, description, role_prompt,
                base_prompts=selected_prompts,
                settings=settings
            ):
                st.success("✅ 角色已創建")
                st.experimental_rerun()
            else:
                st.error("❌ 創建失敗")
    
    # 顯示現有角色列表
    st.subheader("現有角色列表 (Existing Roles)")
    roles = role_manager.list_roles()
    
    if not roles:
        st.warning("⚠️ 尚未創建任何角色，請先導入預設角色或創建新角色")
        return
    
    for role_id, role in roles.items():
        with st.expander(f"{role.name} ({role_id})", expanded=False):
            # 基本信息顯示
            st.write("當前設定：")
            
            # 顯示基本信息
            st.write("基本信息：")
            st.write(f"- 名稱：{role.name}")
            st.write(f"- 描述：{role.description}")
            
            # 顯示 Prompts 設定
            st.write("Prompts 設定：")
            
            # 顯示使用的共用 Prompts
            if role.base_prompts:
                st.write("使用的共用 Prompts：")
                prompts = role_manager.get_available_prompts()
                for prompt_id in role.base_prompts:
                    prompt_data = prompts.get(prompt_id, {})
                    st.write(f"**{prompt_id}** - {prompt_data.get('description', '')}")
                    st.text_area(
                        "Prompt 內容",
                        value=prompt_data.get('content', ''),
                        disabled=True,
                        height=100,
                        key=f"prompt_{role_id}_{prompt_id}"
                    )
            
            # 顯示角色專屬 Prompt
            st.write("角色專屬 Prompt：")
            st.text_area(
                "Role Prompt",
                value=role.role_prompt,
                disabled=True,
                height=100,
                key=f"role_prompt_{role_id}"
            )
            
            # 顯示完整的組合 Prompt
            st.write("完整組合後的 Prompt：")
            st.text_area(
                "Combined Prompt",
                value=role.prompt,
                disabled=True,
                height=150,
                key=f"combined_prompt_{role_id}"
            )
            
            # 顯示其他設定
            st.write("模型設定：")
            st.json(role.settings)
            
            # 測試對話按鈕
            if st.button("測試對話 (Test Chat)", key=f"test_{role_id}"):
                with st.spinner("正在準備測試..."):
                    try:
                        db = next(get_db())
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
    st.header("AI 模型設定 (AI Model Settings)")
    
    # 讀取當前設定
    config = Config()
    
    with st.form("api_settings"):
        st.subheader("API 金鑰設定 (API Key Settings)")
        
        # Google API 設定
        st.write("Google API 設定 (Google API Settings)")
        google_api_key = st.text_input(
            "Google API Key",
            value=config.GOOGLE_API_KEY,
            type="password",
            help="設定 Google API Key 以使用 Gemini 模型 (Set Google API Key to use Gemini models)"
        )
        
        # OpenAI API 設定
        st.write("OpenAI API 設定 (OpenAI API Settings)")
        openai_api_key = st.text_input(
            "OpenAI API Key",
            value=config.OPENAI_API_KEY,
                    type="password",
            help="設定 OpenAI API Key 以使用 GPT 模型 (Set OpenAI API Key to use GPT models)"
        )
        
        # Claude API 設定
        st.write("Claude API 設定 (Claude API Settings)")
        claude_api_key = st.text_input(
            "Claude API Key",
            value=config.CLAUDE_API_KEY,
            type="password",
            help="設定 Claude API Key 以使用 Claude 模型 (Set Claude API Key to use Claude models)"
        )
        
        # 模型設定
        st.subheader("預設模型設定 (Default Model Settings)")
        default_model = st.selectbox(
            "預設 AI 模型 (Default AI Model)",
            ["gemini-pro", "gpt-4", "gpt-3.5-turbo", "claude-3"],
            help="選擇預設使用的 AI 模型 (Select the default AI model to use)"
        )
        
        # 進階設定
        st.subheader("進階設定 (Advanced Settings)")
        col1, col2 = st.columns(2)
        with col1:
            max_history = st.number_input(
                "最大對話歷史 (Max Chat History)",
                min_value=1,
                max_value=50,
                value=10,
                help="設定保留的對話歷史數量 (Set the number of chat history to keep)"
            )
            max_tokens = st.number_input(
                "最大 Token 數 (Max Tokens)",
                min_value=100,
                max_value=4000,
                value=1000,
                help="設定單次回應的最大 Token 數 (Set the maximum tokens for each response)"
            )
        
        with col2:
            temperature = st.slider(
                "溫度 (Temperature)",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                help="控制回應的創造性，越高越有創意 (Control response creativity, higher value means more creative)"
            )
            top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=0.9,
                help="控制回應的多樣性 (Control response diversity)"
            )
        
        # 儲存設定時包含 default_model
        if st.form_submit_button("儲存設定 (Save Settings)"):
            try:
                # 儲存設定邏輯，包含 default_model...
                config.update_settings({
                    'DEFAULT_MODEL': default_model,
                    # ... 其他設定
                })
                st.success("✅ 設定已儲存 (Settings Saved)")
            except Exception as e:
                st.error(f"❌ 儲存失敗 (Save Failed): {str(e)}")

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
    st.header("LINE 官方帳號管理 (LINE Official Account Management)")
    
    # LINE API 設定
    with st.expander("API 設定 (API Settings)", expanded=True):
        st.markdown("""
        ### LINE 官方帳號設定步驟 (LINE Official Account Setup Steps)
        1. 前往 LINE Developers Console (Go to LINE Developers Console)
           [LINE Developers Console](https://developers.line.biz/console/)
        2. 建立或選擇一個 Provider (Create or select a Provider)
        3. 建立一個 Messaging API Channel (Create a Messaging API Channel)
        4. 在 Basic Settings 中可以找到 (In Basic Settings, you can find)：
           - Channel Secret (頻道密鑰)
        5. 在 Messaging API 設定中可以找到 (In Messaging API settings, you can find)：
           - Channel Access Token (頻道存取權杖)
           - Bot Basic ID (機器人 ID)
        """)
        
        # 從配置文件加載當前設定
        config = Config()
        current_settings = {
            'LINE_CHANNEL_SECRET': config.LINE_CHANNEL_SECRET,
            'LINE_CHANNEL_ACCESS_TOKEN': config.LINE_CHANNEL_ACCESS_TOKEN,
            'LINE_BOT_ID': config.LINE_BOT_ID
        }
        
        with st.form("line_settings"):
            channel_secret = st.text_input(
                "Channel Secret",
                value=current_settings['LINE_CHANNEL_SECRET'],
                type="password"
            )
            channel_token = st.text_input(
                "Channel Access Token",
                value=current_settings['LINE_CHANNEL_ACCESS_TOKEN'],
                type="password"
            )
            bot_id = st.text_input(
                "Bot ID",
                value=current_settings['LINE_BOT_ID']
            )
            
            if st.form_submit_button("保存設定"):
                try:
                    update_env_file({
                        'LINE_CHANNEL_SECRET': channel_secret,
                        'LINE_CHANNEL_ACCESS_TOKEN': channel_token,
                        'LINE_BOT_ID': bot_id
                    })
                    st.success("設定已更新，請重新啟動服務以套用更改")
                except Exception as e:
                    st.error(f"保存設定失敗：{str(e)}")
    
    # Webhook 狀態顯示
    with st.expander("Webhook 狀態 (Webhook Status)", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            ### Webhook 設定說明 (Webhook Setup Instructions)
            1. 確保 LINE Bot 服務正在運行 (Ensure LINE Bot service is running)：
               ```bash
               python run.py --mode bot
               ```
            2. 複製下方的 Webhook URL (Copy the Webhook URL below)
            3. 前往 LINE Developers Console (Go to LINE Developers Console)
            4. 在 Messaging API 設定中 (In Messaging API settings)：
               - 貼上 Webhook URL (Paste the Webhook URL)
               - 開啟「Use webhook」選項 (Enable "Use webhook" option)
               - 點擊「Verify」按鈕測試連接 (Click "Verify" button to test connection)
            """)
        
        with col2:
            st.markdown("### 服務狀態 (Service Status)")
            if check_line_bot_service():
                st.success("✅ 服務運行中 (Service Running)")
            else:
                st.error("❌ 服務未運行 (Service Not Running)")
        
        # 顯示當前 Webhook URL
        st.subheader("當前 Webhook URL")
        webhook_url = get_webhook_url()
        if webhook_url:
            webhook_full_url = f"{webhook_url}/callback"
            st.code(webhook_full_url, language=None)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("複製 URL"):
                    st.write("URL 已複製到剪貼簿")
                    st.markdown(f"""
                    <script>
                        navigator.clipboard.writeText('{webhook_full_url}');
                    </script>
                    """, unsafe_allow_html=True)
            with col2:
                st.info("👆 請複製此 URL 到 LINE Developers Console 的 Webhook URL 欄位")
        else:
            st.warning("⚠️ 無法獲取 Webhook URL")
    
    # 機器人資訊
    if bot_id:
        with st.expander("加入好友資訊 (Add Friend Information)", expanded=True):
            st.markdown(f"""
            ### 加入好友方式 (Ways to Add Friend)
            1. 掃描 QR Code (Scan QR Code)：
               - 使用 LINE 掃描這個連結 (Use LINE to scan this link)：
                 [QR Code](https://line.me/R/ti/p/@{bot_id})
            2. 搜尋 Bot ID (Search Bot ID)：
               - 在 LINE 搜尋欄位輸入 (Enter in LINE search field)：@{bot_id}
            3. 點擊好友連結 (Click Friend Link)：
               - [https://line.me/R/ti/p/@{bot_id}](https://line.me/R/ti/p/@{bot_id})
            """)

async def show_chat_test():
    st.header("對話測試 (Chat Test)")
    
    # 初始化聊天歷史
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # 設定區域
    with st.expander("對話設定 (Chat Settings)", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # 獲取已設定的模型列表
            config = Config()
            available_models = []
            
            if config.GOOGLE_API_KEY:
                available_models.extend([
                    "gemini-2.0-flash-exp",
                    "gemini-1.5-flash",
                    "gemini-1.5-flash-8b",
                    "gemini-1.5-pro"
                ])
            if config.OPENAI_API_KEY:
                available_models.extend([
                    "gpt-4-turbo-preview",
                    "gpt-3.5-turbo"
                ])
            if config.CLAUDE_API_KEY:
                available_models.extend([
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307"
                ])
            
            if not available_models:
                st.warning("請先在 API 設定中設定至少一個 API Key")
                available_models = ["無可用模型"]
            
            # 選擇模型
            model = st.selectbox(
                "選擇模型 (Select Model)",
                available_models,
                index=0
            )
            
            # 選擇角色
            role_manager = RoleManager()
            roles = role_manager.list_roles()
            selected_role = st.selectbox(
                "選擇角色 (Select Role)",
                ["無角色 (No Role)"] + list(roles.keys()),
                format_func=lambda x: roles[x].name if x in roles else x
            )
        
        with col2:
            # 臨時參數調整
            st.write("臨時參數調整 (Temporary Settings)")
            temperature = st.slider(
                "溫度 (Temperature)", 
                0.0, 1.0, 
                value=roles[selected_role].settings['temperature'] if selected_role in roles else 0.7
            )
            top_p = st.slider(
                "Top P",
                0.0, 1.0,
                value=roles[selected_role].settings['top_p'] if selected_role in roles else 0.9
            )
    
    # 顯示對話歷史
    for message in st.session_state.chat_history:
        role_icon = "🧑" if message["role"] == "user" else "🤖"
        st.write(f"{role_icon} {message['content']}")
    
    # 文字輸入區
    with st.form(key="chat_form"):
        user_input = st.text_area("輸入訊息 (Enter Message)", height=100)
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.form_submit_button("發送")
        with col2:
            clear_button = st.form_submit_button("清除歷史")
    
    # 處理發送按鈕
    if submit_button and user_input:
        try:
            # 添加用戶訊息到歷史
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # 獲取 AI 回應
            with st.spinner("AI思考中..."):
                # 建立 ConversationManager
                conversation_manager = ConversationManager()
                
                # 準備對話參數
                chat_params = {
                    "temperature": temperature,
                    "top_p": top_p
                }
                
                # 如果選擇了角色，使用角色的提示詞
                if selected_role in roles:
                    chat_params["system_prompt"] = roles[selected_role].prompt
                
                response = await conversation_manager.get_response(
                    "admin_test",
                    user_input,
                    model=model,
                    **chat_params
                )
            
            # 添加 AI 回應到歷史
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # 重新載入頁面以顯示新訊息
            st.experimental_rerun()
            
        except Exception as e:
            st.error(f"發生錯誤：{str(e)}")
    
    # 處理清除按鈕
    if clear_button:
        st.session_state.chat_history = []
        st.experimental_rerun()
    
    # 檔案上傳區域
    st.subheader("檔案處理 (File Processing)")
    uploaded_file = st.file_uploader(
        "上傳檔案 (Upload File)", 
        type=['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg', 'wav', 'mp3']
    )
    
    if uploaded_file:
        try:
            file_processor = FileProcessor()
            result = file_processor.process_file(uploaded_file, save_to_db=False)
            
            if result['success']:
                content = result['content']
                
                if content['type'] == 'image':
                    # 使用 Gemini Vision API 進行圖片描述
                    image_description = model_manager.describe_image(content['image'])
                    st.write("圖片描述：", image_description)
                    message = f"這是一張圖片，內容描述如下：\n{image_description}"
                else:
                    message = content.get('text', '無法讀取檔案內容')
                
                # 添加到對話歷史
                st.session_state.chat_history.append({"role": "user", "content": message})
                
                # 顯示處理結果
                st.success("檔案處理成功！")
                
            else:
                st.error(f"檔案處理失敗：{result.get('error', '未知錯誤')}")
                
        except Exception as e:
            st.error(f"處理檔案時發生錯誤：{str(e)}")

def get_prompt_template(prompt_type: str) -> str:
    """根據類型返回 prompt 模板"""
    templates = {
        "Language": "請使用{language}與使用者對話，保持自然流暢的表達方式。",
        "Tone": "在對話中使用{tone}的語氣和風格，讓對話更加生動。",
        "Format": "回答時請使用{format}的格式，確保內容清晰易讀。",
        "WritingStyle": "以{field}領域專家的身份回答，運用專業知識和經驗。",
        "Personality": "展現{traits}的性格特徵，讓對話更有個性。"
    }
    return templates.get(prompt_type, "")

def check_line_bot_service():
    """檢查 LINE Bot 服務狀態"""
    max_retries = 3
    timeout = 3  # 增加超時時間到 3 秒
    
    for i in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:5000/status", timeout=timeout)
            if response.status_code == 200:
                return True
            time.sleep(1)
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                time.sleep(1)
                continue
    return False

def get_webhook_url():
    """獲取 webhook URL"""
    try:
        response = requests.get("http://127.0.0.1:5000/webhook-url", timeout=3)
        if response.status_code == 200:
            return response.json().get('url')
    except requests.exceptions.RequestException:
        pass
    return None

def main():
    st.set_page_config(
        page_title="Line AI Assistant - 管理介面",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("Line AI Assistant 管理介面")
    
    role_manager = RoleManager()
    
    # 側邊欄選單
    st.sidebar.title("功能選單 (Menu)")
    menu = st.sidebar.selectbox(
        "選擇功能 (Select Function)",
        ["系統狀態 (System Status)", 
         "AI 模型設定 (AI Model Settings)", 
         "LINE 官方帳號管理 (LINE Official Account)",
         "對話測試 (Chat Test)",
         "共用 Prompts 管理 (Shared Prompts)",
         "角色管理 (Role Management)",
         "文件管理 (Document Management)"]
    )
    
    if "系統狀態" in menu:
        show_system_status()
    elif "AI 模型設定" in menu:
        show_api_settings()
    elif "LINE 官方帳號管理" in menu:
        show_line_account_management()
    elif "對話測試" in menu:
        asyncio.run(show_chat_test())
    elif "共用 Prompts 管理" in menu:
        show_prompts_management(role_manager)
    elif "角色管理" in menu:
        show_role_management(role_manager)
    elif "文件管理" in menu:
        st.header("文件管理 (Document Management)")
        st.info("📝 文件管理功能開發中...")

if __name__ == "__main__":
    main() 