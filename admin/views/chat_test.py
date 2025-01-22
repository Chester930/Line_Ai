import streamlit as st
from shared.ai.chat_tester import ChatTester
from shared.config.config import Config
from shared.config.model_descriptions import MODEL_DESCRIPTIONS
from shared.ai.model_manager import ModelManager
from shared.database.models import Role, KnowledgeBase
from shared.utils.plugin_manager import PluginManager
from shared.plugins.web_search import WebSearchPlugin
from shared.plugins.youtube_subtitle import YouTubeSubtitlePlugin
from shared.plugins.web_browser import WebBrowserPlugin
from shared.database.database import SessionLocal
from shared.utils.role_manager import RoleManager
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

def get_available_models(config: Config) -> list:
    """獲取已配置的可用模型列表"""
    available_models = []
    
    # OpenAI Models
    if config.get("OPENAI_API_KEY"):
        openai_models = MODEL_DESCRIPTIONS.get("OpenAI 模型", {})
        for model_id, model_info in openai_models.items():
            if not model_info.get("deprecated", False):
                available_models.append({
                    "name": model_info["name"],
                    "id": model_info["model_ids"]["openai"],
                    "description": model_info["description"],
                    "provider": "OpenAI",
                    "features": model_info["features"]
                })
    
    # Google Models
    if config.get("GOOGLE_API_KEY"):
        google_models = MODEL_DESCRIPTIONS.get("Google Gemini 模型", {})
        for model_id, model_info in google_models.items():
            if not model_info.get("deprecated", False):
                available_models.append({
                    "name": model_info["name"],
                    "id": model_info["model_ids"]["google"],
                    "description": model_info["description"],
                    "provider": "Google",
                    "features": model_info["features"]
                })
    
    # Claude Models
    if config.get("ANTHROPIC_API_KEY"):
        claude_models = MODEL_DESCRIPTIONS.get("Claude 模型", {})
        for model_id, model_info in claude_models.items():
            available_models.append({
                "name": model_info["name"],
                "id": model_info["model_ids"]["anthropic"],
                "description": model_info["description"],
                "provider": "Anthropic",
                "features": model_info["features"]
            })
    
    return available_models

def show_page():
    """對話測試頁面"""
    st.header("對話測試")
    
    # 初始化聊天記錄和插件管理器
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        # 添加初始系統提示，包含時間信息
        current_time = datetime.now()
        st.session_state.chat_history.append({
            "role": "system",
            "content": f"當前時間是 {current_time.strftime('%Y年%m月%d日 %H:%M:%S')}。你可以回答與時間日期相關的問題。每次對話時請使用最新的系統時間。"
        })
    
    config = Config()
    role_manager = RoleManager()
    plugin_manager = PluginManager()
    
    # 註冊插件
    web_search_plugin = WebSearchPlugin()
    web_browser_plugin = WebBrowserPlugin()
    youtube_plugin = YouTubeSubtitlePlugin()
    
    plugin_manager.register_plugin(web_search_plugin)
    plugin_manager.register_plugin(web_browser_plugin)
    plugin_manager.register_plugin(youtube_plugin)
    
    # 基本設定區域
    with st.container():
        st.subheader("對話設定")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 選擇角色
            roles = role_manager.list_roles()
            if roles:
                role_options = ["無"] + [f"{role.name} ({role_id})" for role_id, role in roles.items()]
                selected_role_name = st.selectbox(
                    "選擇角色",
                    options=role_options,
                    format_func=lambda x: "不使用角色" if x == "無" else x,
                    help="選擇預設角色進行對話"
                )
                
                # 獲取選擇的角色
                selected_role = None
                if selected_role_name != "無":
                    role_id = selected_role_name.split("(")[-1].strip(")")
                    selected_role = roles.get(role_id)
                    
                    # 顯示角色資訊
                    if selected_role:
                        st.info(f"**角色描述：** {selected_role.description}")
                        
                        # 顯示角色的提示詞
                        if selected_role.base_prompts:
                            st.write("**使用的提示詞：**")
                            available_prompts = role_manager.get_available_prompts()
                            for prompt_id in selected_role.base_prompts:
                                if prompt_id in available_prompts:
                                    st.write(f"- {available_prompts[prompt_id].get('description', prompt_id)}")
            
            # 插件選擇
            st.write("**插件功能**")
            available_plugins = {
                "web_search": {
                    "name": "網路搜尋",
                    "description": "允許 AI 助手搜尋並參考網路上的最新資訊"
                },
                "web_browser": {
                    "name": "網頁瀏覽",
                    "description": "允許 AI 助手瀏覽和解析網頁內容"
                },
                "youtube_subtitle": {
                    "name": "YouTube 字幕",
                    "description": "允許 AI 助手處理 YouTube 影片字幕內容，理解影片大意"
                }
            }
            
            # 獲取已啟用的插件
            enabled_plugins = []
            for plugin_id, plugin_info in available_plugins.items():
                plugin = plugin_manager.get_plugin(plugin_id)
                if plugin and plugin.config.get("enabled", False):
                    enabled_plugins.append(plugin_id)
            
            selected_plugins = []
            if enabled_plugins:
                selected_plugins = st.multiselect(
                    "選擇要使用的插件",
                    options=enabled_plugins,
                    default=enabled_plugins,  # 默認選中所有啟用的插件
                    format_func=lambda x: available_plugins[x]["name"],
                    help="可以選擇多個插件同時使用"
                )
                
                # 顯示已選插件的說明
                if selected_plugins:
                    st.write("**已選插件說明：**")
                    for plugin_id in selected_plugins:
                        plugin_info = available_plugins[plugin_id]
                        st.info(f"**{plugin_info['name']}**: {plugin_info['description']}")
            else:
                st.warning("⚠️ 尚未啟用任何插件，請前往「插件管理」頁面設定")
            
            # 選擇模型（如果沒有選擇角色或角色允許自定義模型）
            if not selected_role or selected_role.settings.get("allow_model_selection", True):
                available_models = get_available_models(config)
                if available_models:
                    model = st.selectbox(
                        "選擇語言模型",
                        available_models,
                        format_func=lambda x: x["name"],
                        help="選擇要使用的語言模型"
                    )
                    st.info(model["description"])
                else:
                    st.error("⚠️ 尚未設定任何可用的語言模型")
                    st.info("👉 前往「AI 模型設定」頁面進行設定")
                    return
        
        with col2:
            # 模型參數設定（如果沒有選擇角色或角色允許自定義參數）
            if not selected_role or selected_role.settings.get("allow_parameter_adjustment", True):
                st.write("**參數設定**")
                temperature = st.slider(
                    "溫度 (Temperature)", 
                    0.0, 1.0, 
                    value=selected_role.settings.get("temperature", 0.7) if selected_role else 0.7,
                    help="控制回答的創造性"
                )
                
                max_tokens = st.number_input(
                    "最大長度",
                    min_value=100,
                    max_value=4000,
                    value=selected_role.settings.get("max_tokens", 1000) if selected_role else 1000,
                    help="控制回答的最大長度"
                )
            else:
                temperature = selected_role.settings.get("temperature", 0.7)
                max_tokens = selected_role.settings.get("max_tokens", 1000)
    
    # 顯示對話歷史
    st.subheader("對話歷史")
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            # 跳過系統消息的顯示
            if message["role"] == "system":
                # 如果是字幕相關的系統消息，顯示一個簡短的提示
                if "YouTube 影片" in message["content"]:
                    with st.chat_message("system", avatar="🎥"):
                        st.caption("AI 已接收影片字幕內容")
                continue
            
            role_icon = "🧑" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=role_icon):
                st.write(message["content"])
    
    # 文字輸入區
    with st.form(key="chat_form"):
        # 初始化 session state
        if "input_key" not in st.session_state:
            st.session_state.input_key = 0
            
        user_input = st.text_area(
            "輸入訊息", 
            key=f"input_area_{st.session_state.input_key}",
            height=100,
            placeholder="在此輸入您的訊息..."
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.form_submit_button("發送", use_container_width=True)
        with col2:
            clear_button = st.form_submit_button("清除歷史", type="secondary", use_container_width=True)
    
    # 處理發送按鈕
    if submit_button and user_input:
        try:
            # 保存當前輸入
            current_input = user_input
            
            # 立即更新 input key 來清空輸入欄
            st.session_state.input_key += 1
            
            # 更新系統時間信息
            current_time = datetime.now()
            st.session_state.chat_history.append({
                "role": "system",
                "content": f"當前時間更新：{current_time.strftime('%Y年%m月%d日 %H:%M:%S')}"
            })

            # 檢查是否包含 URL
            url_pattern = re.compile(
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            )
            
            # 檢查是否是搜尋請求
            search_patterns = [
                r'^搜尋\s+(.+)$',
                r'^search\s+(.+)$',
                r'^尋找\s+(.+)$',
                r'^查詢\s+(.+)$'
            ]
            
            # 處理 YouTube 影片
            if "youtube_subtitle" in selected_plugins and "youtube.com" in user_input:
                # 從用戶輸入中提取 YouTube URL
                youtube_urls = re.findall(r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([^&\s]+)', user_input)
                
                if youtube_urls:
                    st.info("🎥 檢測到 YouTube 影片連結，正在處理字幕...")
                    # 調用 YouTube 字幕插件
                    youtube_plugin = plugin_manager.get_plugin("youtube_subtitle")
                    if youtube_plugin:
                        # 只處理第一個找到的 URL
                        video_url = f"https://youtube.com/watch?v={youtube_urls[0]}"
                        result = youtube_plugin.execute(video_url)
                        if result["success"]:
                            subtitles = result["subtitles"]
                            video_id = result["video_id"]
                            # 使用小型 expander 顯示簡短提示
                            with st.expander("🎥 已處理影片字幕", expanded=False):
                                st.caption(f"已成功提取 YouTube 影片 ({video_id}) 的字幕內容供 AI 參考")
                            # 在用戶輸入中只添加簡短提示
                            user_input += "\n[已提取影片字幕供 AI 參考]"
                            # 將字幕內容作為系統消息添加到歷史（只給 AI 使用）
                            st.session_state.chat_history.append({
                                "role": "system",
                                "content": f"[此消息僅供 AI 參考] YouTube 影片 {video_id} 的字幕內容：\n" + "\n".join(segment['text'] for segment in subtitles)
                            })
                        else:
                            st.error(f"無法獲取字幕：{result.get('error', '未知錯誤')}")
            
            # 處理網頁瀏覽
            elif "web_browser" in selected_plugins and url_pattern.search(user_input):
                st.info("🌐 檢測到網址，正在讀取網頁內容...")
                web_browser = plugin_manager.get_plugin("web_browser")
                if web_browser:
                    urls = url_pattern.findall(user_input)
                    for url in urls[:1]:  # 只處理第一個 URL
                        result = web_browser.execute(url)
                        if result["success"]:
                            content = result["content"]
                            # 使用 expander 顯示簡短提示
                            with st.expander("🌐 網頁內容摘要", expanded=False):
                                st.caption(f"已讀取網頁：{content['title']}")
                            # 將網頁內容作為系統消息添加到歷史
                            st.session_state.chat_history.append({
                                "role": "system",
                                "content": f"[網頁內容] 標題：{content['title']}\n\n{content['text'][:1000]}..."
                            })
                            user_input += "\n[已讀取網頁內容供 AI 參考]"
                        else:
                            st.error(f"無法讀取網頁：{result.get('error', '未知錯誤')}")

            # 處理搜尋請求
            elif "web_search" in selected_plugins:
                # 檢查是否是搜尋指令
                search_match = None
                for pattern in search_patterns:
                    match = re.match(pattern, user_input)
                    if match:
                        search_match = match
                        break
                
                # 如果不是搜尋指令但包含問題，也進行搜尋
                if not search_match and any(keyword in user_input.lower() for keyword in ["最新", "新聞", "最近", "報導", "消息"]):
                    search_query = user_input
                else:
                    search_query = search_match.group(1) if search_match else None

                if search_query:
                    st.info("🔍 正在搜尋相關資訊...")
                    web_search = plugin_manager.get_plugin("web_search")
                    if web_search:
                        results = web_search.execute(search_query)
                        if results:
                            # 使用 expander 顯示搜尋結果摘要
                            with st.expander("🔍 搜尋結果摘要", expanded=False):
                                st.caption(f"已找到 {len(results)} 筆相關資訊")
                            # 將搜尋結果作為系統消息添加到歷史
                            search_content = f"[搜尋結果] 關鍵字：{search_query}\n\n"
                            for result in results:
                                search_content += f"- {result['title']}\n{result['snippet']}\n來源：{result['link']}\n\n"
                            st.session_state.chat_history.append({
                                "role": "system",
                                "content": search_content
                            })
                            user_input += "\n[已取得網路搜尋結果供 AI 參考]"
                        else:
                            st.warning("未找到相關資訊")

            # 添加用戶訊息到歷史
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # 獲取 AI 回應
            with st.spinner("AI思考中..."):
                chat_tester = ChatTester()
                response = chat_tester.get_response(
                    messages=st.session_state.chat_history,
                    model=model["id"] if not selected_role else selected_role.settings.get("model", model["id"]),
                    temperature=temperature,
                    max_tokens=max_tokens,
                    role=selected_role,
                    plugins=selected_plugins
                )
            
            # 添加 AI 回應到歷史
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # 重新運行頁面以更新顯示
            st.rerun()
            
        except Exception as e:
            logger.error(f"對話失敗: {e}")
            st.error(f"發生錯誤：{str(e)}")
            # 發生錯誤時也更新 input key
            st.session_state.input_key += 1
    
    # 處理清除按鈕
    if clear_button:
        st.session_state.chat_history = []
        st.session_state.input_key += 1
        st.rerun()
    
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
                    image_description = chat_tester.describe_image(content['image'])
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