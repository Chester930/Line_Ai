import streamlit as st
from admin.components.header import show_header
from admin.components.footer import show_footer
from admin.components.sidebar import show_sidebar
from admin.views import (
    system_status,
    model_settings,
    line_management,
    chat_test,
    prompts_management,
    role_management,
    plugin_management,
    knowledge_base
)

# 設定頁面配置（必須在最開始）
st.set_page_config(
    page_title="Line AI Assistant - 管理介面",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義 CSS - 特別處理導航欄
st.markdown("""
    <style>
        /* 隱藏所有自動產生的元素 */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 隱藏 Streamlit 默認的導航欄 */
        [data-testid="stSidebarNav"] {display: none !important;}
        .css-1d391kg {display: none !important;}
        .css-163ttbj {display: none !important;}
        
        /* 側邊欄樣式 */
        section[data-testid="stSidebar"] {
            background-color: rgb(14, 17, 23);
            width: 250px !important;
            min-width: 250px !important;
        }
        
        /* 確保側邊欄內容在最上層 */
        section[data-testid="stSidebar"] > div {
            height: 100vh;
            z-index: 999999 !important;
            background-color: rgb(14, 17, 23);
        }
        
        /* 調整內容區域 */
        .block-container {
            padding-top: 1rem;
            max-width: none;
        }
        
        /* 美化 radio 按鈕 */
        .stRadio > label {
            display: none;
        }
        
        .stRadio > div {
            padding: 0.5rem;
            border-radius: 4px;
        }
        
        .stRadio > div:hover {
            background-color: rgba(151, 166, 195, 0.15);
        }
    </style>
""", unsafe_allow_html=True)

def main():
    """主程式入口"""
    # 顯示頁面頭部
    show_header()
    
    # 顯示側邊欄並獲取選單選項
    menu = show_sidebar()
    
    # 頁面路由
    pages = {
        "系統狀態": system_status.show_page,
        "AI 模型設定": model_settings.show_page,
        "LINE 官方帳號": line_management.show_page,
        "對話測試": chat_test.show_page,
        "共用 Prompts": prompts_management.show_page,
        "角色管理": role_management.show_page,
        "插件功能": plugin_management.show_page,
        "知識庫管理": knowledge_base.show_page
    }
    
    # 顯示對應頁面
    if menu in pages:
        pages[menu]()
    else:
        st.info("此功能正在維護中...")
    
    # 顯示頁面底部
    show_footer()

if __name__ == "__main__":
    main() 