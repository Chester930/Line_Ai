from typing import Dict, Any
import streamlit as st
from shared.utils.plugin_manager import PluginManager
from shared.plugins.web_search import WebSearchPlugin
from shared.plugins.youtube_subtitle import YouTubeSubtitlePlugin
from shared.config.config import Config
from shared.plugins.web_browser import WebBrowserPlugin
import logging

logger = logging.getLogger(__name__)

def show_page():
    """顯示插件管理頁面"""
    st.title("插件管理")
    
    try:
        # 初始化插件管理器和配置
        plugin_manager = PluginManager()
        config = Config()
        
        # 註冊插件
        web_search_plugin = WebSearchPlugin()
        web_browser_plugin = WebBrowserPlugin()
        youtube_plugin = YouTubeSubtitlePlugin()
        
        plugin_manager.register_plugin(web_search_plugin)
        plugin_manager.register_plugin(web_browser_plugin)
        plugin_manager.register_plugin(youtube_plugin)
        
        # 添加標籤頁
        tab1, tab2, tab3 = st.tabs([
            "網頁搜尋插件", 
            "網頁瀏覽插件",
            "YouTube 字幕插件"
        ])
        
        with tab1:
            show_web_search_settings(plugin_manager, config)
        
        with tab2:
            show_web_browser_settings(plugin_manager, config)
            
        with tab3:
            show_youtube_subtitle_settings(plugin_manager, config)
            
    except Exception as e:
        logger.error(f"載入插件管理頁面失敗: {e}")
        st.error(f"載入插件管理頁面時發生錯誤: {str(e)}")

def show_web_search_settings(plugin_manager: PluginManager, config: Config):
    """顯示網路搜尋插件設定"""
    st.markdown("""
    ### 網路搜尋插件 (Web Search Plugin)
    
    允許 AI 助手在回答問題時搜尋並參考網路上的最新資訊。支援以下搜尋引擎：
    
    1. **Google Custom Search**
       - 需要 API Key 和 Search Engine ID (CX)
       - 提供最準確的搜尋結果
       - [申請教學](https://developers.google.com/custom-search/v1/introduction)
    
    2. **Bing Web Search**
       - 需要 API Key
       - 提供豐富的搜尋結果
       - [申請教學](https://www.microsoft.com/bing/apis/pricing)
    
    3. **DuckDuckGo**
       - 免費，無需 API Key
       - 注重隱私的搜尋引擎
       - 搜尋結果可能較少
    """)
    
    # API 金鑰設定
    with st.form("api_key_settings"):
        st.subheader("API 金鑰設定")
        
        # Google Search API 設定
        st.markdown("#### Google Custom Search API")
        google_api_key = st.text_input(
            "API Key",
            value=config.get("GOOGLE_SEARCH_API_KEY", ""),
            type="password",
            key="google_search_api_key",
            help="從 Google Cloud Console 獲取的 API Key"
        )
        google_cx = st.text_input(
            "Search Engine ID (CX)",
            value=config.get("GOOGLE_SEARCH_CX", ""),
            type="password",
            key="google_search_cx",
            help="從 Google Custom Search Console 獲取的搜尋引擎 ID"
        )
        
        # Bing Search API 設定
        st.markdown("#### Bing Web Search API")
        bing_api_key = st.text_input(
            "API Key",
            value=config.get("BING_SEARCH_API_KEY", ""),
            type="password",
            key="bing_search_api_key",
            help="從 Microsoft Azure Portal 獲取的 API Key"
        )
        
        if st.form_submit_button("保存 API 設定"):
            try:
                config.update({
                    "GOOGLE_SEARCH_API_KEY": google_api_key,
                    "GOOGLE_SEARCH_CX": google_cx,
                    "BING_SEARCH_API_KEY": bing_api_key
                })
                st.success("✅ API 設定已更新")
                # 重新載入插件的 API 金鑰
                if plugin_manager.get_plugin("web_search"):
                    plugin_manager.get_plugin("web_search")._load_api_keys()
            except Exception as e:
                logger.error(f"更新 API 設定失敗: {e}")
                st.error(f"❌ 更新失敗：{str(e)}")
    
    # 插件功能設定
    with st.form("web_search_settings"):
        st.subheader("功能設定")
        
        plugin = plugin_manager.get_plugin("web_search")
        plugin_config = plugin.config if plugin else {}
        
        enabled = st.toggle(
            "啟用插件",
            value=plugin_config.get("enabled", False),
            help="啟用後，AI 助手將可以使用網路搜尋功能"
        )
        
        if enabled:
            col1, col2 = st.columns(2)
            with col1:
                search_engine = st.selectbox(
                    "搜尋引擎",
                    ["Google", "Bing", "DuckDuckGo"],
                    index=["Google", "Bing", "DuckDuckGo"].index(
                        plugin_config.get("engine", "Google")
                    ),
                    help="選擇要使用的搜尋引擎，DuckDuckGo 無需 API Key"
                )
                max_results = st.number_input(
                    "最大搜尋結果數",
                    min_value=1,
                    max_value=10,
                    value=plugin_config.get("max_results", 3),
                    help="每次搜尋返回的最大結果數量"
                )
            with col2:
                weight = st.slider(
                    "搜尋結果權重",
                    min_value=0.0,
                    max_value=1.0,
                    value=plugin_config.get("weight", 0.3),
                    help="搜尋結果在 AI 回答中的參考權重"
                )
                timeout = st.number_input(
                    "搜尋超時 (秒)",
                    min_value=1,
                    max_value=30,
                    value=plugin_config.get("timeout", 10),
                    help="搜尋請求的最大等待時間"
                )
        
        if st.form_submit_button("保存功能設定"):
            try:
                new_config = {
                    "enabled": enabled,
                    "engine": search_engine if enabled else "Google",
                    "max_results": max_results if enabled else 3,
                    "weight": weight if enabled else 0.3,
                    "timeout": timeout if enabled else 10
                }
                if plugin_manager.update_plugin_config("web_search", new_config):
                    st.success("✅ 功能設定已更新")
                else:
                    st.error("❌ 更新失敗：插件未正確載入")
            except Exception as e:
                logger.error(f"更新設定失敗: {e}")
                st.error(f"❌ 更新失敗：{str(e)}")

def show_youtube_subtitle_settings(plugin_manager: PluginManager, config: Config):
    """顯示 YouTube 字幕插件設定"""
    st.markdown("""
    ### YouTube 字幕插件 (YouTube Subtitle Plugin)
    
    從 YouTube 影片中提取字幕，支援多語言字幕和自動分段處理。主要功能：
    
    1. **多語言字幕支援**
       - 可設定優先語言順序
       - 支援自動生成的字幕
       - 智能語言回退機制
    
    2. **字幕處理功能**
       - 自動分段處理
       - 智能合併相關內容
       - 過濾無效內容
    """)
    
    # 插件功能設定
    with st.form("youtube_subtitle_settings"):
        st.subheader("功能設定")
        
        plugin = plugin_manager.get_plugin("youtube_subtitle")
        plugin_config = plugin.config if plugin else {}
        
        enabled = st.toggle(
            "啟用插件",
            value=plugin_config.get("enabled", False),
            help="啟用後，AI 助手將可以處理 YouTube 影片字幕"
        )
        
        if enabled:
            col1, col2 = st.columns(2)
            with col1:
                preferred_languages = st.multiselect(
                    "字幕語言優先順序",
                    options=["zh-TW", "zh-CN", "en", "ja", "ko"],
                    default=plugin_config.get("preferred_languages", ["zh-TW", "zh-CN", "en"]),
                    help="設定字幕語言的優先順序，將按順序嘗試獲取"
                )
                chunk_size = st.number_input(
                    "字幕分段大小 (字元數)",
                    min_value=100,
                    max_value=1000,
                    value=plugin_config.get("chunk_size", 500),
                    help="單個字幕片段的最大字元數"
                )
            with col2:
                include_auto_subtitles = st.checkbox(
                    "包含自動生成的字幕",
                    value=plugin_config.get("include_auto_subtitles", False),
                    help="是否使用 YouTube 自動生成的字幕（可能不太準確）"
                )
                max_results = st.number_input(
                    "最大處理數量",
                    min_value=1,
                    max_value=50,
                    value=plugin_config.get("max_results", 10),
                    help="單次處理的最大字幕片段數量"
                )
        
        if st.form_submit_button("保存功能設定"):
            try:
                new_config = {
                    "enabled": enabled,
                    "preferred_languages": preferred_languages if enabled else ["zh-TW", "zh-CN", "en"],
                    "chunk_size": chunk_size if enabled else 500,
                    "include_auto_subtitles": include_auto_subtitles if enabled else False,
                    "max_results": max_results if enabled else 10
                }
                if plugin_manager.update_plugin_config("youtube_subtitle", new_config):
                    st.success("✅ 功能設定已更新")
                else:
                    st.error("❌ 更新失敗：插件未正確載入")
            except Exception as e:
                logger.error(f"更新設定失敗: {e}")
                st.error(f"❌ 更新失敗：{str(e)}")

def show_web_browser_settings(plugin_manager: PluginManager, config: Config):
    """顯示網頁瀏覽插件設置"""
    st.subheader("網頁瀏覽插件設置")
    
    # 插件說明
    st.markdown("""
    此插件可以訪問和解析網頁內容，主要功能：
    - 提取網頁的標題和主要文本內容
    - 清理 JavaScript 和樣式代碼
    - 提取重要鏈接
    - 支持內容長度限制
    """)
    
    plugin = plugin_manager.get_plugin("web_browser")
    plugin_config = plugin.config if plugin else {}
    
    with st.form("web_browser_settings"):
        enabled = st.toggle(
            "啟用插件",
            value=plugin_config.get("enabled", True),
            help="啟用後，AI 助手將可以瀏覽網頁內容"
        )
        
        if enabled:
            timeout = st.number_input(
                "請求超時時間（秒）", 
                min_value=1, 
                max_value=60, 
                value=plugin_config.get("timeout", 10),
                help="訪問網頁時的最大等待時間"
            )
            
            max_content = st.number_input(
                "最大內容長度（字符）",
                min_value=1000,
                max_value=100000,
                value=plugin_config.get("max_content_length", 50000),
                step=1000,
                help="提取的網頁內容最大字符數"
            )
        
        if st.form_submit_button("保存設置"):
            try:
                new_config = {
                    "enabled": enabled,
                    "timeout": timeout if enabled else 10,
                    "max_content_length": max_content if enabled else 50000
                }
                if plugin_manager.update_plugin_config("web_browser", new_config):
                    st.success("✅ 設置已保存")
                else:
                    st.error("❌ 更新失敗：插件未正確載入")
            except Exception as e:
                logger.error(f"保存設置失敗: {e}")
                st.error(f"保存設置失敗: {str(e)}") 