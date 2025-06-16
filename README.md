# 🤖 AutoGen 語音助手

結合 OpenAI、Google Cloud Speech-to-Text 和 AutoGen 三重 Agent 協作的個人化 AI 語音轉文字助手

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

## ✨ 功能特色

- 🎤 **語音轉文字**：使用 Google Cloud Speech-to-Text API 進行高精度語音識別
- 🤖 **AutoGen 三重 Agent 協作**：
  - Agent 1: 語音處理專家（修正語音辨識錯誤）
  - Agent 2: 內容優化專家（優化文字表達和結構）
  - Agent 3: 繁體中文轉換專家（確保 100% 繁體中文輸出）
- 📝 **智能文字優化**：自動優化語法、用詞和表達方式
- 🇹🇼 **繁體中文輸出**：確保台灣用戶友好的文字格式
- 📊 **用戶學習記錄**：追蹤和儲存用戶互動統計
- ⚡ **即時處理**：快速回應用戶語音訊息

## 📁 專案結構

```
AutoGen/
├── src/                             # 核心模組目錄
│   ├── audio.py                     # 音頻處理模組
│   ├── speech.py                    # 語音轉文字模組
│   ├── models.py                    # AutoGen 模型處理器
│   └── storage.py                   # 用戶資料儲存模組
├── files/                           # 臨時檔案目錄
├── tinydb/                          # 資料庫目錄
├── main.py                          # 主程式
├── requirements.txt                 # 依賴套件清單
├── config.env                       # 環境配置檔案
└── README.md                        # 專案說明
```

## 🔧 專案詳情

- 使用虛擬環境進行開發
- 使用的 API：
  - OpenAI GPT-4o API
  - Google Cloud Speech-to-Text API
  - LINE Developer Messaging API
- 部署平台：
  - Railway 平台
- 資料儲存：使用 TinyDB 進行本地資料儲存

## 🚀 安裝

要安裝並運行此專案，請按照以下步驟：

1. 複製專案：
```bash
git clone https://github.com/GuanRuLai/AI-Message-Assistant.git
```

2. 進入專案目錄：
```bash
cd AI-Message-Assistant
```

3. 安裝必要的依賴套件：
```bash
pip install -r requirements.txt
```

4. 設定環境變數：
複製 `env.example` 為 `config.env` 並填入您的 API 金鑰

## 📱 使用方法

要啟動 AutoGen 語音助手，執行以下指令：

```bash
python main.py
```

### 🎤 LINE Bot 使用說明

1. 將 LINE Bot 加為好友
2. 發送語音訊息給 Bot
3. Bot 會自動處理並回覆優化後的繁體中文文字
4. 支援文字訊息優化功能
5. 輸入「幫助」查看使用說明
6. 輸入「狀態」查看使用統計

### 📊 回應格式

```
✨ 語音轉文字完成

🎯 原始文字：
[原始語音辨識結果]

📝 AI 優化結果：
[AutoGen 三重 Agent 優化後的繁體中文]
```

## 🏗️ 系統架構

```
用戶語音訊息 
    ↓
LINE Webhook 接收
    ↓
音頻下載處理 (AudioProcessor)
    ↓
Google Cloud Speech-to-Text 語音轉文字 (SpeechProcessor)
    ↓
AutoGen 三重 Agent 協作處理 (AutoGenProcessor)
    ↓
用戶資料儲存 (UserStorage)
    ↓
回傳優化繁體中文
```

## 🔑 環境需求

- Python 3.8+
- OpenAI API Key
- LINE Bot Channel (Channel Secret & Access Token)
- Google Cloud Platform 帳戶和 Speech-to-Text API 啟用
- Google Cloud 服務帳戶金鑰 (JSON 格式)

## 📝 授權

本專案採用 MIT 授權 - 詳見 LICENSE 檔案

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