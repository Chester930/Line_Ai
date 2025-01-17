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

logger = logging.getLogger(__name__)

class NgrokManager:
    def __init__(self):
        self.base_dir = Config.DATA_DIR
        self.ngrok_path = self._get_ngrok_path()
        self.config_path = os.path.join(self.base_dir, "ngrok.yml")
        
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
        config = {
            "version": "2",
            "authtoken": Config.NGROK_AUTH_TOKEN,
            "tunnels": {
                "line-bot": {
                    "proto": "http",
                    "addr": "5000"
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
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
            
            # 啟動 ngrok
            process = subprocess.Popen(
                [self.ngrok_path, "start", "--config", self.config_path, "line-bot"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

            # 等待隧道建立
            time.sleep(3)
            
            # 獲取公開 URL
            try:
                response = requests.get("http://localhost:4040/api/tunnels")
                tunnels = response.json()["tunnels"]
                for tunnel in tunnels:
                    if tunnel["proto"] == "https":
                        return tunnel["public_url"]
            except:
                pass
            
            raise RuntimeError("無法獲取 ngrok URL")

        except Exception as e:
            logger.error(f"啟動 ngrok 失敗: {str(e)}")
            raise
    
    def stop(self):
        """停止 ngrok"""
        try:
            subprocess.run(["taskkill", "/F", "/IM", "ngrok.exe"], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
        except:
            pass 