import streamlit as st
from shared.config.config import Config
from shared.utils.plugin_manager import PluginManager

def show_page():
    """顯示插件功能管理頁面"""
    st.header("插件功能列表 (Plugin Features)")
    
    plugin_manager = PluginManager()
    config = Config()
    
    # 網路搜尋插件設定
    with st.expander("🔍 網路搜尋 (Web Search)", expanded=True):
        st.markdown("""
        ### 網路搜尋插件 (Web Search Plugin)
        
        允許 AI 助手在回答問題時搜尋並參考網路上的最新資訊。
        """)
        
        with st.form("web_search_settings"):
            enabled = st.toggle(
                "啟用網路搜尋",
                value=config.get("web_search.enabled", False)
            )
            
            if enabled:
                col1, col2 = st.columns(2)
                with col1:
                    max_results = st.number_input(
                        "最大搜尋結果數",
                        min_value=1,
                        max_value=10,
                        value=config.get("web_search.max_results", 3)
                    )
                with col2:
                    search_weight = st.slider(
                        "搜尋結果權重",
                        min_value=0.0,
                        max_value=1.0,
                        value=config.get("web_search.weight", 0.3)
                    )
                
                search_engine = st.selectbox(
                    "搜尋引擎",
                    options=["Google", "Bing", "DuckDuckGo"],
                    index=0
                )
            
            if st.form_submit_button("保存設定"):
                try:
                    config.update({
                        "web_search.enabled": enabled,
                        "web_search.max_results": max_results if enabled else 3,
                        "web_search.weight": search_weight if enabled else 0.3,
                        "web_search.engine": search_engine
                    })
                    st.success("✅ 設定已更新")
                except Exception as e:
                    st.error(f"❌ 保存失敗：{str(e)}")
    
    # 知識庫插件設定
    with st.expander("📚 知識庫 (Knowledge Base)", expanded=True):
        st.markdown("""
        ### 知識庫插件 (Knowledge Base Plugin)
        
        讓 AI 助手能夠存取和使用自定義的知識庫資源。
        """)
        
        with st.form("kb_settings"):
            enabled = st.toggle(
                "啟用知識庫",
                value=config.get("knowledge_base.enabled", False)
            )
            
            if enabled:
                col1, col2 = st.columns(2)
                with col1:
                    chunk_size = st.number_input(
                        "文件分段大小",
                        min_value=100,
                        max_value=1000,
                        value=config.get("knowledge_base.chunk_size", 500)
                    )
                with col2:
                    kb_weight = st.slider(
                        "知識庫權重",
                        min_value=0.0,
                        max_value=1.0,
                        value=config.get("knowledge_base.weight", 0.5)
                    )
            
            if st.form_submit_button("保存設定"):
                try:
                    config.update({
                        "knowledge_base.enabled": enabled,
                        "knowledge_base.chunk_size": chunk_size if enabled else 500,
                        "knowledge_base.weight": kb_weight if enabled else 0.5
                    })
                    st.success("✅ 設定已更新")
                except Exception as e:
                    st.error(f"❌ 保存失敗：{str(e)}")
    
    # 即將推出的插件
    with st.expander("🔜 即將推出 (Coming Soon)", expanded=True):
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