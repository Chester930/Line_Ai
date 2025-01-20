import os
import sys
import platform
import requests
import subprocess
import json
import time
import logging
from pathlib import Path
from shared.config.config import Config

logger = logging.getLogger(__name__)

class NgrokManager:
    def __init__(self):
        self.config = Config()
        self.base_dir = self.config.DATA_DIR
        self.ngrok_path = self._get_ngrok_path()
        self.config_path = os.path.join(self.base_dir, "ngrok.yml")
        self.process = None
        
    def _get_ngrok_path(self):
        """獲取 ngrok 執行檔路徑"""
        system = platform.system().lower()
        if system == "windows":
            return "ngrok.exe"  # 假設 ngrok 已在系統 PATH 中
        return "ngrok"
    
    def get_webhook_url(self) -> str:
        """獲取當前的 webhook URL"""
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=1)  # 添加 timeout
            tunnels = response.json()["tunnels"]
            if tunnels:
                for tunnel in tunnels:
                    if tunnel["proto"] == "https":
                        return tunnel["public_url"]
            return None
        except Exception as e:
            # 改為 debug 級別的日誌，因為這是預期中可能發生的情況
            logger.debug(f"獲取 webhook URL 失敗: {str(e)}")
            return None

    def start(self):
        """啟動 ngrok"""
        try:
            # 檢查是否已經運行
            try:
                url = self.get_webhook_url()
                if url:
                    logger.info(f"ngrok 已經在運行: {url}")
                    return url
            except:
                pass

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
                startupinfo=startupinfo
            )
            
            # 等待服務啟動
            time.sleep(3)
            
            # 獲取 URL
            url = self.get_webhook_url()
            if url:
                logger.info(f"ngrok 服務已就緒: {url}")
                return url
            
            raise RuntimeError("無法獲取 ngrok URL")
            
        except Exception as e:
            logger.error(f"啟動 ngrok 失敗: {str(e)}")
            self.stop()
            raise

    def stop(self):
        """停止 ngrok"""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
            
            # 確保進程被終止
            if platform.system().lower() == "windows":
                subprocess.run(["taskkill", "/F", "/IM", "ngrok.exe"], 
                             capture_output=True, check=False)
            else:
                subprocess.run(["pkill", "ngrok"], 
                             capture_output=True, check=False)
                
        except Exception as e:
            logger.warning(f"停止 ngrok 時發生錯誤: {str(e)}") 