# Line AI Assistant

一個基於 LINE 的 AI 助手系統。

## 功能特點

- 多角色對話系統
- 文件知識庫
- 管理員介面
- Studio 測試環境
- 多模型支援 (Gemini、GPT、Claude)
- 多媒體處理 (文件、圖片、音訊)

## 安裝步驟

### 1. 建立虛擬環境

Windows:
```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
venv\Scripts\activate

# 確認 Python 版本
python --version  # 應為 3.8 以上
```

Linux/Mac:
```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate

# 確認 Python 版本
python --version  # 應為 3.8 以上
```

### 2. 安裝依賴

```bash
# 更新 pip
python -m pip install --upgrade pip

# 安裝依賴套件
pip install -r requirements.txt
```

### 3. 環境設定

1. 複製環境變數範本：
```bash
cp .env.example .env
```

2. 編輯 `.env` 文件，填入必要的設定：
- LINE Channel 設定
  - LINE_CHANNEL_SECRET
  - LINE_CHANNEL_ACCESS_TOKEN
- AI API Keys
  - GOOGLE_API_KEY (Gemini)
  - OPENAI_API_KEY (GPT)
  - ANTHROPIC_API_KEY (Claude)
- Ngrok Auth Token

### 4. 初始化系統

```bash
# 執行初始化腳本
python scripts/setup.py
```

## 運行方式

系統提供三種運行模式，需要使用兩個終端機視窗來運行：

### 終端機視窗 1 - LINE Bot 服務
```bash
# 啟動虛擬環境
venv\Scripts\activate

# 啟動 LINE Bot 服務
python run.py --mode bot

# 成功啟動後會顯示：
# 啟動 LINE Bot 服務...
# === LINE Bot Webhook URL ===
# https://xxxx-xxx-xxx-xxx-xxx.ngrok.io/webhook
#  * Running on http://127.0.0.1:5000
```

### 終端機視窗 2 - 管理介面
```bash
# 啟動虛擬環境
venv\Scripts\activate

# 啟動管理介面
python run.py --mode admin

# 成功啟動後會顯示：
# 啟動管理員介面...
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

### 運行模式說明

1. LINE Bot 服務 (`--mode bot`)
   - 啟動 Flask 伺服器
   - 自動開啟 ngrok 服務
   - 生成 Webhook URL
   - 處理 LINE 訊息

2. 管理員介面 (`--mode admin`)
   - 系統設定和管理
   - 查看 Webhook URL
   - 角色和提示詞管理
   - 對話測試功能

3. Studio 開發環境 (`--mode studio`)
   - 開發和測試工具
   - 詳細的參數調整
   - 測試記錄功能

使用建議：
- 本地開發：同時運行 bot 和 admin 模式
- 正式部署：使用 PM2 或 Supervisor 管理 bot 服務
- 開發測試：使用 studio 模式進行功能測試

## 開發指南

### 角色管理
- 使用管理員介面創建和管理角色
- 可設定角色的提示詞和參數
- 支援匯入預設角色

### 文件管理
- 支援上傳 PDF、Word、Excel 等格式
- 自動提取文件內容
- 建立知識庫索引

### 對話測試
- 使用 Studio 進行即時對話測試
- 可調整模型參數
- 支援對話記錄匯出

## 注意事項

1. 環境要求：
- Python 3.8 或以上
- 足夠的記憶體（建議 4GB 以上）
- 穩定的網路連接

2. 安全性：
- 請妥善保管 API Keys
- 定期更新 LINE Channel Token
- 不要將 .env 文件上傳到版本控制系統

3. 使用建議：
- 首次使用請完整執行初始化流程
- 定期備份對話和設定資料
- 在虛擬環境中運行專案

## 支援的檔案格式

- 文件：
  - 純文本 (.txt)
  - PDF (.pdf)
  - Word (.doc, .docx)
  - Excel (.xls, .xlsx)
- 圖片：
  - PNG (.png)
  - JPEG (.jpg, .jpeg)
- 音訊：
  - MP3 (.mp3)
  - WAV (.wav)

## AI 模型設定

支援的模型：
1. Google Gemini
   - gemini-pro：文字處理
   - gemini-pro-vision：圖像分析
2. OpenAI GPT
   - gpt-4-turbo-preview
   - gpt-4
   - gpt-3.5-turbo
3. Anthropic Claude
   - claude-3-opus-20240229
   - claude-3-sonnet-20240229
   - claude-3-haiku-20240229

## 常見問題

1. 檔案上傳失敗
   - 檢查檔案格式是否支援
   - 檢查檔案大小限制

2. API 連接錯誤
   - 確認 API Key 正確性
   - 檢查網路連接
   - 確認 API 額度

3. 模型切換問題
   - 確認已在 .env 中設置對應的 API Key
   - 檢查模型是否在已啟用列表中

## LINE Bot 設定說明

### 1. 終端機1啟動 LINE Bot 服務
```bash
# 啟動虛擬環境
venv\Scripts\activate
# 啟動 LINE Bot 服務
python run.py --mode bot
```

### 2. 終端機2開啟管理介面
```bash
# 啟動虛擬環境
venv\Scripts\activate
# 開啟管理介面
python run.py --mode admin
```

### 2. LINE Developers 設定
1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 建立或選擇一個 Provider
3. 建立一個 Messaging API Channel
4. 在 Basic Settings 中可以找到：
   - Channel Secret (頻道密鑰)
5. 在 Messaging API 設定中可以找到：
   - Channel Access Token (頻道存取權杖)
   - Bot Basic ID (機器人 ID)

### 3. Webhook 設定步驟
1. 啟動 LINE Bot 服務後，會自動開啟 ngrok 並產生 Webhook URL
2. 在管理介面的「LINE 官方帳號管理」中可以看到當前的 Webhook URL
3. 將此 URL 設定到 LINE Developers Console：
   - 進入你的 Channel
   - 選擇 Messaging API 設定
   - 將 Webhook URL 貼到「Webhook URL」欄位
   - 開啟「Use webhook」選項
   - 點擊「Verify」按鈕測試連接

注意事項：
- 每次重新啟動 LINE Bot 服務，ngrok 都會產生新的 URL
- 需要重新設定 LINE Developers Console 的 Webhook URL
- 建議在正式環境使用固定網域，避免頻繁更換 URL

### 4. 本地開發設定
1. 安裝 ngrok
2. 在 .env 中設定 NGROK_AUTH_TOKEN
3. LINE Bot 服務會自動管理 ngrok 的啟動和關閉
4. 管理介面會顯示當前的 Webhook URL 和服務狀態

### 5. 正式環境部署
建議使用：
- 固定網域
- SSL 憑證
- 反向代理（如 Nginx）
- PM2 或 Supervisor 管理程序
- 反向代理（如 Nginx）
- PM2 或 Supervisor 管理程序