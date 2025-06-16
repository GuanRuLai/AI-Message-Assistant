"""
🤖 AutoGen 0.4 語音助手 - 主程式
支援最新的 AutoGen AgentChat 和 LINE Bot SDK v3
本地開發版本 - 使用 ngrok 進行測試
"""

import os
import sys
import tempfile
import traceback
from datetime import datetime
from typing import Optional
from pathlib import Path

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, MessagingApiBlob,
    ReplyMessageRequest, PushMessageRequest, TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent, AudioMessageContent, TextMessageContent
)
from dotenv import load_dotenv
from loguru import logger

# 導入自定義模組
from src.audio import AudioProcessor
from src.speech import SpeechProcessor
from src.models import AutoGenProcessor

# 載入環境變數
load_dotenv('config.env')

class AutoGenVoiceBot:
    def __init__(self):
        """初始化 AutoGen 語音助手"""
        self.app = Flask(__name__)
        
        # LINE Bot 配置 - 新增除錯資訊
        self.channel_secret = os.getenv('LINE_CHANNEL_SECRET')
        self.channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        
        # 除錯：顯示環境變數狀態
        logger.info(f"🔍 環境變數檢查:")
        logger.info(f"   LINE_CHANNEL_SECRET: {'已設定' if self.channel_secret else '未設定'}")
        logger.info(f"   LINE_CHANNEL_ACCESS_TOKEN: {'已設定' if self.channel_access_token else '未設定'}")
        
        if not self.channel_secret or not self.channel_access_token:
            # 提供更詳細的錯誤資訊
            missing = []
            if not self.channel_secret:
                missing.append("LINE_CHANNEL_SECRET")
            if not self.channel_access_token:
                missing.append("LINE_CHANNEL_ACCESS_TOKEN")
            
            error_msg = f"缺少環境變數: {', '.join(missing)}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        # 初始化 LINE Bot v3 API
        self.configuration = Configuration(access_token=self.channel_access_token)
        self.handler = WebhookHandler(self.channel_secret)
        
        # 初始化處理器
        self.audio_processor = AudioProcessor()
        self.speech_processor = SpeechProcessor()
        self.autogen_processor = AutoGenProcessor()
        
        # 臨時檔案目錄
        self.temp_dir = Path('files')
        self.temp_dir.mkdir(exist_ok=True)
        
        # 設定路由和處理器
        self._setup_routes()
        self._setup_handlers()
        
        logger.info("🤖 AutoGen 0.4 語音助手已啟動")
    
    def _setup_routes(self):
        """設定 Flask 路由"""
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """LINE Webhook 端點"""
            signature = request.headers.get('X-Line-Signature', '')
            body = request.get_data(as_text=True)
            
            logger.info(f"📨 收到 Webhook 請求")
            
            try:
                self.handler.handle(body, signature)
                return 'OK', 200
            except InvalidSignatureError:
                logger.error("❌ LINE Webhook 簽名驗證失敗")
                abort(400)
            except Exception as e:
                logger.error(f"❌ Webhook 處理錯誤: {e}")
                return 'Internal Server Error', 500
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """健康檢查端點"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "AutoGen 0.4 語音助手"
            }, 200
        
        @self.app.route('/env-check', methods=['GET'])
        def env_check():
            """環境變數檢查端點"""
            env_status = {
                "LINE_CHANNEL_SECRET": "已設定" if os.getenv('LINE_CHANNEL_SECRET') else "未設定",
                "LINE_CHANNEL_ACCESS_TOKEN": "已設定" if os.getenv('LINE_CHANNEL_ACCESS_TOKEN') else "未設定",
                "OPENAI_API_KEY": "已設定" if os.getenv('OPENAI_API_KEY') else "未設定",
                "GOOGLE_APPLICATION_CREDENTIALS_JSON": "已設定" if os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON') else "未設定",
                "timestamp": datetime.now().isoformat()
            }
            return env_status, 200
        
        @self.app.route('/', methods=['GET'])
        def home():
            """首頁"""
            return {
                "message": "🤖 AutoGen 0.4 語音助手已啟動",
                "status": "running",
                "features": [
                    "語音轉文字",
                    "AutoGen 0.4 Agent 協作",
                    "繁體中文輸出",
                    "無狀態設計，保護隱私"
                ],
                "endpoints": {
                    "webhook": "/webhook",
                    "health": "/health",
                    "env-check": "/env-check",
                    "home": "/"
                },
                "version": "2024.1",
                "timestamp": datetime.now().isoformat()
            }, 200
    
    def _setup_handlers(self):
        """設定 LINE 訊息處理器"""
        
        @self.handler.add(MessageEvent, message=AudioMessageContent)
        def handle_audio_message(event):
            """處理語音訊息"""
            logger.info("🎤 收到語音訊息，開始處理...")
            
            try:
                user_id = event.source.user_id
                message_id = event.message.id
                
                # 1. 回覆處理中訊息
                with ApiClient(self.configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="🎧 正在處理您的語音訊息，請稍候...")]
                        )
                    )
                
                # 2. 下載並處理語音
                result = self._process_audio_message(user_id, message_id)
                
                # 3. 發送結果
                if result:
                    self._send_result(user_id, result)
                else:
                    self._send_error(user_id, "語音處理失敗，請重試")
                
            except Exception as e:
                logger.error(f"❌ 處理語音訊息錯誤: {e}")
                self._send_error(event.source.user_id, "處理過程中發生錯誤")
        
        @self.handler.add(MessageEvent, message=TextMessageContent)
        def handle_text_message(event):
            """處理文字訊息"""
            text = event.message.text.strip()
            user_id = event.source.user_id
            
            logger.info(f"📝 收到文字訊息: {text}")
            
            try:
                with ApiClient(self.configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    
                    if text.lower() in ['help', '幫助', '說明']:
                        help_text = self._get_help_message()
                        line_bot_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token,
                                messages=[TextMessage(text=help_text)]
                            )
                        )
                    elif text.lower() in ['status', '狀態']:
                        status_text = self._get_status_message(user_id)
                        line_bot_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token,
                                messages=[TextMessage(text=status_text)]
                            )
                        )
                    else:
                        # 一般文字訊息用AutoGen處理
                        result = self.autogen_processor.process_text(text)
                        line_bot_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token,
                                messages=[TextMessage(text=result)]
                            )
                        )
                
            except Exception as e:
                logger.error(f"❌ 處理文字訊息錯誤: {e}")
    
    def _process_audio_message(self, user_id: str, message_id: str) -> Optional[dict]:
        """處理語音訊息的完整流程"""
        try:
            # 1. 下載語音檔案 - 使用 MessagingApiBlob
            with ApiClient(self.configuration) as api_client:
                line_bot_blob_api = MessagingApiBlob(api_client)
                audio_path = self.audio_processor.download_audio(
                    line_bot_blob_api, message_id, self.temp_dir
                )
            
            if not audio_path:
                logger.error("❌ 語音檔案下載失敗")
                return None
            
            # 2. 語音轉文字
            logger.info("🎯 開始語音轉文字...")
            text = self.speech_processor.speech_to_text(audio_path)
            
            if not text:
                logger.error("❌ 語音轉文字失敗")
                self.audio_processor.cleanup_file(audio_path)
                return None
            
            logger.info(f"📝 語音轉文字結果: {text}")
            
            # 3. AutoGen 處理
            logger.info("🤖 開始 AutoGen 處理...")
            autogen_result = self.autogen_processor.process_text(text)
            
            # 4. 清理臨時檔案
            self.audio_processor.cleanup_file(audio_path)
            
            return {
                'original_text': text,
                'processed_text': autogen_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 處理語音訊息錯誤: {e}")
            return None
    
    def _send_result(self, user_id: str, result: dict):
        """發送處理結果"""
        try:
            # 只顯示AI優化結果
            response_text = result['processed_text']
            
            with ApiClient(self.configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=user_id,
                        messages=[TextMessage(text=response_text)]
                    )
                )
            
        except Exception as e:
            logger.error(f"❌ 發送結果失敗: {e}")
    
    def _send_error(self, user_id: str, error_msg: str):
        """發送錯誤訊息"""
        try:
            with ApiClient(self.configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=user_id,
                        messages=[TextMessage(text=f"❌ {error_msg}")]
                    )
                )
        except Exception as e:
            logger.error(f"❌ 發送錯誤訊息失敗: {e}")
    
    def _get_help_message(self) -> str:
        """獲取幫助訊息"""
        return """🎤 AutoGen 0.4 語音助手使用說明

✨ 功能：
• 語音轉文字
• AutoGen 0.4 Agent 協作優化  
• 繁體中文輸出
• 即時處理，無記錄儲存

📱 使用方法：
1. 發送語音訊息進行轉文字
2. 發送文字訊息進行優化
3. 輸入「狀態」查看系統狀態
4. 輸入「幫助」查看此說明

⚡ 指令：
• help/幫助 - 顯示使用說明
• status/狀態 - 查看系統狀態

🔧 技術特色：
• 採用最新 AutoGen 0.4 架構
• LINE Bot SDK v3 支援
• Google Cloud Speech-to-Text
• 智能文字優化
• 無狀態設計，保護隱私"""
    
    def _get_status_message(self, user_id: str) -> str:
        """獲取系統狀態訊息"""
        return f"""📊 系統狀態

🤖 AutoGen 0.4 語音助手
✅ 系統運行正常
🎤 語音轉文字：可用
📝 文字優化：可用
🕒 當前時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 版本：AutoGen 0.4"""
    
    def run(self):
        """啟動 Flask 應用程式 - 本地開發模式"""
        port = int(os.getenv('PORT', 5000))  # 本地開發使用 5000 port
        logger.info(f"🚀 啟動 AutoGen 語音助手 - 本地開發模式")
        logger.info(f"📡 伺服器運行於: http://localhost:{port}")
        logger.info(f"🔗 Webhook 端點: http://localhost:{port}/webhook")
        logger.info(f"💡 請使用 ngrok 建立公開 URL 並設定到 LINE Developer Console")
        
        self.app.run(
            host='0.0.0.0',
            port=port,
            debug=True  # 本地開發啟用 debug 模式
        )

def main():
    """主函數"""
    try:
        bot = AutoGenVoiceBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("👋 程式已停止")
    except Exception as e:
        logger.error(f"❌ 程式啟動失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 