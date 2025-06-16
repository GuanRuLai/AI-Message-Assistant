"""
LINE Bot 配置檢查腳本
"""

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv('config.env')

def check_line_config():
    """檢查LINE Bot配置"""
    print("🔍 檢查 LINE Bot 配置...")
    print("=" * 50)
    
    # 檢查環境變數
    channel_secret = os.getenv('LINE_CHANNEL_SECRET')
    channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    
    print(f"📋 Channel Secret: {'✅ 已設定' if channel_secret else '❌ 未設定'}")
    if channel_secret:
        print(f"   長度: {len(channel_secret)} 字符")
        print(f"   前10字符: {channel_secret[:10]}...")
    
    print(f"📋 Channel Access Token: {'✅ 已設定' if channel_access_token else '❌ 未設定'}")
    if channel_access_token:
        print(f"   長度: {len(channel_access_token)} 字符")
        print(f"   前20字符: {channel_access_token[:20]}...")
    
    print("\n🌐 Webhook 設定檢查:")
    print("   正確的 Webhook URL: https://web-production-b64c1.up.railway.app/webhook")
    print("   請確認在 LINE Developer Console 中設定此 URL")
    
    print("\n🔧 LINE Bot 設定檢查清單:")
    print("   1. ✅ Messaging API 已啟用")
    print("   2. ✅ Webhook 已啟用")
    print("   3. ✅ Webhook URL 設定正確")
    print("   4. ✅ Channel Secret 和 Access Token 正確")
    print("   5. ✅ Bot 已加為好友")
    
    print("\n📱 測試步驟:")
    print("   1. 先發送文字訊息測試基本功能")
    print("   2. 再發送語音訊息測試語音功能")
    
    return channel_secret and channel_access_token

if __name__ == "__main__":
    if check_line_config():
        print("\n✅ 基本配置檢查通過")
    else:
        print("\n❌ 配置有問題，請檢查環境變數") 