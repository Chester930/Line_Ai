# Line AI Assistant

一個基於 LINE Bot 的 AI 助手系統，支援多角色對話和文件知識庫。

## 功能特點

- 多角色 AI 對話系統
- 文件知識庫管理
- 網頁管理介面
- LINE Bot 整合
- 自動化通知系統

## 系統需求

- Python 3.8+
- PostgreSQL
- ngrok

## 安裝步驟

1. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

2. 設定環境變數或建立 .env 檔案：
```env
# LINE Bot Settings
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token

# Database Settings
DATABASE_URL=postgresql://username:password@localhost:5432/line_ai_db

# Ngrok Settings
NGROK_AUTH_TOKEN=your_ngrok_token
```

3. 建立資料庫：
```sql
CREATE DATABASE line_ai_db;
```

## 使用方式

### 首次使用

1. 執行專案：
```bash
python run.py
```
- 系統會自動進入管理員介面
- 完成必要的初始設定：
  - 設定 API Keys
  - 導入或設定 AI 角色
  - 上傳知識庫文件
  - 進行測試對話

### 日常使用

1. 啟動系統：
```bash
python run.py
```

2. 管理員操作：
- 在管理員介面中可以：
  - 啟動/停止 LINE Bot
  - 管理 AI 角色設定
  - 管理文件知識庫
  - 查看系統狀態
  - 測試 AI 回應

### 注意事項

1. 系統運行狀態：
- LINE Bot 運行時無法進行設定修改
- 需要修改設定時，請先停止 LINE Bot

2. 文件管理：
- 支援的文件格式：PDF, DOCX, XLSX, TXT
- 上傳文件會自動建立知識庫索引

3. 角色管理：
- 可以導入預設角色
- 可以自訂角色設定和提示詞
- 每個角色可以設定獨立的參數

## 專案結構

```
Line_Ai/
├── admin/              # 管理員介面
├── shared/             # 共用元件
│   ├── config/        # 設定檔
│   ├── database/      # 資料庫模組
│   ├── line_sdk/      # LINE Bot SDK
│   └── utils/         # 工具函數
├── ui/                # 使用者介面
├── data/              # 資料存儲
├── uploads/           # 上傳文件
└── logs/              # 日誌文件
```

## 開發指南

### 添加新角色

1. 在 `shared/config/default_roles.json` 中定義角色：
```json
{
    "role_id": {
        "name": "角色名稱",
        "description": "角色描述",
        "prompt": "角色提示詞",
        "settings": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1000,
            "web_search": true
        }
    }
}
```

### 自訂通知

1. 在管理員介面中設定：
- 每日通知
- 每週通知
- 特定日期通知

## 故障排除

1. LINE Bot 無法啟動：
- 檢查 API Keys 設定
- 確認 ngrok 是否正常運行
- 查看日誌文件

2. 資料庫連接問題：
- 確認資料庫服務是否運行
- 檢查連接字串設定
- 確認資料庫用戶權限

## 貢獻指南

1. Fork 專案
2. 創建特性分支
3. 提交變更
4. 發送 Pull Request

## 授權

本專案採用 MIT 授權條款