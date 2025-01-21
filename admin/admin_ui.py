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
    page_title="Line AI Assistant Admin",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 使用更完整的 CSS 隱藏所有不需要的元素
st.markdown("""
    <style>
        /* 隱藏漢堡選單 */
        #MainMenu {visibility: hidden;}
        
        /* 隱藏頁尾 */
        footer {visibility: hidden;}
        
        /* 隱藏部署按鈕 */
        .stDeployButton {display:none;}
        
        /* 隱藏導航列表 */
        .css-1d391kg {display: none;}  /* 導航容器 */
        section[data-testid="stSidebar"] > div.css-1d391kg {display: none;}
        .css-1rs6os {display: none;}   /* 導航項目 */
        .css-17lntkn {display: none;}  /* 導航文字 */
        
        /* 隱藏其他可能的選單元素 */
        .css-ch5dnh {display: none;}
        .css-cio0dv {display: none;}
        .css-1dp5vir {display: none;}
        
        /* 修正側邊欄樣式 */
        .css-1544g2n {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

def main():
    """主程式入口"""
    # 顯示頁面頭部
    show_header()
    
    # 顯示側邊欄並獲取選單選項
    menu = show_sidebar()
    
    # 頁面路由（添加對話測試功能）
    pages = {
        "系統狀態": system_status.show_page,
        "AI 模型設定": model_settings.show_page,
        "LINE 官方帳號": line_management.show_page,
        "對話測試": chat_test.show_page  # 新增對話測試路由
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