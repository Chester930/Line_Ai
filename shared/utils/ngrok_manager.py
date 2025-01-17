import subprocess
import time
import re
import sys
import platform
import requests
from urllib.parse import urlparse
import os
import json
from datetime import datetime

class NgrokManager:
    def __init__(self):
        self.process = None
        self.url = None
        self.start_time = None
        self.session_info = {}

    def clear_screen(self):
        """清除終端機畫面"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')

    def print_banner(self, message=""):
        """顯示格式化的橫幅"""
        width = 70
        print(f"\n{'='*width}")
        if message:
            padding = (width - len(message)) // 2
            print(f"{'='*padding} {message} {'='*padding}")
            print(f"{'='*width}")

    def save_session_info(self):
        """保存會話資訊"""
        if self.url and self.start_time:
            self.session_info = {
                'url': self.url,
                'start_time': self.start_time.isoformat(),
                'webhook_url': f"{self.url}/webhook",
                'web_interface': "http://127.0.0.1:4040"
            }
            
            # 確保目錄存在
            os.makedirs('logs', exist_ok=True)
            
            # 保存到文件
            with open('logs/ngrok_session.json', 'w', encoding='utf-8') as f:
                json.dump(self.session_info, f, ensure_ascii=False, indent=2)

    def wait_for_ngrok_api(self, max_retries=10):
        """等待 ngrok API 可用"""
        for i in range(max_retries):
            try:
                response = requests.get("http://127.0.0.1:4040/api/tunnels")
                if response.status_code == 200:
                    return True
            except requests.exceptions.ConnectionError:
                print(f"等待 ngrok 啟動中... ({i+1}/{max_retries})")
                time.sleep(2)
        return False

    def start_ngrok(self):
        """啟動 ngrok 並獲取 URL"""
        try:
            self.clear_screen()
            self.print_banner("初始化 Ngrok 服務")
            self.start_time = datetime.now()
            
            # 根據作業系統選擇適當的命令
            if platform.system() == 'Windows':
                command = 'ngrok http 5000 --authtoken 2rNrVgzjMv8cUIdN8zt40oYOvaU_7Yt4PMwkVChscQL5Y26Ef'
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                self.process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    startupinfo=startupinfo
                )
            else:
                command = ['ngrok', 'http', '5000', '--authtoken', '2rNrVgzjMv8cUIdN8zt40oYOvaU_7Yt4PMwkVChscQL5Y26Ef']
                self.process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

            print("\n正在啟動 ngrok 服務...")
            
            if not self.wait_for_ngrok_api():
                print("\n❌ ngrok API 啟動超時")
                self.stop_ngrok()
                return None
            
            response = requests.get("http://127.0.0.1:4040/api/tunnels")
            tunnels = response.json()['tunnels']
            
            if tunnels:
                self.url = tunnels[0]['public_url']
                if not self.url.startswith('https'):
                    parsed = urlparse(self.url)
                    self.url = f'https://{parsed.netloc}'
                
                # 保存會話資訊
                self.save_session_info()
                
                self.clear_screen()
                self.print_banner("Ngrok 服務啟動成功")
                print(f"\n🔗 Webhook URL:")
                print(f"   {self.url}/webhook")
                print(f"\n🌐 Web 管理介面:")
                print(f"   http://127.0.0.1:4040")
                print(f"\n📝 操作說明:")
                print(f"   1. 複製上方的 Webhook URL")
                print(f"   2. 將 URL 設定到 LINE Developers Console")
                print(f"   3. 在 LINE Bot 中測試連線狀態")
                print(f"\n⏱️ 啟動時間: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"📋 會話資訊已保存至: logs/ngrok_session.json")
                self.print_banner()
                print("\n💡 按 Ctrl+C 可以停止服務...\n")
                return self.url
            else:
                print("\n❌ 無法獲取 ngrok URL")
                return None

        except Exception as e:
            print(f"\n❌ 啟動 ngrok 時發生錯誤: {str(e)}")
            self.stop_ngrok()
            return None

    def stop_ngrok(self):
        """停止 ngrok 進程"""
        if self.process:
            self.process.terminate()
            self.process = None
            self.url = None
            if self.start_time:
                duration = datetime.now() - self.start_time
                print(f"\n⏱️ 服務運行時間: {duration}")
            print("\n✅ Ngrok 服務已停止")

if __name__ == "__main__":
    manager = NgrokManager()
    try:
        url = manager.start_ngrok()
        if url:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        manager.stop_ngrok() 