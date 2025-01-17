# Line AI Assistant Builder

一個幫助使用者建立和管理自己的 Line AI 官方帳號的跨平台應用程式。

## 功能特點
- 視覺化界面建立 Line AI Bot
- 知識庫管理與配置
- 即時對話測試
- 數據分析與報表
- 跨平台支援 (Desktop & Mobile)

## 開發環境需求
- Python 3.8+
- Node.js 14+
- Flutter 2.0+

## 安裝說明

### 1. 建立虛擬環境

```bash
python -m venv venv
```

### 2. 啟動虛擬環境

```bash
.\venv\Scripts\activate
```

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```


# 安裝所需套件


### 3. 環境設定
在專案根目錄建立 `.env` 文件，並填入以下設定：


# LINE Bot Settings

LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token

LINE_CHANNEL_SECRET=your_line_channel_secret


# Google API Settings

GOOGLE_API_KEY=your_google_api_key


# Ngrok Settings

NGROK_AUTH_TOKEN=your_ngrok_auth_token


## 啟動說明

### 1. 測試配置

# 測試環境變數是否正確載入

python -m shared.config.config


### 2. 啟動服務器

# 啟動 webhook 服務器

python -m shared.line_sdk.server



### 3. 使用 ngrok 進行測試



# 在新的終端機視窗中運行

ngrok http 5000


## 測試步驟

1. **確認服務器運行**
   - 檢查終端機輸出是否顯示 `Uvicorn running on http://0.0.0.0:5000`
   - 確認沒有錯誤訊息

2. **確認 ngrok 連接**
   - 複製 ngrok 提供的 HTTPS URL
   - 在 LINE Developers Console 中設定 Webhook URL
   - Webhook URL 格式：`https://your-ngrok-url/webhook`

3. **測試 LINE Bot**
   - 掃描 LINE Bot 的 QR Code
   - 發送測試訊息
   - 確認是否收到回應

## 常見問題排解

1. **找不到模組**
   ```bash
   pip install [missing_module_name]
   ```

2. **環境變數未載入**
   - 確認 `.env` 文件位置正確
   - 確認環境變數格式正確
   - 使用 `Config.print_config()` 檢查配置

3. **服務器啟動失敗**
   - 確認端口 5000 未被占用
   - 確認虛擬環境已啟動
   - 檢查錯誤日誌

## 開發文檔
[待補充]

## 貢獻指南
[待補充]

## 授權資訊
[待補充]