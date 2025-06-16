# 🤖 LINE Bot 語音轉文字助手

智能語音轉文字 LINE Bot，整合 AutoGen 三重 Agent 協作，提供優化的繁體中文輸出。

## ✨ 功能特色

- 🎤 **語音訊息接收**：支援 LINE 語音訊息輸入
- 🧠 **AutoGen 三重 Agent 協作**：
  - Agent 1: 語音處理專家 (修正語音辨識錯誤)
  - Agent 2: 內容優化專家 (優化文字表達)
  - Agent 3: 繁體轉換專家 (確保 100% 繁體中文輸出)
- 📝 **智能文字優化**：自動優化語法、用詞和表達
- 🇹🇼 **繁體中文輸出**：確保台灣用戶友好的文字格式
- ⚡ **即時處理**：快速回應用戶語音訊息

## 🏗️ 系統架構

```
用戶語音訊息 
    ↓
LINE Webhook 接收
    ↓
下載語音檔案
    ↓
Google Cloud Speech-to-Text 語音轉文字
    ↓
AutoGen 三重 Agent 協作處理
    ↓
回傳優化繁體中文
```

## 📋 環境需求

- Python 3.8+
- OpenAI API Key
- LINE Bot Channel (Channel Secret & Access Token)
- Google Cloud Platform 帳戶和 Speech-to-Text API 啟用
- Google Cloud 服務帳戶金鑰 (JSON 格式)

## 🚀 快速開始

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

編輯 `config.env` 檔案：

```env
# OpenAI API 設定
OPENAI_API_KEY=your_openai_api_key

# LINE Bot 設定  
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token

# 伺服器設定
PORT=8000
WEBHOOK_URL=https://your-domain.com/webhook
```

### 3. 啟動服務

```bash
# 使用快速啟動腳本
python start_line_bot.py

# 或直接啟動
python line_bot_app.py
```

### 4. 設定 LINE Webhook

在 LINE Developers Console 中設定 Webhook URL：
```
https://your-domain.com/webhook
```

## 📁 專案結構

```
AutoGen/
├── agents/                          # AutoGen 語音處理模組
│   ├── autogen_voice_processor.py   # 三重 Agent 協作處理器
│   └── google_stt_processor.py      # Google Cloud Speech-to-Text 處理器
├── config.env                       # 環境配置檔案
├── line_bot_app.py                  # LINE Bot 主程式
├── start_line_bot.py                # 快速啟動腳本
├── requirements.txt                 # 依賴套件清單
└── README.md                        # 專案說明
```

## 🔧 API 端點

- `POST /webhook` - LINE Bot Webhook 接收端點
- `GET /health` - 服務健康檢查
- `GET /` - 服務狀態頁面

## 💬 使用方式

1. 將 LINE Bot 加為好友
2. 發送語音訊息給 Bot
3. Bot 會自動處理並回覆優化後的繁體中文文字

### 回應格式

```
✨ 語音轉文字完成

🎯 原始文字：
[原始語音辨識結果]

📝 AI 優化結果：
[AutoGen 三重 Agent 優化後的繁體中文]
```

## 🔮 未來規劃

- [x] 整合 Google Cloud Speech-to-Text API
- [ ] 支援多種語言輸入
- [ ] 增加語音訊息長度支援
- [ ] 添加使用者偏好設定
- [ ] 整合更多 AI 功能

## 🛠️ 技術堆疊

- **Web 框架**: Flask
- **LINE Bot SDK**: line-bot-sdk v3
- **AI 協作**: AutoGen
- **語音轉文字**: Google Cloud Speech-to-Text
- **語言模型**: OpenAI GPT-4o
- **日誌系統**: Loguru
- **簡繁轉換**: OpenCC (備用)

## 📝 設定說明

### LINE Bot 設定

1. 前往 [LINE Developers](https://developers.line.biz/)
2. 建立 Provider 和 Messaging API Channel
3. 取得 Channel Secret 和 Channel Access Token
4. 設定 Webhook URL

### AutoGen 設定

AutoGen 三重 Agent 協作流程：

1. **Speech Agent**: 修正語音辨識錯誤
2. **Optimization Agent**: 優化文字表達和結構  
3. **Traditional Chinese Agent**: 強制轉換為繁體中文

## 🔒 安全注意事項

- 不要將 API Key 提交到版本控制
- 使用 HTTPS 進行 Webhook 通訊
- 定期更新依賴套件
- 實施適當的錯誤處理和日誌記錄

## 🆘 故障排除

### 常見問題

1. **Webhook 驗證失敗**
   - 檢查 Channel Secret 是否正確
   - 確認 Webhook URL 可以被 LINE 訪問

2. **語音處理失敗**
   - 檢查 OpenAI API Key 額度
   - 確認語音檔案格式支援

3. **模組導入錯誤**
   - 執行 `pip install -r requirements.txt`
   - 檢查 Python 版本是否符合需求

### 日誌查看

服務運行時會產生詳細的日誌，可用於除錯：

```python
# 查看即時日誌
tail -f logs/line_bot.log
```

## 📞 支援

如有問題或建議，請聯絡開發團隊。

---

**© 2024 AutoGen LINE Bot 語音助手** # AI-Message-Assistant
