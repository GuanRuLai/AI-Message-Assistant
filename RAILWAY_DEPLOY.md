# 🚀 Railway 部署指南

## 📋 部署前準備

### 1. 推送代碼到 GitHub
```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### 2. 準備所需的 API Keys 和認證

## 🔑 需要在 Railway 設定的環境變數

登入 [Railway](https://railway.app) 並連接您的 GitHub 倉庫後，在 **Variables** 頁面設定以下環境變數：

### 🤖 基本設定
```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# AutoGen 設定
AUTOGEN_MODEL=gpt-4o
AUTOGEN_TEMPERATURE=0.7
```

### 🎤 Google Cloud Speech-to-Text
```env
# 語言和模型設定
GOOGLE_STT_LANGUAGE=cmn-Hant-TW
GOOGLE_STT_MODEL=default

# 🔐 重要：Google Cloud 認證 JSON（將整個 JSON 內容貼上）
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account","project_id":"ai-message-assistant-463106","private_key_id":"208dc2c8b7c6...","private_key":"-----BEGIN PRIVATE KEY-----\n...完整的JSON內容...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
```

### 🤖 LINE Bot 設定
```env
# LINE Bot Channel 資訊
LINE_CHANNEL_SECRET=d34ac45af4bc54cb954ecb39785f6b6e
LINE_CHANNEL_ACCESS_TOKEN=Izvua7TB8Y9GQ+joPnvnhdTRgMFaOs88DfPLVtfyhuZnsVXofu89o3u0tA0RSjflARPvHkoYWTjMNfYuFp4aDHcRlyVajz+f8Xx5l9kz2MVxM2rSpqE8YanfrYyb1L+jf6bz6zdIteCq/f+XHYAeHgdB04t89/1O/w1cDnyilFU=
```

### 📊 其他設定
```env
# 文字處理設定
ENABLE_TEXT_OPTIMIZATION=true
MAX_OPTIMIZATION_ROUNDS=4

# 系統設定
LOG_LEVEL=INFO
MONITOR_INTERVAL=1
PROCESSING_DELAY=2
MAX_RETRIES=3

# 語音設定
VOICE_SAMPLE_RATE=16000
VOICE_CHUNK_SIZE=480
VOICE_VAD_MODE=1
VOICE_SILENCE_THRESHOLD=2.0
VOICE_MIN_SPEECH_DURATION=1.0

# 臨時檔案目錄
TEMP_AUDIO_DIR=temp_audio
```

## 🛠️ credential.json 處理方式

**重要**：Railway 不支援上傳檔案，所以我們使用環境變數來傳遞 Google Cloud 認證。

### 步驟 1: 開啟您的 credential JSON 檔案
```bash
# 檢視您的認證檔案內容
cat ai-message-assistant-463106-208dc2c8b7c6.json
```

### 步驟 2: 複製完整的 JSON 內容
將整個 JSON 檔案的內容（包括大括號）複製到 `GOOGLE_APPLICATION_CREDENTIALS_JSON` 環境變數中。

### 範例格式：
```json
{
  "type": "service_account",
  "project_id": "ai-message-assistant-463106",
  "private_key_id": "208dc2c8b7c6...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...完整的私鑰...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## 🚀 部署步驟

### 1. 在 Railway 建立新專案
- 前往 [Railway](https://railway.app)
- 點擊 "New Project"
- 選擇 "Deploy from GitHub repo"
- 選擇您的 `AI-Message-Assistant` 倉庫

### 2. 設定環境變數
- 在專案頁面點擊 "Variables" 標籤
- 逐一加入上述所有環境變數

### 3. 等待部署完成
- Railway 會自動偵測 Python 專案
- 安裝 requirements.txt 中的依賴
- 使用 Procfile 啟動應用

### 4. 取得 Webhook URL
部署完成後，您會得到一個類似這樣的 URL：
```
https://your-app-name.railway.app
```

您的 LINE Bot Webhook URL 就是：
```
https://your-app-name.railway.app/webhook
```

## 🔧 設定 LINE Bot Webhook

### 1. 前往 LINE Developers Console
- 登入 [LINE Developers](https://developers.line.biz/)
- 選擇您的 Bot
- 進入 "Messaging API" 設定

### 2. 設定 Webhook URL
```
Webhook URL: https://your-app-name.railway.app/webhook
```

### 3. 驗證 Webhook
- 點擊 "Verify" 按鈕
- 確保顯示成功訊息

### 4. 啟用 Webhook
- 確保 "Use webhook" 開關是開啟的

## 🧪 測試部署

### 1. 檢查健康狀態
訪問：`https://your-app-name.railway.app/health`

應該會看到：
```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "service": "LINE Bot 語音助手"
}
```

### 2. 測試 LINE Bot
- 加您的 LINE Bot 為好友
- 發送語音訊息
- 確認收到 AI 處理後的繁體中文回覆

## 🐛 故障排除

### 查看 Railway 日誌
在 Railway 專案頁面點擊 "Deployments" 查看詳細日誌。

### 常見問題

1. **Google Cloud 認證失敗**
   - 確認 `GOOGLE_APPLICATION_CREDENTIALS_JSON` 是完整的 JSON
   - 檢查 JSON 格式是否正確

2. **LINE Bot 驗證失敗**
   - 確認 `LINE_CHANNEL_SECRET` 和 `LINE_CHANNEL_ACCESS_TOKEN` 正確
   - 檢查 Webhook URL 是否可訪問

3. **OpenAI API 錯誤**
   - 確認 `OPENAI_API_KEY` 正確且有額度

## 📱 完成！

部署成功後，您的 LINE Bot 就可以：
- ✅ 接收語音訊息
- ✅ 使用 Google Cloud Speech-to-Text 轉錄
- ✅ 通過 AutoGen 三重 Agent 優化
- ✅ 回傳優質的繁體中文文字

🎉 恭喜您成功部署 AI 語音轉文字助手到 Railway！ 