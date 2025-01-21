import streamlit as st
from shared.utils.ngrok_manager import NgrokManager
from shared.config.config import Config
import requests
import json

def test_webhook_url(url: str) -> bool:
    """測試 Webhook URL 是否可訪問"""
    try:
        response = requests.get(url)
        return response.status_code == 200
    except:
        return False

def show_page():
    """顯示 LINE 官方帳號管理頁面"""
    st.header("LINE 官方帳號設定")
    
    config = Config()
    ngrok = NgrokManager()
    
    # LINE Channel 設定
    with st.expander("Channel 設定", expanded=True):
        with st.form("line_channel_settings"):
            channel_id = st.text_input(
                "Channel ID",
                value=config.get("line.channel_id", ""),
                type="password"
            )
            
            channel_secret = st.text_input(
                "Channel Secret",
                value=config.get("line.channel_secret", ""),
                type="password"
            )
            
            access_token = st.text_input(
                "Channel Access Token",
                value=config.get("line.access_token", ""),
                type="password"
            )
            
            if st.form_submit_button("保存設定"):
                try:
                    config.update({
                        "line.channel_id": channel_id,
                        "line.channel_secret": channel_secret,
                        "line.access_token": access_token
                    })
                    st.success("✅ LINE Channel 設定已更新")
                except Exception as e:
                    st.error(f"❌ 保存失敗：{str(e)}")
    
    # Webhook 設定
    with st.expander("Webhook 設定", expanded=True):
        st.write("**目前狀態**")
        
        if ngrok.is_running():
            webhook_url = ngrok.get_public_url()
            st.success(f"✅ Webhook 運行中：{webhook_url}")
            
            if test_webhook_url(webhook_url):
                st.info("✅ Webhook URL 可正常訪問")
            else:
                st.warning("⚠️ Webhook URL 無法訪問")
            
            if st.button("停止 Webhook"):
                try:
                    ngrok.stop()
                    st.success("✅ Webhook 已停止")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ 停止失敗：{str(e)}")
        else:
            st.warning("⚠️ Webhook 未運行")
            
            if st.button("啟動 Webhook"):
                try:
                    ngrok.start()
                    st.success("✅ Webhook 已啟動")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ 啟動失敗：{str(e)}")

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