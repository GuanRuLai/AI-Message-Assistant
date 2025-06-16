"""
🤖 AutoGen 0.4 語音助手 - 主程式
支援最新的 AutoGen AgentChat 和 LINE Bot SDK v3
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
    Configuration, ApiClient, MessagingApi,
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
from src.storage import UserStorage

# 載入環境變數
load_dotenv('config.env')

class AutoGenVoiceBot:
    def __init__(self):
        """初始化 AutoGen 語音助手"""
        self.app = Flask(__name__)
        
        # LINE Bot 配置
        self.channel_secret = os.getenv('LINE_CHANNEL_SECRET')
        self.channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        
        if not self.channel_secret or not self.channel_access_token:
            raise ValueError("LINE Channel Secret 或 Access Token 未設定")
        
        # 初始化 LINE Bot v3 API
        self.configuration = Configuration(access_token=self.channel_access_token)
        self.handler = WebhookHandler(self.channel_secret)
        
        # 初始化處理器
        self.audio_processor = AudioProcessor()
        self.speech_processor = SpeechProcessor()
        self.autogen_processor = AutoGenProcessor()
        self.user_storage = UserStorage()
        
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
                    "用戶學習記錄"
                ],
                "endpoints": {
                    "webhook": "/webhook",
                    "health": "/health",
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
                                messages=[TextMessage(text=f"📝 文字優化結果：\n{result}")]
                            )
                        )
                
            except Exception as e:
                logger.error(f"❌ 處理文字訊息錯誤: {e}")
    
    def _process_audio_message(self, user_id: str, message_id: str) -> Optional[dict]:
        """處理語音訊息的完整流程"""
        try:
            # 1. 下載語音檔案
            with ApiClient(self.configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                audio_path = self.audio_processor.download_audio(
                    line_bot_api, message_id, self.temp_dir
                )
            
            if not audio_path:
                return None
            
            # 2. 語音轉文字
            transcription = self.speech_processor.transcribe(audio_path)
            
            if not transcription:
                return None
            
            # 3. AutoGen 處理
            optimized_text = self.autogen_processor.process_text(transcription)
            
            # 4. 儲存用戶互動記錄
            self.user_storage.save_interaction(
                user_id, transcription, optimized_text
            )
            
            # 5. 清理臨時檔案
            self.audio_processor.cleanup_file(audio_path)
            
            return {
                'original': transcription,
                'optimized': optimized_text
            }
            
        except Exception as e:
            logger.error(f"❌ 處理語音訊息失敗: {e}")
            return None
    
    def _send_result(self, user_id: str, result: dict):
        """發送處理結果"""
        try:
            response_text = "✨ 語音轉文字完成\n\n"
            response_text += f"🎯 原始文字：\n{result['original']}\n\n"
            response_text += f"📝 AI 優化結果：\n{result['optimized']}"
            
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
• 學習記錄追蹤

📱 使用方法：
1. 發送語音訊息進行轉文字
2. 發送文字訊息進行優化
3. 輸入「狀態」查看使用記錄
4. 輸入「幫助」查看此說明

⚡ 指令：
• help/幫助 - 顯示使用說明
• status/狀態 - 查看使用統計

🔧 技術特色：
• 採用最新 AutoGen 0.4 架構
• LINE Bot SDK v3 支援
• Google Cloud Speech-to-Text
• 智能文字優化"""
    
    def _get_status_message(self, user_id: str) -> str:
        """獲取用戶狀態訊息"""
        try:
            stats = self.user_storage.get_user_stats(user_id)
            return f"""📊 您的使用統計

🎤 語音處理次數: {stats.get('audio_count', 0)}
📝 文字處理次數: {stats.get('text_count', 0)}
📅 首次使用: {stats.get('first_use', '未知')}
🕒 最後使用: {stats.get('last_use', '未知')}

🚀 版本：AutoGen 0.4"""
        except:
            return "📊 暫無使用記錄"
    
    def run(self):
        """啟動 Flask 應用程式"""
        port = int(os.environ.get('PORT', 8000))  # Replit 使用動態端口
        host = '0.0.0.0'  # 允許外部訪問
        
        logger.info(f"🚀 啟動 AutoGen 0.4 語音助手服務於 {host}:{port}")
        
        # Replit 環境使用
        self.app.run(
            host=host,
            port=port,
            debug=False  # 生產環境關閉 debug
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