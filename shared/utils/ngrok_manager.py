import os
import sys
import platform
import requests
import zipfile
import subprocess
import json
import time
import logging
from pathlib import Path
from shared.config.config import Config
from pyngrok import ngrok

logger = logging.getLogger(__name__)

class NgrokManager:
    def __init__(self, auth_token: str = None):
        self.auth_token = auth_token
        self._tunnel = None
        
    def start(self, port: int = 5000) -> str:
        """啟動 ngrok 服務"""
        try:
            if self.auth_token:
                ngrok.set_auth_token(self.auth_token)
            
            self._tunnel = ngrok.connect(port)
            return self._tunnel.public_url
        except Exception as e:
            logger.error(f"Ngrok 啟動失敗: {str(e)}")
            return None
    
    def stop(self):
        """停止 ngrok 服務"""
        try:
            if self._tunnel:
                ngrok.disconnect(self._tunnel.public_url)
                self._tunnel = None
        except Exception as e:
            logger.error(f"Ngrok 停止失敗: {str(e)}")
    
    def is_running(self) -> bool:
        """檢查 ngrok 是否正在運行"""
        return self._tunnel is not None
    
    def get_url(self) -> str:
        """獲取 ngrok 網址"""
        return self._tunnel.public_url if self._tunnel else None

    def _get_ngrok_path(self):
        """獲取 ngrok 執行檔路徑"""
        system = platform.system().lower()
        if system == "windows":
            return os.path.join(self.base_dir, "ngrok.exe")
        return os.path.join(self.base_dir, "ngrok")
    
    def _download_ngrok(self):
        """下載 ngrok"""
        try:
            system = platform.system().lower()
            arch = platform.machine().lower()
            
            # 確定下載 URL
            if system == "windows":
                url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
            elif system == "darwin":
                url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip"
            else:
                url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip"
            
            # 下載檔案
            response = requests.get(url)
            zip_path = os.path.join(self.base_dir, "ngrok.zip")
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # 解壓縮
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.base_dir)
            
            # 設置執行權限
            if system != "windows":
                os.chmod(self.ngrok_path, 0o755)
            
            # 清理
            os.remove(zip_path)
            return True
            
        except Exception as e:
            logger.error(f"下載 ngrok 失敗: {str(e)}")
            return False

    def _create_config(self):
        """創建 ngrok 配置文件"""
        if not self.config.NGROK_AUTH_TOKEN:
            raise ValueError("未設定 NGROK_AUTH_TOKEN，請在 .env 文件中設定")
        
        config = {
            "version": "2",
            "authtoken": self.config.NGROK_AUTH_TOKEN,
            "region": self.config.NGROK_REGION,
            "web_addr": "localhost:4040",
            "tunnels": {
                "line-bot": {
                    "proto": "http",
                    "addr": 5000
                }
            }
        }
        
        import yaml
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def ensure_ngrok(self):
        """確保 ngrok 可用"""
        if not os.path.exists(self.ngrok_path):
            if not self._download_ngrok():
                raise RuntimeError("無法下載 ngrok")
        
        self._create_config()
    
    def start(self):
        """啟動 ngrok"""
        try:
            self.ensure_ngrok()
            
            # 檢查端口是否被占用
            def is_port_in_use(port):
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    return s.connect_ex(('localhost', port)) == 0
            
            if is_port_in_use(4040):
                logger.warning("端口 4040 已被占用，嘗試終止舊進程...")
                self.stop()
                time.sleep(2)
            
            # 停止可能已經運行的 ngrok
            self.stop()
            
            # 啟動 ngrok
            logger.info("正在啟動 ngrok 服務...")
            startupinfo = None
            if platform.system().lower() == "windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.process = subprocess.Popen(
                [self.ngrok_path, "start", "--config", self.config_path, "--all"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                encoding='utf-8'  # 使用 UTF-8 編碼
            )
            
            # 檢查啟動是否有錯誤
            time.sleep(1)
            if self.process.poll() is not None:
                _, stderr = self.process.communicate()
                raise RuntimeError(f"ngrok 啟動失敗: {stderr}")
            
            # 等待服務啟動
            logger.info("等待 ngrok 服務就緒...")
            time.sleep(5)
            
            # 重試獲取 URL
            max_retries = 5
            for i in range(max_retries):
                try:
                    url = self.get_public_url()
                    if url:
                        logger.info(f"ngrok 服務已就緒: {url}")
                        return url
                    
                    logger.warning(f"第 {i+1} 次嘗試: 未獲取到 URL")
                    time.sleep(2)
                except Exception as e:
                    logger.warning(f"第 {i+1} 次嘗試失敗: {str(e)}")
                    if i < max_retries - 1:
                        time.sleep(2)
                        continue
            
            raise RuntimeError("無法獲取 ngrok URL")
            
        except Exception as e:
            logger.error(f"啟動 ngrok 失敗: {str(e)}")
            self.stop()  # 清理失敗的進程
            raise
    
    def stop(self):
        """停止 ngrok"""
        try:
            if self.process:
                logger.info("正在停止 ngrok 進程...")
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
            
            # 確保進程被終止
            if platform.system().lower() == "windows":
                logger.info("正在檢查並終止所有 ngrok 進程...")
                subprocess.run(
                    ["taskkill", "/F", "/IM", "ngrok.exe"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False
                )
            else:
                subprocess.run(
                    ["pkill", "ngrok"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False
                )
            
            time.sleep(1)  # 等待進程完全終止
            
        except Exception as e:
            logger.warning(f"停止 ngrok 時發生錯誤: {str(e)}")
    
    def get_public_url(self):
        """獲取當前的公開 URL"""
        try:
            response = requests.get("http://localhost:4040/api/tunnels")
            tunnels = response.json()["tunnels"]
            for tunnel in tunnels:
                if tunnel["proto"] == "https":
                    return tunnel["public_url"]
        except:
            return None 