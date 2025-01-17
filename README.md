# Line AI Assistant

一個基於 LINE 的 AI 助手系統。

## 功能特點

- 多角色對話系統
- 文件知識庫
- 管理員介面
- Studio 測試環境

## 安裝步驟

1. 安裝依賴：
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# 或
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

2. 設置環境變數：
- 複製 `.env.example` 到 `.env`
- 填入必要的配置信息

3. 初始化系統：
```bash
python scripts/setup.py
```

## 運行方式

1. 啟動管理員介面：
```bash
python run.py --mode admin
```

2. 啟動 LINE Bot：
```bash
python run.py --mode app
```

3. 啟動 Studio：
```bash
streamlit run studio/studio_ui.py
```

## 開發指南

- 角色管理：使用管理員介面創建和管理角色
- 文件管理：上傳和管理知識庫文件
- 對話測試：使用 Studio 進行對話測試和參數調整

## 注意事項

- 請確保 .env 中的所有配置都已正確設置
- 首次運行時需要完成初始化設置
- 建議在虛擬環境中運行專案