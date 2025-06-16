"""
🤖 LINE Bot 語音轉文字助手
功能：接收語音訊息 → AutoGen 三重 Agent 處理 → 回傳優化繁體中文
"""

import os
import asyncio
import tempfile
import traceback
from datetime import datetime
from typing import Optional
from pathlib import Path

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, AudioMessageContent
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    TextMessage, ReplyMessageRequest
)
from dotenv import load_dotenv
from loguru import logger

# 導入現有的 AutoGen 語音處理器
from agents.autogen_voice_processor import AutoGenVoiceProcessor

# 載入環境變數
load_dotenv('config.env')

class LineVoiceBot:
    def __init__(self):
        """初始化 LINE Bot"""
        self.app = Flask(__name__)
        
        # LINE Bot 配置
        self.channel_secret = os.getenv('LINE_CHANNEL_SECRET')
        self.channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        
        if not self.channel_secret or not self.channel_access_token:
            raise ValueError("LINE Channel Secret 或 Access Token 未設定")
        
        # 初始化 LINE Bot API
        configuration = Configuration(access_token=self.channel_access_token)
        self.api_client = ApiClient(configuration)
        self.line_bot_api = MessagingApi(self.api_client)
        self.handler = WebhookHandler(self.channel_secret)
        
        # 初始化 AutoGen 語音處理器
        self.voice_processor = AutoGenVoiceProcessor()
        
        # 臨時音檔目錄
        self.temp_audio_dir = Path(os.getenv('TEMP_AUDIO_DIR', 'temp_audio'))
        self.temp_audio_dir.mkdir(exist_ok=True)
        
        # 設定路由和處理器
        self._setup_routes()
        self._setup_handlers()
        
        logger.info("🤖 LINE Bot 語音助手已啟動")
        logger.info(f"📁 臨時音檔目錄: {self.temp_audio_dir}")
    
    def _setup_routes(self):
        """設定 Flask 路由"""
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """LINE Webhook 端點"""
            signature = request.headers.get('X-Line-Signature', '')
            body = request.get_data(as_text=True)
            
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
                "service": "LINE Bot 語音助手"
            }, 200
        
        @self.app.route('/', methods=['GET'])
        def home():
            """首頁"""
            return {
                "message": "🤖 LINE Bot 語音助手已啟動",
                "features": [
                    "語音轉文字",
                    "AutoGen 三重 Agent 優化",
                    "繁體中文輸出"
                ],
                "webhook": "/webhook",
                "health": "/health"
            }, 200
    
    def _setup_handlers(self):
        """設定 LINE 訊息處理器"""
        
        @self.handler.add(MessageEvent, message=AudioMessageContent)
        def handle_audio_message(event):
            """處理語音訊息"""
            asyncio.run(self._process_audio_message(event))
    
    async def _process_audio_message(self, event):
        """處理語音訊息的異步方法"""
        try:
            logger.info("🎤 收到語音訊息，開始處理...")
            
            # 1. 下載語音檔案
            audio_path = await self._download_audio(event.message.id)
            if not audio_path:
                await self._reply_error(event.reply_token, "語音檔案下載失敗")
                return
            
            # 2. 發送處理中訊息
            await self._reply_message(event.reply_token, "🎧 正在處理您的語音訊息，請稍候...")
            
            # 3. 使用 AutoGen 處理語音
            result = await self._process_with_autogen(audio_path)
            
            # 4. 解析並回傳結果
            if result:
                await self._send_processed_result(event.source.user_id, result)
            else:
                await self._send_error_message(event.source.user_id, "語音處理失敗，請重試")
            
            # 5. 清理臨時檔案
            self._cleanup_temp_file(audio_path)
            
        except Exception as e:
            logger.error(f"❌ 處理語音訊息時發生錯誤: {e}")
            logger.error(f"詳細錯誤: {traceback.format_exc()}")
            await self._reply_error(event.reply_token, "處理過程中發生錯誤，請重試")
    
    async def _download_audio(self, message_id: str) -> Optional[str]:
        """下載語音檔案"""
        try:
            # 使用 LINE Bot API 取得語音內容
            message_content = self.line_bot_api.get_message_content(message_id)
            
            # 建立臨時檔案
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"voice_{timestamp}_{message_id}.m4a"
            audio_path = self.temp_audio_dir / audio_filename
            
            # 儲存語音檔案
            with open(audio_path, 'wb') as audio_file:
                for chunk in message_content.iter_content():
                    audio_file.write(chunk)
            
            logger.info(f"✅ 語音檔案已下載: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"❌ 下載語音檔案失敗: {e}")
            return None
    
    async def _process_with_autogen(self, audio_path: str) -> Optional[str]:
        """使用 AutoGen 處理語音檔案"""
        try:
            logger.info("🚀 開始 AutoGen 三重 Agent 協作...")
            
            # 使用現有的 AutoGen 語音處理器
            result = await self.voice_processor.process_audio(audio_path)
            
            logger.info("✅ AutoGen 處理完成")
            return result
            
        except Exception as e:
            logger.error(f"❌ AutoGen 處理失敗: {e}")
            return None
    
    async def _reply_message(self, reply_token: str, text: str):
        """回覆訊息"""
        try:
            message = TextMessage(text=text)
            request_obj = ReplyMessageRequest(
                reply_token=reply_token,
                messages=[message]
            )
            self.line_bot_api.reply_message(request_obj)
            
        except Exception as e:
            logger.error(f"❌ 回覆訊息失敗: {e}")
    
    async def _send_processed_result(self, user_id: str, result: str):
        """發送處理結果"""
        try:
            # 解析 AutoGen 結果
            original_text = ""
            optimized_text = ""
            
            if "原始文字：" in result and "優化後的文字：" in result:
                parts = result.split("優化後的文字：", 1)
                if len(parts) == 2:
                    original_text = parts[0].replace("原始文字：", "").strip()
                    optimized_text = parts[1].strip()
            else:
                optimized_text = result
            
            # 組合回傳訊息
            response_text = "✨ 語音轉文字完成\n\n"
            
            if original_text:
                response_text += f"🎯 原始文字：\n{original_text}\n\n"
            
            if optimized_text:
                response_text += f"📝 AI 優化結果：\n{optimized_text}"
            else:
                response_text += "❌ 無法處理您的語音內容"
            
            # 推送訊息給用戶
            message = TextMessage(text=response_text)
            self.line_bot_api.push_message(
                to=user_id,
                messages=[message]
            )
            
            logger.info(f"✅ 已發送處理結果給用戶: {user_id}")
            
        except Exception as e:
            logger.error(f"❌ 發送處理結果失敗: {e}")
    
    async def _send_error_message(self, user_id: str, error_msg: str):
        """發送錯誤訊息"""
        try:
            response_text = f"❌ {error_msg}\n\n請重新發送語音訊息，或聯絡客服協助。"
            message = TextMessage(text=response_text)
            self.line_bot_api.push_message(
                to=user_id,
                messages=[message]
            )
            
        except Exception as e:
            logger.error(f"❌ 發送錯誤訊息失敗: {e}")
    
    async def _reply_error(self, reply_token: str, error_msg: str):
        """回覆錯誤訊息"""
        await self._reply_message(reply_token, f"❌ {error_msg}")
    
    def _cleanup_temp_file(self, file_path: str):
        """清理臨時檔案"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🗑️ 已清理臨時檔案: {file_path}")
        except Exception as e:
            logger.warning(f"⚠️ 清理臨時檔案失敗: {e}")
    
    def run(self):
        """啟動 LINE Bot 服務"""
        port = int(os.getenv('PORT', 8000))
        logger.info(f"🚀 LINE Bot 啟動於端口 {port}")
        logger.info(f"📡 Webhook URL: {os.getenv('WEBHOOK_URL', f'http://localhost:{port}/webhook')}")
        
        self.app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )

def main():
    """主程式入口"""
    try:
        # 初始化並啟動 LINE Bot
        bot = LineVoiceBot()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 用戶中斷，正在關閉服務...")
    except Exception as e:
        logger.error(f"❌ 啟動失敗: {e}")
        logger.error(f"詳細錯誤: {traceback.format_exc()}")

if __name__ == "__main__":
    main() 