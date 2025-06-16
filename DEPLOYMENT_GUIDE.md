# 🚀 AutoGen 0.4 語音助手 - Railway 部署指南

## 📋 專案優化總結

### ✅ 已完成的升級和優化

1. **升級到 AutoGen 0.4**
   - 使用 `autogen-agentchat==0.4.0` 最新版本
   - 採用全新的 Agent 協作架構
   - 支援異步處理和更好的效能

2. **升級到 LINE Bot SDK v3**
   - 使用 `line-bot-sdk==3.17.1` 最新版本
   - 重構所有 API 呼叫以適應新架構
   - 改善訊息處理和錯誤處理

3. **Railway 部署優化**
   - 動態端口支援 (`PORT` 環境變數)
   - 簡化 `nixpacks.toml` 配置
   - 生產環境設定
   - 健康檢查端點

4. **依賴套件優化**
   - 移除衝突套件
   - 更新所有依賴到最新穩定版本
   - 加入錯誤處理和降級方案

## 🔧 Railway 部署步驟

### 1. 準備工作

確認您已經有以下 API 金鑰：
- OpenAI API Key
- LINE Bot Channel Secret
- LINE Bot Channel Access Token  
- Google Cloud Speech-to-Text 認證

### 2. 連接 GitHub 到 Railway

1. 登入 [Railway.app](https://railway.app)
2. 點擊 "New Project"
3. 選擇 "Deploy from GitHub repo"
4. 選擇您的 `AI-Message-Assistant` 專案

### 3. 設定環境變數

在 Railway 專案設定中添加以下環境變數：

```bash
# 🔑 OpenAI API 設定
OPENAI_API_KEY=your_openai_api_key_here

# 🤖 LINE Bot 設定  
LINE_CHANNEL_SECRET=your_line_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here

# 🎤 Google Cloud Speech-to-Text
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}
# 或者
GOOGLE_APPLICATION_CREDENTIALS=credentials.json

# 🔧 選用設定
AUTOGEN_MODEL=gpt-4o
AUTOGEN_TEMPERATURE=0.7
GOOGLE_STT_LANGUAGE=cmn-Hant-TW
GOOGLE_STT_MODEL=default
LOG_LEVEL=INFO
```

### 4. 部署流程

1. **自動建置**: Railway 會自動檢測 `nixpacks.toml` 並開始建置
2. **等待部署**: 建置過程約需 2-5 分鐘
3. **獲取網址**: 部署完成後會獲得公開網址 (如: `https://your-app-name.railway.app`)

### 5. 設定 LINE Bot Webhook

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 選擇您的 Bot
3. 在 "Messaging API" 頁面設定 Webhook URL:
   ```
   https://your-app-name.railway.app/webhook
   ```
4. 啟用 "Use webhook"

## 🏗️ 專案架構

```
專案根目錄/
├── main.py                 # 🚀 主程式 (Flask + AutoGen 0.4)
├── requirements.txt        # 📦 Python 依賴 (最新版本)
├── nixpacks.toml          # 🔧 Railway 建置配置
├── Procfile               # 🚀 啟動指令
├── railway.json           # ⚙️ Railway 專案設定
├── runtime.txt            # 🐍 Python 版本
├── config.env             # 🔐 環境變數範例 (被 .gitignore)
├── src/
│   ├── audio.py           # 🎵 音訊處理 (LINE Bot SDK v3)
│   ├── speech.py          # 🎤 語音轉文字 (Google Cloud STT)
│   ├── models.py          # 🤖 AutoGen 0.4 處理器
│   └── storage.py         # 💾 用戶資料儲存
└── files/                 # 📁 臨時檔案目錄
```

## 🔍 功能特色

### AutoGen 0.4 三重 Agent 協作
1. **語音處理專家**: 修正語音辨識錯誤
2. **內容優化專家**: 提升文字品質和可讀性
3. **繁體中文專家**: 確保繁體中文輸出

### LINE Bot 功能
- 🎤 語音訊息轉文字
- 📝 文字訊息優化
- 📊 使用統計查詢
- ❓ 幫助指令

### 技術優勢
- ⚡ AutoGen 0.4 異步處理
- 🔄 自動錯誤恢復
- 🛡️ 穩健的錯誤處理
- 📈 效能監控
- 🗑️ 自動檔案清理

## 🧪 測試部署

部署完成後，可以通過以下方式測試：

1. **健康檢查**: 訪問 `https://your-app-name.railway.app/health`
2. **LINE Bot 測試**: 發送語音或文字訊息
3. **日誌監控**: 在 Railway 控制台查看部署日誌

## 🐛 故障排除

### 常見問題

1. **建置失敗**
   - 檢查 `requirements.txt` 中的套件版本
   - 確認 Python 版本相容性 (Python 3.11)

2. **AutoGen 初始化失敗**
   - 檢查 `OPENAI_API_KEY` 是否正確設定
   - 確認 API 金鑰有足夠的額度

3. **LINE Bot 無回應**
   - 確認 Webhook URL 設定正確
   - 檢查 `LINE_CHANNEL_SECRET` 和 `LINE_CHANNEL_ACCESS_TOKEN`

4. **語音處理失敗**
   - 檢查 Google Cloud 認證設定
   - 確認 Speech-to-Text API 已啟用

### 日誌查看

在 Railway 控制台中查看即時日誌：
- 🚀 啟動日誌
- 📨 Webhook 請求日誌  
- ❌ 錯誤訊息
- ✅ 處理成功記錄

## 📚 相關連結

- [AutoGen 0.4 文檔](https://microsoft.github.io/autogen/)
- [LINE Bot SDK v3 文檔](https://line.github.io/line-bot-sdk-python/)
- [Railway 部署文檔](https://docs.railway.app/)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)

---

## 🎉 部署成功！

恭喜！您的 AutoGen 0.4 語音助手現在已經成功部署到 Railway，並擁有公開可訪問的網址。

**下一步建議：**
1. 設定 LINE Bot Webhook URL
2. 測試語音和文字功能
3. 監控使用情況和效能
4. 根據需要調整 AutoGen 模型參數

如有任何問題，請檢查 Railway 部署日誌或聯繫技術支援。 