import streamlit as st
from shared.utils.ngrok_manager import NgrokManager
from shared.config.config import Config
import requests

def show_page():
    """LINE 官方帳號管理頁面"""
    st.header("LINE 官方帳號管理")
    
    config = Config()
    ngrok_manager = NgrokManager()
    
    # LINE Channel 設定
    with st.expander("Channel 設定", expanded=True):
        show_channel_settings(config)
    
    # Webhook 設定
    with st.expander("Webhook 設定", expanded=True):
        show_webhook_settings(config, ngrok_manager)
    
    # 官方帳號資訊
    with st.expander("加入好友資訊", expanded=True):
        show_account_info(config)

def show_channel_settings(config: Config):
    """顯示 Channel 設定"""
    with st.form("line_channel_form"):
        channel_secret = st.text_input(
            "Channel Secret",
            value=config.LINE_CHANNEL_SECRET or "",
            type="password",
            help="從 LINE Developers Console 獲取"
        )
        
        channel_token = st.text_input(
            "Channel Access Token",
            value=config.LINE_CHANNEL_ACCESS_TOKEN or "",
            type="password",
            help="從 LINE Developers Console 獲取"
        )
        
        bot_id = st.text_input(
            "Bot Basic ID",
            value=config.LINE_BOT_ID or "",
            help="機器人的基本 ID"
        )
        
        if st.form_submit_button("儲存設定"):
            try:
                config.update_settings({
                    'LINE_CHANNEL_SECRET': channel_secret,
                    'LINE_CHANNEL_ACCESS_TOKEN': channel_token,
                    'LINE_BOT_ID': bot_id
                })
                st.success("✅ Channel 設定已更新")
            except Exception as e:
                st.error(f"❌ 更新失敗: {str(e)}")

def show_webhook_settings(config: Config, ngrok_manager: NgrokManager):
    """顯示 Webhook 設定"""
    # Webhook URL 顯示
    current_url = ngrok_manager.get_webhook_url()
    st.write("目前的 Webhook URL:")
    st.code(current_url or "未啟動")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("啟動 Webhook"):
            try:
                url = ngrok_manager.start()
                st.success(f"✅ Webhook 已啟動: {url}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 啟動失敗: {str(e)}")
    
    with col2:
        if st.button("停止 Webhook"):
            try:
                ngrok_manager.stop()
                st.success("✅ Webhook 已停止")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 停止失敗: {str(e)}")
    
    # Webhook 測試
    if st.button("測試 Webhook"):
        with st.spinner("測試中..."):
            result = test_webhook(current_url)
            if result['success']:
                st.success("✅ Webhook 測試成功")
            else:
                st.error(f"❌ 測試失敗: {result['error']}")

def show_account_info(config: Config):
    """顯示官方帳號資訊"""
    if not config.LINE_BOT_ID:
        st.warning("⚠️ 請先設定 Bot Basic ID")
        return
    
    st.markdown(f"""
    ### 加入好友方式 (Ways to Add Friend)
    1. 掃描 QR Code：
       - 使用 LINE 掃描這個連結：[QR Code](https://line.me/R/ti/p/@{config.LINE_BOT_ID})
    
    2. 搜尋 Bot ID：
       - 在 LINE 搜尋欄位輸入：@{config.LINE_BOT_ID}
    
    3. 點擊好友連結：
       - [https://line.me/R/ti/p/@{config.LINE_BOT_ID}](https://line.me/R/ti/p/@{config.LINE_BOT_ID})
    """)

def test_webhook(url: str) -> dict:
    """測試 Webhook 連接"""
    if not url:
        return {
            'success': False,
            'error': '未設定 Webhook URL'
        }
    
    try:
        response = requests.post(
            url,
            json={"type": "test"},
            timeout=5
        )
        return {
            'success': response.status_code == 200,
            'error': None if response.status_code == 200 else f"HTTP {response.status_code}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }