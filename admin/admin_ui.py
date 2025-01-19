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

def show_prompts_management(role_manager):
    st.header("共用 Prompts 管理")
    
    # 顯示預設和自定義的 Prompts
    categories = [
        "語言設定 (Language)", 
        "語氣風格 (Tone)", 
        "輸出格式 (Format)", 
        "專業領域 (Expertise)", 
        "性格特徵 (Personality)"
    ]
    
    for category in categories:
        with st.expander(f"{category}", expanded=False):
            # 獲取當前類別的英文標識（用於後端處理）
            category_id = category.split(" (")[1].rstrip(")")
            prompts = role_manager.get_prompts_by_category(category_id)
            
            # 顯示預設和自定義的 prompts
            st.subheader("預設 Prompts")
            default_prompts = {k: v for k, v in prompts.items() if v.get('is_default')}
            for prompt_id, data in default_prompts.items():
                with st.expander(f"{data['description']}", expanded=False):
                    st.text_area("內容", value=data['content'], disabled=True)
                    st.write(f"使用次數: {data['usage_count']}")
            
            st.subheader("自定義 Prompts")
            custom_prompts = {k: v for k, v in prompts.items() if not v.get('is_default')}
            if custom_prompts:
                for prompt_id, data in custom_prompts.items():
                    with st.expander(f"{data['description']}", expanded=False):
                        st.text_area("內容", value=data['content'], disabled=True)
                        st.write(f"使用次數: {data['usage_count']}")
                        if st.button("刪除", key=f"delete_{prompt_id}"):
                            if role_manager.delete_prompt(prompt_id):
                                st.success("已刪除")
                                st.experimental_rerun()
            else:
                st.info("尚未創建自定義 Prompts")
            
            # 創建新的自定義 prompt
            st.subheader(f"創建新的 {category.split(' (')[0]}")
            with st.form(f"create_prompt_{category_id}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    prompt_id = st.text_input(
                        "Prompt ID",
                        help="唯一標識符，例如：chinese_language"
                    )
                    description = st.text_input(
                        "描述 (Description)",
                        help="簡短描述這個 prompt 的用途"
                    )
                with col2:
                    prompt_type = st.selectbox(
                        "類型 (Type)",
                        ["Language", "Tone", "Personality", "Expertise", "Others"]
                    )
                
                content = st.text_area(
                    "Prompt 內容",
                    height=150,
                    help="prompt 的具體內容",
                    placeholder=get_prompt_template(prompt_type)
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    example_input = st.text_input(
                        "測試輸入 (Test Input)",
                        help="輸入一段測試文字來預覽效果"
                    )
                with col2:
                    if example_input:
                        st.write("預期效果預覽：")
                        st.write(content.replace("{input}", example_input))
                
                if st.form_submit_button("創建 Prompt"):
                    if prompt_id and content:
                        if role_manager.create_prompt(
                            prompt_id, 
                            content, 
                            description,
                            prompt_type=prompt_type,
                            category=category_id
                        ):
                            st.success("✅ Prompt 已創建")
                            st.experimental_rerun()
                        else:
                            st.error("❌ 創建失敗，ID 可能已存在")
                    else:
                        st.warning("⚠️ 請填寫必要欄位")

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
        available_prompts = role_manager.get_available_prompts()
        selected_prompts = st.multiselect(
            "選擇共用 Prompts",
            options=list(available_prompts.keys()),
            format_func=lambda x: f"{x} - {available_prompts[x].get('description', '')}",
            help="選擇要使用的共用 prompts"
        )
        
        role_prompt = st.text_area(
            "角色專屬提示詞 (Role Prompt)",
            help="設定角色的特定行為和回應方式"
        )
        
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
    st.header("LINE 官方帳號管理")
    
    # LINE API 設定
    with st.expander("API 設定", expanded=True):
        st.markdown("""
        ### LINE 官方帳號設定步驟
        1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
        2. 建立或選擇一個 Provider
        3. 建立一個 Messaging API Channel
        4. 在 Basic Settings 中可以找到：
           - Channel Secret (頻道密鑰)
        5. 在 Messaging API 設定中可以找到：
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
    with st.expander("Webhook 狀態", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            ### Webhook 設定說明
            1. 確保 LINE Bot 服務正在運行：
               ```bash
               python run.py --mode bot
               ```
            2. 複製下方的 Webhook URL
            3. 前往 [LINE Developers Console](https://developers.line.biz/console/)
            4. 在 Messaging API 設定中：
               - 貼上 Webhook URL
               - 開啟「Use webhook」選項
               - 點擊「Verify」按鈕測試連接
            """)
        
        with col2:
            st.markdown("### 服務狀態")
            if check_line_bot_service():
                st.success("✅ 服務運行中")
            else:
                st.error("❌ 服務未運行")
        
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
        with st.expander("加入好友資訊", expanded=True):
            st.markdown(f"""
            ### 加入好友方式
            1. 掃描 QR Code：
               - 使用 LINE 掃描 [這個連結](https://line.me/R/ti/p/@{bot_id})
            2. 搜尋 Bot ID：
               - 在 LINE 搜尋欄位輸入：@{bot_id}
            3. 點擊好友連結：
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
        "Expertise": "以{field}領域專家的身份回答，運用專業知識和經驗。",
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