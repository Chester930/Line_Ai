import streamlit as st
import sys
import os

# 將專案根目錄加入到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config.config import Config
from shared.utils.ngrok_manager import NgrokManager
from shared.utils.settings_manager import SettingsManager

def show_api_keys_settings(settings_manager):
    st.header("API Keys 設定")
    with st.form("api_keys_form"):
        line_channel_secret = st.text_input(
            "LINE Channel Secret",
            value=settings_manager.get_api_key("line_channel_secret"),
            type="password"
        )
        line_channel_access_token = st.text_input(
            "LINE Channel Access Token",
            value=settings_manager.get_api_key("line_channel_access_token"),
            type="password"
        )
        ngrok_auth_token = st.text_input(
            "Ngrok Auth Token",
            value=settings_manager.get_api_key("ngrok_auth_token"),
            type="password"
        )
        
        if st.form_submit_button("保存"):
            success = settings_manager.update_api_keys(
                line_channel_secret=line_channel_secret,
                line_channel_access_token=line_channel_access_token,
                ngrok_auth_token=ngrok_auth_token
            )
            
            if success:
                st.success("設定已保存")
                if not settings_manager.is_initialized():
                    settings_manager.mark_initialized()
            else:
                st.error("保存失敗")

def main():
    st.title("Line AI Assistant 管理介面")
    
    settings_manager = SettingsManager()
    
    # 側邊欄
    st.sidebar.title("功能選單")
    menu = st.sidebar.selectbox(
        "選擇功能",
        ["系統狀態", "API Keys 設定", "角色管理", "文件管理", "專案控制"]
    )
    
    if menu == "系統狀態":
        st.header("系統狀態")
        st.write("目前版本：1.0.0")
        if settings_manager.is_initialized():
            st.success("系統已初始化")
        else:
            st.warning("系統尚未初始化，請先設定 API Keys")
        
    elif menu == "API Keys 設定":
        show_api_keys_settings(settings_manager)
    
    elif menu == "角色管理":
        st.header("角色管理")
        st.info("角色管理功能開發中...")
    
    elif menu == "文件管理":
        st.header("文件管理")
        st.info("文件管理功能開發中...")
    
    elif menu == "專案控制":
        st.header("專案控制")
        if not settings_manager.is_initialized():
            st.warning("請先完成系統初始化設定")
            return
            
        if st.button("啟動 LINE Bot"):
            try:
                ngrok = NgrokManager()
                webhook_url = ngrok.start()
                st.success(f"LINE Bot 已啟動\nWebhook URL: {webhook_url}")
            except Exception as e:
                st.error(f"啟動失敗：{str(e)}")

if __name__ == "__main__":
    main() 