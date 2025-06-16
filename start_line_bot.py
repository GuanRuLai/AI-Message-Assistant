#!/usr/bin/env python3
"""
🚀 LINE Bot 語音助手 - 快速啟動腳本
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 確保 agents 模組可以被導入
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 載入環境變數
load_dotenv('config.env')

def check_requirements():
    """檢查必要的設定"""
    required_vars = [
        'OPENAI_API_KEY',
        'LINE_CHANNEL_SECRET', 
        'LINE_CHANNEL_ACCESS_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ 缺少必要的環境變數:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n請檢查 config.env 檔案設定")
        return False
    
    return True

def main():
    """主程式"""
    print("🤖 LINE Bot 語音助手啟動中...")
    
    # 檢查設定
    if not check_requirements():
        sys.exit(1)
    
    try:
        # 導入並啟動 LINE Bot
        from line_bot_app import LineVoiceBot
        
        print("✅ 正在初始化 LINE Bot...")
        bot = LineVoiceBot()
        
        print("🚀 啟動成功！按 Ctrl+C 停止服務")
        bot.run()
        
    except KeyboardInterrupt:
        print("\n🛑 服務已停止")
    except ImportError as e:
        print(f"❌ 導入模組失敗: {e}")
        print("請確認已安裝所有依賴套件: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 