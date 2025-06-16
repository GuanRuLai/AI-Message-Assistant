# 🤖 AutoGen 0.4 語音助手

一個整合 AutoGen 0.4、LINE Bot SDK v3 和 Google Cloud Speech-to-Text 的智能語音助手。

## 📋 目錄

- [介紹](#介紹)
- [功能特色](#功能特色)
- [專案結構](#專案結構)
- [專案詳情](#專案詳情)
- [安裝](#安裝)
- [使用方法](#使用方法)
- [授權](#授權)
- [致謝](#致謝)

## 介紹

AutoGen 語音助手是一個個人化的 AI 語音轉文字助手，整合了 OpenAI、Google Cloud Speech-to-Text 和 AutoGen 三重 Agent 協作系統。本專案旨在透過 LINE Bot 提供互動式且高效的語音轉文字服務，並使用多重 AI Agent 來優化文字品質，確保輸出繁體中文結果。

## ✨ 主要功能

- 🎤 **語音轉文字**：使用 Google Cloud Speech-to-Text API
- 🤖 **AutoGen 0.4 協作**：多 Agent 智能對話系統
- 💬 **LINE Bot 整合**：支援最新 LINE Bot SDK v3
- 🗣️ **繁體中文支援**：專為繁體中文優化
- 📊 **用戶記錄**：TinyDB 本地資料儲存

## 🚀 本地開發設定

### 1. 環境需求

- Python 3.9+
- LINE Developer Account
- Google Cloud Platform Account
- OpenAI API Key
- ngrok (用於本地測試)

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 環境變數設定

複製 `env.example` 為 `config.env` 並填入您的 API 金鑰：

```bash
cp env.example config.env
```

編輯 `config.env`：

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# LINE Bot
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token

# Google Cloud (JSON 格式)
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}
```

### 4. 使用 ngrok 進行本地測試

1. **安裝 ngrok**：
   ```bash
   # 下載並安裝 ngrok
   # https://ngrok.com/download
   ```

2. **啟動應用程式**：
   ```bash
   python main.py
   ```

3. **在另一個終端啟動 ngrok**：
   ```bash
   ngrok http 5000
   ```

4. **設定 LINE Webhook**：
   - 複製 ngrok 提供的 HTTPS URL (例如：`https://abc123.ngrok.io`)
   - 在 LINE Developer Console 設定 Webhook URL：`https://abc123.ngrok.io/webhook`

### 5. 測試功能

- 📱 **健康檢查**：`https://your-ngrok-url.ngrok.io/health`
- 🔍 **環境變數檢查**：`https://your-ngrok-url.ngrok.io/env-check`
- 🏠 **首頁**：`https://your-ngrok-url.ngrok.io/`

## 📁 專案結構

```
AutoGen/
├── main.py                 # 主程式
├── config.env             # 環境變數配置
├── requirements.txt       # Python 依賴
├── src/
│   ├── audio.py          # 音訊處理
│   ├── speech.py         # 語音轉文字
│   ├── models.py         # AutoGen 處理
│   └── storage.py        # 資料儲存
├── files/                # 臨時檔案目錄
└── tinydb/              # 資料庫檔案
```

## 🔧 技術架構

- **LINE Bot SDK v3.17.1**：最新 LINE Bot 開發框架
- **AutoGen 0.4**：微軟最新 Agent 協作框架
- **Google Cloud Speech-to-Text**：語音識別服務
- **OpenAI GPT-4**：自然語言處理
- **Flask**：Web 框架
- **TinyDB**：輕量級資料庫

## 📝 使用說明

1. **語音訊息**：發送語音訊息給 LINE Bot，系統會自動轉換為文字並進行 AI 處理
2. **文字訊息**：直接發送文字訊息進行 AI 對話
3. **指令**：
   - `help` 或 `幫助`：顯示使用說明
   - `status` 或 `狀態`：顯示系統狀態

## 🐛 除錯

如果遇到問題，請檢查：

1. **環境變數**：訪問 `/env-check` 端點檢查設定
2. **日誌輸出**：查看終端的詳細日誌
3. **ngrok 連線**：確保 ngrok 正常運行
4. **LINE Webhook**：確認 Webhook URL 設定正確

## 📄 授權

MIT License

## 🔑 環境需求

- Python 3.8+
- OpenAI API Key
- LINE Bot Channel (Channel Secret & Access Token)
- Google Cloud Platform 帳戶和 Speech-to-Text API 啟用
- Google Cloud 服務帳戶金鑰 (JSON 格式)

## 🙏 致謝

感謝 [AI-English-Tutor-Linebot](https://github.com/GuanRuLai/AI-English-Tutor-Linebot) 專案提供的靈感和寶貴的參考資源。

## 📞 關於

🤖 結合 OpenAI、Google Cloud Speech-to-Text 和 AutoGen 三重 Agent 協作的個人化 AI 語音轉文字助手

### 🌟 資源

- 📖 Readme
- 📄 MIT license

### 📈 活動

⭐ **0** stars  
👀 **1** watching  
🍴 **0** forks

### 💻 語言

- Python 100.0% 