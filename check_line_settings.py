"""
🔍 LINE Developer Console 設定檢查工具
幫助診斷 webhook events 空陣列問題
"""

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv('config.env')

def check_line_settings():
    """檢查LINE Bot設定"""
    print("🔍 LINE Developer Console 設定檢查")
    print("=" * 60)
    
    # 檢查基本配置
    channel_secret = os.getenv('LINE_CHANNEL_SECRET')
    channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    
    print("📋 基本配置檢查:")
    print(f"   Channel Secret: {'✅ 已設定' if channel_secret else '❌ 未設定'}")
    print(f"   Access Token: {'✅ 已設定' if channel_access_token else '❌ 未設定'}")
    print()
    
    # Webhook URL
    webhook_url = "https://web-production-b64c1.up.railway.app/webhook"
    print("🌐 Webhook 設定:")
    print(f"   正確的 Webhook URL: {webhook_url}")
    print()
    
    # 重要設定檢查清單
    print("🔧 LINE Developer Console 必要設定檢查清單:")
    print("   請登入 https://developers.line.biz/console/ 檢查以下設定：")
    print()
    
    print("1. 📱 Basic settings (基本設定):")
    print("   ✅ Channel type: Messaging API")
    print("   ✅ Channel name: 已設定")
    print("   ✅ Channel description: 已設定")
    print()
    
    print("2. 🔗 Messaging API settings:")
    print("   ✅ Webhook URL: " + webhook_url)
    print("   ✅ Use webhook: ON (必須開啟)")
    print("   ✅ Verify webhook: 點擊驗證應該顯示 Success")
    print()
    
    print("3. ❌ 自動回覆設定 (這是關鍵!):")
    print("   ❌ Auto-reply messages: OFF (必須關閉)")
    print("   ❌ Greeting messages: OFF (必須關閉)")
    print("   📝 說明: 如果自動回覆開啟，webhook會收到空events")
    print()
    
    print("4. 🔐 Channel access token:")
    print("   ✅ 已生成並複製到環境變數")
    print()
    
    print("5. 🔑 Channel secret:")
    print("   ✅ 已複製到環境變數")
    print()
    
    print("🚨 常見問題診斷:")
    print("   如果收到 events: [] 空陣列，通常是因為：")
    print("   1. 自動回覆訊息 (Auto-reply messages) 沒有關閉")
    print("   2. 歡迎訊息 (Greeting messages) 沒有關閉") 
    print("   3. Webhook 沒有正確啟用")
    print("   4. Bot 還沒有被加為好友")
    print()
    
    print("🔧 解決步驟:")
    print("   1. 登入 LINE Developer Console")
    print("   2. 選擇您的 Messaging API Channel")
    print("   3. 點擊 'Messaging API' 標籤")
    print("   4. 確認 'Use webhook' 是 ON")
    print("   5. 確認 'Auto-reply messages' 是 OFF")
    print("   6. 確認 'Greeting messages' 是 OFF")
    print("   7. 點擊 'Verify' 測試 Webhook URL")
    print()
    
    print("📱 測試步驟:")
    print("   1. 先發送文字訊息測試")
    print("   2. 再發送語音訊息測試")
    print("   3. 檢查日誌是否有 events 內容")

if __name__ == "__main__":
    check_line_settings() 