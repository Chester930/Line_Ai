# Line AI Assistant

一個基於 LINE 的 AI 助手系統。

## 功能特點

- 多角色對話系統
- 文件知識庫
- 管理員介面
- Studio 測試環境

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
- AI API Keys
- Ngrok Auth Token

### 4. 初始化系統

```bash
# 執行初始化腳本
python scripts/setup.py
```

## 運行方式

系統提供三種運行模式，可根據需求選擇：

### 1. 管理員介面（推薦）
```bash
python run.py --mode admin
```
- 主要功能：
  - 系統設定和管理
  - LINE Bot 的啟動/停止控制
  - 角色管理和測試
  - AI 模型設定
- 特點：
  - 整合了所有核心功能
  - 可直接控制 LINE Bot
  - 提供基本的測試功能
- 適合：日常使用和管理

### 2. LINE Bot 獨立模式
```bash
python run.py --mode app
```
- 主要功能：
  - 純粹運行 LINE Bot 服務
- 特點：
  - 僅啟動必要服務
  - 資源佔用較少
  - 適合純後台運行
- 適合：正式部署環境

### 3. Studio 開發環境
```bash
streamlit run studio/studio_ui.py
```
- 主要功能：
  - 專注於開發和測試
  - 詳細的參數調整
  - 完整的測試功能
- 特點：
  - 提供更多開發工具
  - 可導出測試記錄
  - 即時調整和測試
- 適合：開發和調試階段

使用建議：
- 一般使用者：使用管理員介面即可滿足大部分需求
- 伺服器部署：使用 app 模式執行
- 開發人員：使用 Studio 進行開發和測試

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