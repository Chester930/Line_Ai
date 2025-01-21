import streamlit as st
from shared.ai.chat_tester import ChatTester
from shared.config.config import Config
from shared.database.models import Role, KnowledgeBase
from shared.utils.plugin_manager import PluginManager
from shared.database.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

def show_page():
    """對話測試頁面"""
    st.header("對話測試")
    
    # 初始化聊天記錄
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # 獲取配置和插件管理器
    config = Config()
    plugin_manager = PluginManager()
    
    # 設定區域
    with st.container():
        st.subheader("對話設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 選擇語言模型
            available_models = []
            if config.get("OPENAI_API_KEY"):
                available_models.append("gpt-3.5-turbo")
                available_models.append("gpt-4")
            if config.get("GOOGLE_API_KEY"):
                available_models.append("gemini-pro")
            if config.get("ANTHROPIC_API_KEY"):
                available_models.append("claude-3-sonnet")
            
            if available_models:
                model = st.selectbox(
                    "選擇模型 (Select Model)",
                    available_models,
                    help="選擇要使用的語言模型，需要在模型設定頁面配置對應的 API 金鑰"
                )
            else:
                st.error("⚠️ 尚未設定任何可用的語言模型，請先在模型設定頁面配置 API 金鑰")
                model = None
            
            # 選擇角色
            with SessionLocal() as db:
                roles = db.query(Role).filter(Role.is_enabled == True).all()
                if roles:
                    role_names = ["無"] + [role.name for role in roles]
                    selected_role = st.selectbox(
                        "選擇角色 (Select Role)",
                        role_names,
                        help="選擇要使用的預設角色，需要在角色管理頁面創建和啟用"
                    )
                else:
                    st.warning("⚠️ 尚未創建任何角色，可以在角色管理頁面創建")
                    selected_role = None
        
        with col2:
            # 臨時參數調整
            st.write("臨時參數調整 (Temporary Settings)")
            temperature = st.slider(
                "溫度 (Temperature)", 
                0.0, 1.0, 
                value=0.7,
                help="控制回答的創造性，較高的值會產生更多樣化的回答"
            )
            top_p = st.slider(
                "Top P",
                0.0, 1.0,
                value=0.9,
                help="控制回答的保守程度，較低的值會產生更保守的回答"
            )
    
    # 插件設定
    with st.container():
        st.subheader("插件設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 網路搜尋插件
            web_search_plugin = plugin_manager.get_plugin("web_search")
            if web_search_plugin and web_search_plugin.initialize():
                web_search = st.checkbox(
                    "網路搜尋 (Web Search)",
                    value=False,
                    help="啟用網路搜尋功能，需要在插件管理頁面配置搜尋引擎 API"
                )
                
                if web_search:
                    web_search_weight = st.slider(
                        "搜尋參考權重",
                        0.0, 1.0,
                        value=web_search_plugin.config.get("weight", 0.3),
                        help="控制搜尋結果在回答中的參考程度"
                    )
            else:
                st.warning("⚠️ 網路搜尋插件未啟用或配置不完整")
                web_search = False
        
        with col2:
            # 知識庫選擇
            with SessionLocal() as db:
                knowledge_bases = db.query(KnowledgeBase).all()
                if knowledge_bases:
                    kb_names = ["無"] + [kb.name for kb in knowledge_bases]
                    selected_kb = st.selectbox(
                        "選擇知識庫 (Select Knowledge Base)",
                        kb_names,
                        help="選擇要參考的知識庫，需要在知識庫管理頁面創建和上傳文件"
                    )
                    
                    if selected_kb != "無":
                        kb_weight = st.slider(
                            "知識庫參考權重",
                            0.0, 1.0,
                            value=0.5,
                            help="控制知識庫內容在回答中的參考程度"
                        )
                else:
                    st.warning("⚠️ 尚未創建任何知識庫，可以在知識庫管理頁面創建")
                    selected_kb = None
    
    # 顯示對話歷史
    st.subheader("對話歷史")
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
    if submit_button and user_input and model:
        try:
            # 添加用戶訊息到歷史
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # 獲取 AI 回應
            with st.spinner("AI思考中..."):
                chat_tester = ChatTester()
                
                # 準備對話參數
                chat_params = {
                    "model": model,
                    "temperature": temperature,
                    "top_p": top_p
                }
                
                # 添加角色設定
                if selected_role and selected_role != "無":
                    with SessionLocal() as db:
                        role = db.query(Role).filter(Role.name == selected_role).first()
                        if role:
                            chat_params["role"] = role
                
                # 添加知識庫設定
                if selected_kb and selected_kb != "無":
                    with SessionLocal() as db:
                        kb = db.query(KnowledgeBase).filter(KnowledgeBase.name == selected_kb).first()
                        if kb:
                            chat_params["knowledge_base"] = {
                                "id": kb.id,
                                "weight": kb_weight
                            }
                
                # 添加插件設定
                if web_search and web_search_plugin:
                    chat_params["plugins"] = {
                        "web_search": {
                            "enabled": True,
                            "weight": web_search_weight
                        }
                    }
                
                response = chat_tester.get_response(
                    messages=st.session_state.chat_history,
                    **chat_params
                )
            
            # 添加 AI 回應到歷史
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # 重新載入頁面以顯示新訊息
            st.experimental_rerun()
            
        except Exception as e:
            logger.error(f"對話失敗: {e}")
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