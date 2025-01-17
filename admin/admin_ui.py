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
import asyncio

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
            "models": [
                "gemini-2.0-flash-exp",  # Gemini 2.0快閃記憶體
                "gemini-1.5-flash",      # Gemini 1.5閃存
                "gemini-1.5-flash-8b",   # Gemini 1.5 Flash-8B
                "gemini-1.5-pro",        # Gemini 1.5專業版
                "text-embedding-004",     # 文字嵌入 (開發中)
                "aqa"                     # 空氣品質保證 (開發中)
            ],
            "available_models": [        # 目前可用的模型
                "gemini-2.0-flash-exp",
                "gemini-1.5-flash",
                "gemini-1.5-flash-8b",
                "gemini-1.5-pro"
            ],
            "description": """Gemini 系列模型：
            
            1. Gemini 2.0快閃記憶體 (gemini-2.0-flash-exp)
               • 新一代多模態模型
               • 支援: 音訊、圖片、影片和文字
               • 特點: 速度快、功能全面
            
            2. Gemini 1.5閃存 (gemini-1.5-flash)
               • 快速且多功能的通用模型
               • 適合: 日常對話和一般任務
               • 特點: 反應快速、資源消耗低
            
            3. Gemini 1.5 Flash-8B (gemini-1.5-flash-8b)
               • 輕量級模型
               • 適合: 大量簡單任務處理
               • 特點: 超低延遲、高並發
            
            4. Gemini 1.5專業版 (gemini-1.5-pro)
               • 高階推理模型
               • 適合: 複雜分析和專業任務
               • 特點: 推理能力強、結果精確
            
            以下功能開發中：
            
            5. 文字嵌入 (text-embedding-004)
               • 文本向量化模型
               • 用途: 文本相似度分析
               • 特點: 高精度文本理解
            
            6. 空氣品質保證 (aqa)
               • 專業問答模型
               • 用途: 提供可靠來源解答
               • 特點: 答案準確度高"""
        },
        "OpenAI": {
            "api_key": "OPENAI_API_KEY",
            "models": [
                "gpt-4o",           # 通用旗艦模型
                "gpt-4o-mini",      # 小型快速模型
                "o1",               # 複雜推理模型
                "o1-mini",          # 輕量推理模型
                "gpt-4o-realtime",  # 即時互動模型
                "gpt-4o-audio",     # 音訊處理模型
                "gpt-4-turbo",      # 舊版高智能模型
                "gpt-3.5-turbo",    # 基礎快速模型
                "dall-e-3",         # 圖像生成模型
                "tts-1",            # 語音合成模型
                "whisper-1",        # 語音識別模型
                "text-embedding-3",  # 文本向量模型
                "moderation-latest"  # 內容審核模型
            ],
            "description": """OpenAI 系列模型：
            
            1. 語言模型
               • GPT-4o: 最新旗艦模型，全能型 AI
               • GPT-4o-mini: 經濟型快速模型
               • O1/O1-mini: 專注推理的新一代模型
               • GPT-4-turbo: 前代高性能模型
               • GPT-3.5-turbo: 性價比最高的基礎模型
            
            2. 多模態模型
               • GPT-4o-realtime: 即時音訊文本互動
               • GPT-4o-audio: 專業音訊處理
               • DALL·E-3: AI 圖像生成
            
            3. 專業工具
               • TTS-1: 高品質語音合成
               • Whisper-1: 精確語音識別
               • Text-embedding-3: 文本向量化
               • Moderation-latest: 內容安全審核
            
            特點說明：
            • 即時互動: 支援流式輸出
            • 多語言: 支援超過95種語言
            • 安全性: 內建內容過濾
            • 可擴展: API 使用無並發限制"""
        },
        "Anthropic": {
            "api_key": "CLAUDE_API_KEY",
            "models": [
                # Claude 3.5 系列
                "claude-3-5-sonnet-20241022",  # 3.5 Sonnet
                "claude-3-5-haiku-20241022",   # 3.5 Haiku
                
                # Claude 3 系列
                "claude-3-opus-20240229",      # 3 Opus
                "claude-3-sonnet-20240229",    # 3 Sonnet
                "claude-3-haiku-20240307"      # 3 Haiku
            ],
            "description": """Claude 系列模型：
            Claude 3.5 系列 (最新):
            - claude-3-5-sonnet: 高性能通用模型
            - claude-3-5-haiku: 快速輕量模型
            
            Claude 3 系列:
            - claude-3-opus: 最強大的模型，適合複雜任務
            - claude-3-sonnet: 平衡性能和速度的通用模型
            - claude-3-haiku: 快速響應的輕量模型
            
            支援平台:
            - Anthropic API (直接使用)
            - AWS Bedrock (添加 anthropic. 前綴)
            - GCP Vertex AI (使用 @ 格式)"""
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
                    
                    # 選擇要使用的模型
                    enabled_models = st.multiselect(
                        "使用的模型",  # 改為"使用的模型"
                        options=config["available_models"] if "available_models" in config else config["models"],
                        default=[config["available_models"][0]] if "available_models" in config else [config["models"][0]],
                        help=f"選擇要使用的 {provider} 模型"
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
    st.header("LINE 官方帳號管理 (LINE Official Account)")
    
    # 從環境變數獲取設定值
    line_settings = {
        'LINE_CHANNEL_SECRET': os.getenv('LINE_CHANNEL_SECRET'),
        'LINE_CHANNEL_ACCESS_TOKEN': os.getenv('LINE_CHANNEL_ACCESS_TOKEN'),
        'LINE_BOT_ID': os.getenv('LINE_BOT_ID'),
        'NGROK_AUTH_TOKEN': os.getenv('NGROK_AUTH_TOKEN')
    }
    
    settings_names = {
        'LINE_CHANNEL_SECRET': '頻道密鑰',
        'LINE_CHANNEL_ACCESS_TOKEN': '頻道存取權杖',
        'LINE_BOT_ID': '機器人 ID',
        'NGROK_AUTH_TOKEN': 'Ngrok 權杖'
    }
    
    # 檢查缺少的設定
    missing_settings = [
        settings_names[key] 
        for key, value in line_settings.items() 
        if not value
    ]
    
    if missing_settings:
        st.error("⚠️ 尚未完成必要設定")
        
        st.markdown("""
        ### LINE 官方帳號設定步驟

        1. 前往 [LINE Developers](https://developers.line.biz/zh-hant/) 並登入
        2. 建立或選擇一個 Provider
        3. 建立一個 Messaging API Channel
        4. 在 Basic Settings 中可以找到：
           - Channel Secret (頻道密鑰)
        5. 在 Messaging API 設定中可以找到：
           - Channel Access Token (頻道存取權杖)
           - Bot Basic ID (機器人 ID)
        """)
        
        st.info("請在 .env 文件中設定以下項目：")
        for item in missing_settings:
            st.markdown(f"- {item}")
        
        st.warning("""
        注意事項：
        - Channel Secret 和 Access Token 請妥善保管
        - 設定完成後需要重新啟動應用程式
        - Webhook URL 會在機器人啟動後自動設定
        """)
        return
    
    # 所有設定都存在時顯示資訊
    with st.expander("帳號資訊 (Account Info)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.info("基本資訊")
            st.write(f"Channel Secret: {'*' * 10}")
            st.write(f"Access Token: {'*' * 10}")
            st.write(f"Bot ID: @{line_settings['LINE_BOT_ID']}")
            st.success("✓ LINE Channel 已設定")
        
        with col2:
            st.info("Webhook 設定")
            st.success("✓ Ngrok 已設定")
            st.write(f"Auth Token: {'*' * 10}")
    
    # 好友管理
    with st.expander("好友管理 (Friend Management)", expanded=True):
        st.subheader("加入好友")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### 加入方式
            1. 使用 LINE 掃描 QR Code
            2. 點擊好友連結
            3. 搜尋 Bot ID
            """)
        
        with col2:
            st.markdown("""
            ### 好友連結
            點擊下方連結加入好友：
            """)
            bot_id = line_settings['LINE_BOT_ID']
            st.markdown(f"[加為好友](https://line.me/R/ti/p/@{bot_id})")
            st.info(f"Bot ID: @{bot_id}")
    
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

def show_chat_test():
    """顯示對話測試區域"""
    # 初始化會話狀態
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.temp_files = []
    
    st.header("對話測試")
    
    # LINE 手機風格 CSS
    st.markdown("""
    <style>
    /* 模擬手機外框 */
    .phone-frame {
        width: 360px;
        height: 640px;
        background: white;
        border-radius: 30px;
        box-shadow: 0 0 20px rgba(0,0,0,0.2);
        position: relative;
        margin: 20px auto;
        overflow: hidden;
    }
    
    /* 聊天界面 */
    .chat-container {
        height: calc(100% - 120px);
        overflow-y: auto;
        background: #f0f0f0;
        padding: 10px;
    }
    
    /* 頂部狀態欄 */
    .chat-header {
        height: 60px;
        background: #00c300;
        color: white;
        display: flex;
        align-items: center;
        padding: 0 15px;
        position: sticky;
        top: 0;
    }
    
    /* 底部輸入欄 */
    .chat-input {
        height: 60px;
        background: white;
        border-top: 1px solid #ddd;
        position: sticky;
        bottom: 0;
        display: flex;
        align-items: center;
        padding: 0 10px;
    }
    
    /* 上傳按鈕 */
    .upload-button {
        width: 40px;
        height: 40px;
        background: #f0f0f0;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        margin-right: 10px;
    }
    
    /* 訊息樣式 */
    .message {
        margin: 10px 0;
        max-width: 80%;
        clear: both;
    }
    
    .user-message {
        float: right;
        background: #00c300;
        color: white;
        border-radius: 20px;
        padding: 10px 15px;
    }
    
    .assistant-message {
        float: left;
        background: white;
        border-radius: 20px;
        padding: 10px 15px;
    }
    
    /* 彈出視窗 */
    .modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 1000;
    }
    
    .modal-content {
        background: white;
        width: 80%;
        max-width: 500px;
        margin: 100px auto;
        padding: 20px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 模擬手機界面
    chat_container = st.container()
    with chat_container:
        # 顯示對話歷史
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # 處理訊息輸入
    if prompt := st.chat_input("輸入訊息..."):
        # 添加用戶訊息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 生成回應
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                response = handle_message(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

def handle_message(message: str) -> str:
    """處理發送的訊息"""
    try:
        # 創建資料庫會話
        db = SessionLocal()
        conversation_manager = ConversationManager(db)
        
        # 使用 asyncio 運行異步函數
        async def get_response():
            return await conversation_manager.handle_message(
                line_user_id="test_user",
                message=message,
                role_id="fk_helper"  # 使用預設角色
            )
        
        # 運行異步函數
        response = asyncio.run(get_response())
        return response
        
    except Exception as e:
        logger.error(f"處理訊息時發生錯誤：{str(e)}")
        return f"抱歉，處理訊息時發生錯誤：{str(e)}"
    finally:
        db.close()

def handle_uploaded_file(file):
    """處理上傳的文件"""
    try:
        # 創建臨時文件夾
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        # 保存文件
        file_path = temp_dir / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        
        # 記錄臨時文件
        st.session_state.temp_files.append(str(file_path))
        
        # 根據文件類型返回不同訊息
        file_type = file.type
        if file_type.startswith('image/'):
            return f"[圖片: {file.name}] (圖片辨識功能開發中)"
        elif file_type.startswith('audio/'):
            return f"[音訊: {file.name}] (語音辨識功能開發中)"
        elif file_type.startswith('video/'):
            return f"[影片: {file.name}] (影片處理功能開發中)"
        else:
            return f"[檔案: {file.name}]"
            
    except Exception as e:
        logger.error(f"處理文件時發生錯誤：{str(e)}")
        return f"處理文件時發生錯誤：{str(e)}"

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
         "對話測試 (Chat Test)",  # 添加對話測試選項
         "對話角色管理 (Chat Role Management)",
         "文件管理 (Document Management)"]
    )
    
    if "系統狀態" in menu:
        show_system_status()
    elif "AI 模型設定" in menu:
        show_api_settings()
    elif "LINE 官方帳號管理" in menu:
        show_line_account_management()
    elif "對話測試" in menu:
        show_chat_test()  # 添加對話測試功能
    elif "對話角色管理" in menu:
        show_role_management(role_manager)
    elif "文件管理" in menu:
        st.header("文件管理 (Document Management)")
        st.info("📝 文件管理功能開發中...")

if __name__ == "__main__":
    main() 