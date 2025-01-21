import streamlit as st
import logging
from shared.database.database import init_db

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 確保資料庫初始化
logger.info("正在檢查並初始化資料庫...")
init_db()

# 必須是第一個 Streamlit 命令，在其他任何導入之前
st.set_page_config(
    page_title="AI 助理管理介面",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 其他導入放在 set_page_config 之後
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

# 添加自定義 CSS
st.markdown("""
    <style>
    /* 側邊欄樣式 */
    .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* 隱藏 Streamlit 默認的導航欄和英文列表 */
    [data-testid="stSidebarNav"] {display: none !important;}
    .css-163ttbj {display: none !important;}
    .css-1d391kg {display: none !important;}
    
    /* 標題樣式 */
    .stTitle {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    /* 分隔線樣式 */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 側邊欄容器樣式 */
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