import streamlit as st
from shared.utils.plugin_manager import PluginManager

def show_page():
    """插件功能管理頁面"""
    st.header("插件功能管理")
    
    # 網路搜尋插件
    with st.expander("網路搜尋 (Web Search)", expanded=True):
        show_web_search_plugin()
    
    # 知識庫插件
    with st.expander("知識庫 (Knowledge Base)", expanded=True):
        show_knowledge_base_plugin()
    
    # 即將推出的插件
    with st.expander("即將推出 (Coming Soon)", expanded=True):
        show_upcoming_plugins()

def show_web_search_plugin():
    """顯示網路搜尋插件設定"""
    plugin_manager = PluginManager()
    current_config = plugin_manager.get_plugin_config('web_search') or {}
    
    with st.form("web_search_settings"):
        enabled = st.checkbox(
            "啟用插件",
            value=current_config.get('enabled', True),
            help="開啟或關閉網路搜尋功能"
        )
        
        if enabled:
            col1, col2 = st.columns(2)
            with col1:
                search_engine = st.selectbox(
                    "搜尋引擎",
                    ["Google", "Bing", "DuckDuckGo"],
                    index=["Google", "Bing", "DuckDuckGo"].index(
                        current_config.get('engine', 'Google')
                    ),
                    help="選擇要使用的搜尋引擎"
                )
                max_results = st.number_input(
                    "最大結果數",
                    1, 10, current_config.get('max_results', 3),
                    help="每次搜尋返回的最大結果數量"
                )
            
            with col2:
                weight = st.slider(
                    "搜尋結果權重",
                    0.0, 1.0, current_config.get('weight', 0.3),
                    help="搜尋結果在回答中的參考權重"
                )
                timeout = st.number_input(
                    "搜尋超時 (秒)",
                    1, 30, current_config.get('timeout', 10),
                    help="搜尋請求的最大等待時間"
                )
        
        if st.form_submit_button("儲存設定"):
            try:
                new_config = {
                    'enabled': enabled,
                    'engine': search_engine,
                    'max_results': max_results,
                    'weight': weight,
                    'timeout': timeout
                } if enabled else {'enabled': False}
                
                if plugin_manager.update_plugin_config('web_search', new_config):
                    st.success("✅ 設定已更新")
                else:
                    st.error("❌ 更新失敗")
            except Exception as e:
                st.error(f"❌ 更新失敗: {str(e)}")

def show_knowledge_base_plugin():
    """顯示知識庫插件設定"""
    plugin_manager = PluginManager()
    current_config = plugin_manager.get_plugin_config('knowledge_base') or {}
    
    with st.form("kb_settings"):
        enabled = st.checkbox(
            "啟用插件",
            value=current_config.get('enabled', True),
            help="開啟或關閉知識庫功能"
        )
        
        if enabled:
            col1, col2 = st.columns(2)
            with col1:
                embedding_model = st.selectbox(
                    "Embedding 模型",
                    ["sentence-transformers", "OpenAI Ada", "自定義"],
                    index=["sentence-transformers", "OpenAI Ada", "自定義"].index(
                        current_config.get('embedding_model', 'sentence-transformers')
                    ),
                    help="選擇用於生成文本向量的模型"
                )
                chunk_size = st.number_input(
                    "分塊大小",
                    100, 1000, current_config.get('chunk_size', 500),
                    help="文檔切分的大小（字符數）"
                )
            
            with col2:
                weight = st.slider(
                    "知識庫權重",
                    0.0, 1.0, current_config.get('weight', 0.5),
                    help="知識庫內容在回答中的參考權重"
                )
                similarity_threshold = st.slider(
                    "相似度閾值",
                    0.0, 1.0, current_config.get('similarity_threshold', 0.7),
                    help="選擇相關內容的最低相似度要求"
                )
        
        if st.form_submit_button("儲存設定"):
            try:
                new_config = {
                    'enabled': enabled,
                    'embedding_model': embedding_model,
                    'chunk_size': chunk_size,
                    'weight': weight,
                    'similarity_threshold': similarity_threshold
                } if enabled else {'enabled': False}
                
                if plugin_manager.update_plugin_config('knowledge_base', new_config):
                    st.success("✅ 設定已更新")
                else:
                    st.error("❌ 更新失敗")
            except Exception as e:
                st.error(f"❌ 更新失敗: {str(e)}")

def show_upcoming_plugins():
    """顯示即將推出的插件"""
    st.markdown("""
    ### 開發中的插件 (Plugins in Development)
    
    1. **多媒體處理插件 (Multimedia Processing)**
       - 圖片分析和生成
       - 語音轉文字
       - 文字轉語音
    
    2. **資料分析插件 (Data Analysis)**
       - 數據視覺化
       - 統計分析
       - 報表生成
    
    3. **工具集成插件 (Tool Integration)**
       - 日程管理
       - 天氣查詢
       - 翻譯服務
    
    4. **自動化工作流插件 (Workflow Automation)**
       - 任務排程
       - 提醒通知
       - 數據同步
    """)