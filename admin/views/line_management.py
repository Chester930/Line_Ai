import streamlit as st
from shared.utils.ngrok_manager import NgrokManager
from shared.config.config import Config
import requests
import json
import time
import logging

logger = logging.getLogger(__name__)

def init_session_state():
    """初始化 session state"""
    if 'line_settings_tab' not in st.session_state:
        st.session_state.line_settings_tab = 'api'
    if 'show_api_settings' not in st.session_state:
        st.session_state.show_api_settings = True
    if 'show_webhook_settings' not in st.session_state:
        st.session_state.show_webhook_settings = True
    if 'show_friend_info' not in st.session_state:
        st.session_state.show_friend_info = True

def test_webhook_url(url: str) -> bool:
    """測試 Webhook URL 是否可訪問"""
    try:
        response = requests.get(url)
        return response.status_code == 200
    except:
        return False

def show_page():
    """顯示 LINE 官方帳號管理頁面"""
    st.title("LINE 官方帳號管理")
    
    # 初始化 session state
    init_session_state()
    
    # 使用 tabs 而不是 expander
    tab1, tab2, tab3 = st.tabs(["API 設定", "Webhook 設定", "加入好友資訊"])
    
    # 從配置文件加載當前設定
    config = Config()
    
    # API 設定標籤頁
    with tab1:
        st.markdown("""
        ### LINE 官方帳號設定步驟
        1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
        2. 建立或選擇一個 Provider
        3. 建立一個 Messaging API Channel
        4. 在 Basic Settings 中可以找到：
           - Channel Secret (頻道密鑰)
        5. 在 Messaging API 設定中可以找到：
           - Channel Access Token (頻道存取權杖)
           - Bot Basic ID (機器人 ID)
        """)
        
        current_settings = {
            'LINE_CHANNEL_SECRET': config.LINE_CHANNEL_SECRET,
            'LINE_CHANNEL_ACCESS_TOKEN': config.LINE_CHANNEL_ACCESS_TOKEN,
            'LINE_BOT_ID': config.LINE_BOT_ID
        }
        
        with st.form("line_settings", clear_on_submit=False):
            channel_secret = st.text_input(
                "Channel Secret",
                value=current_settings['LINE_CHANNEL_SECRET'],
                type="password"
            )
            channel_token = st.text_input(
                "Channel Access Token",
                value=current_settings['LINE_CHANNEL_ACCESS_TOKEN'],
                type="password"
            )
            bot_id = st.text_input(
                "Bot ID",
                value=current_settings['LINE_BOT_ID']
            )
            
            if st.form_submit_button("保存設定"):
                try:
                    update_env_file({
                        'LINE_CHANNEL_SECRET': channel_secret,
                        'LINE_CHANNEL_ACCESS_TOKEN': channel_token,
                        'LINE_BOT_ID': bot_id
                    })
                    st.success("設定已更新，請重新啟動服務以套用更改")
                except Exception as e:
                    logger.error(f"保存設定失敗: {str(e)}")
                    st.error(f"保存設定失敗：{str(e)}")
    
    # Webhook 設定標籤頁
    with tab2:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            ### Webhook 設定說明
            1. 確保 LINE Bot 服務正在運行：
               ```bash
               python run.py --mode bot
               ```
            2. 複製下方的 Webhook URL
            3. 前往 LINE Developers Console
            4. 在 Messaging API 設定中：
               - 貼上 Webhook URL
               - 開啟「Use webhook」選項
               - 點擊「Verify」按鈕測試連接
            """)
        
        with col2:
            st.markdown("### 服務狀態")
            if check_line_bot_service():
                st.success("✅ 服務運行中")
            else:
                st.error("❌ 服務未運行")
        
        # 顯示當前 Webhook URL
        st.subheader("當前 Webhook URL")
        webhook_url = get_webhook_url()
        if webhook_url:
            webhook_full_url = f"{webhook_url}/callback"
            st.code(webhook_full_url, language=None)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("複製 URL"):
                    st.write("URL 已複製到剪貼簿")
                    st.markdown(f"""
                    <script>
                        navigator.clipboard.writeText('{webhook_full_url}');
                    </script>
                    """, unsafe_allow_html=True)
            with col2:
                st.info("👆 請複製此 URL 到 LINE Developers Console 的 Webhook URL 欄位")
        else:
            st.warning("⚠️ 無法獲取 Webhook URL")
    
    # 加入好友資訊標籤頁
    with tab3:
        if config.LINE_BOT_ID:
            st.markdown(f"""
            ### 加入好友方式
            1. 掃描 QR Code：
               - 使用 LINE 掃描這個連結：
                 [QR Code](https://line.me/R/ti/p/@{config.LINE_BOT_ID})
            2. 搜尋 Bot ID：
               - 在 LINE 搜尋欄位輸入：@{config.LINE_BOT_ID}
            3. 點擊好友連結：
               - [https://line.me/R/ti/p/@{config.LINE_BOT_ID}](https://line.me/R/ti/p/@{config.LINE_BOT_ID})
            """)
        else:
            st.warning("請先在 API 設定中設定 Bot ID")

def check_line_bot_service():
    """檢查 LINE Bot 服務狀態"""
    max_retries = 3
    timeout = 3  # 增加超時時間到 3 秒
    
    for i in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:5000/status", timeout=timeout)
            if response.status_code == 200:
                return True
            time.sleep(1)
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                time.sleep(1)
                continue
    return False

def get_webhook_url():
    """獲取 Webhook URL"""
    ngrok = NgrokManager()
    return ngrok.get_public_url()

def show_channel_settings(config: Config):
    """顯示 Channel 設定"""
    with st.form("line_channel_form"):
        channel_secret = st.text_input(
            "Channel Secret",
            value=config.LINE_CHANNEL_SECRET or "",
            type="password"
        )
        
        channel_token = st.text_input(
            "Channel Access Token",
            value=config.LINE_CHANNEL_ACCESS_TOKEN or "",
            type="password"
        )
        
        if st.form_submit_button("儲存設定"):
            try:
                # TODO: 實現設定儲存邏輯
                st.success("Channel 設定已更新")
            except Exception as e:
                st.error(f"更新失敗: {str(e)}")

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
                st.success(f"Webhook 已啟動: {url}")
                st.rerun()
            except Exception as e:
                st.error(f"啟動失敗: {str(e)}")
    
    with col2:
        if st.button("停止 Webhook"):
            try:
                ngrok_manager.stop()
                st.success("Webhook 已停止")
                st.rerun()
            except Exception as e:
                st.error(f"停止失敗: {str(e)}")
    
    # Webhook 測試
    if st.button("測試 Webhook"):
        with st.spinner("測試中..."):
            result = test_webhook(current_url)
            if result['success']:
                st.success("Webhook 測試成功")
            else:
                st.error(f"測試失敗: {result['error']}")

def show_account_info(config: Config):
    """顯示官方帳號資訊"""
    if not config.LINE_CHANNEL_ACCESS_TOKEN:
        st.warning("請先設定 Channel Access Token")
        return
    
    try:
        # TODO: 實現獲取官方帳號資訊的邏輯
        info = {
            "名稱": "AI Assistant",
            "好友數": 100,
            "狀態": "正常",
            "方案": "Developer Trial"
        }
        
        for key, value in info.items():
            st.write(f"- {key}: {value}")
            
    except Exception as e:
        st.error(f"獲取資訊失敗: {str(e)}")

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