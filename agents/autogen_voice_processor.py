"""
AutoGen 語音處理器 (Google Cloud Speech-to-Text 版本)
結合 Google Cloud Speech-to-Text 和 AutoGen 三重 Agent 協作
"""

import os
import asyncio
import json
from typing import Optional
from loguru import logger

# 導入 Google Cloud Speech-to-Text 處理器
from .google_stt_processor import GoogleSTTProcessor

# AutoGen 相關 - 使用新的AG2包名
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

class AutoGenVoiceProcessor:
    def __init__(self):
        """初始化 AutoGen 語音處理器"""
        self.stt_processor = None
        self.speech_agent = None
        self.optimization_agent = None
        self.traditional_chinese_agent = None
        self.user_proxy = None
        self.group_chat = None
        self.group_chat_manager = None
        
        # 配置
        self.openai_config = {
            "model": os.getenv('AUTOGEN_MODEL', 'gpt-4o'),
            "api_key": os.getenv('OPENAI_API_KEY'),
            "temperature": float(os.getenv('AUTOGEN_TEMPERATURE', '0.7'))
        }
        
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化所有組件"""
        try:
            # 初始化 Google Cloud Speech-to-Text 處理器
            self.stt_processor = GoogleSTTProcessor()
            
            # 建立 SpeechAgent
            self.speech_agent = AssistantAgent(
                name="speech_processor",
                system_message="""你是專業的語音轉文字處理專家。

你的任務：
1. 接收語音轉文字的原始結果
2. 修正可能的語音辨識錯誤
3. 保持原意不變，只修正明顯的錯誤
4. 【重要】必須輸出繁體中文

注意事項：
- 不要改變原始語意
- 修正標點符號和語法錯誤
- 保持自然的語言風格
- 使用台灣常用的詞彙表達
- 完成後直接輸出修正後的文字
""",
                llm_config={"config_list": [self.openai_config]}
            )
            
            # 建立 OptimizationAgent
            self.optimization_agent = AssistantAgent(
                name="content_optimizer",
                system_message="""你是專業的內容優化專家。

你的任務：
1. 接收已處理的語音文字
2. 優化文字的表達方式和結構
3. 提升文字的專業度和可讀性
4. 確保內容簡潔有力
5. 輸出優化後的繁體中文內容

優化原則：
- 保持原始意思不變
- 改善語法和用詞
- 增強表達的清晰度
- 使用常用詞彙和自然表達
- 完成後直接輸出優化後的文字
""",
                llm_config={"config_list": [self.openai_config]}
            )
            
            # 建立 TraditionalChineseAgent
            self.traditional_chinese_agent = AssistantAgent(
                name="traditional_chinese_converter",
                system_message="""你是專業的簡繁轉換專家。

你的任務：
1. 接收任何中文文字
2. 將所有簡體中文字符轉換為繁體中文
3. 使用台灣常用的繁體中文詞彙
4. 確保輸出100%繁體中文

常用轉換：
- 软件→軟體 网络→網路 信息→資訊 程序→程式
- 计算机→電腦 设置→設定 文件→檔案 用户→使用者

完成後直接輸出轉換後的繁體中文文字。
""",
                llm_config={"config_list": [self.openai_config]}
            )
            
            # 建立 UserProxy
            self.user_proxy = UserProxyAgent(
                name="user_proxy",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=1,
                code_execution_config=False
            )
            
            logger.info("AutoGen 語音處理器初始化成功")
            
        except Exception as e:
            logger.error(f"初始化 AutoGen 語音處理器失敗: {str(e)}")
            raise
    
    async def process_audio(self, audio_path: str) -> str:
        """處理語音檔案，返回優化後的文字"""
        try:
            # 1. 語音轉文字
            logger.info("開始語音轉文字...")
            transcription = await self.stt_processor.transcribe_audio(audio_path)
            logger.info(f"語音轉文字結果: {transcription}")
            
            # 2. AutoGen 三重 Agent 協作優化
            logger.info("開始 AutoGen 三重 Agent 協作...")
            optimized_text = await self._optimize_with_agents(transcription)
            
            return optimized_text
            
        except Exception as e:
            logger.error(f"處理語音時發生錯誤: {str(e)}")
            return f"處理失敗: {str(e)}"
    
    async def _optimize_with_agents(self, text: str) -> str:
        """使用 AutoGen 三重 Agent 協作優化文字"""
        try:
            if not os.getenv('ENABLE_TEXT_OPTIMIZATION', 'true').lower() == 'true':
                logger.info("文字優化已停用，使用簡單轉換")
                return self._simple_optimize(text)
            
            # 檢查文字長度
            if len(text.strip()) < 3:
                return f"原始文字：{text}\n結果：{text}"
            
            # 建立群組聊天
            groupchat = GroupChat(
                agents=[self.user_proxy, self.speech_agent, self.optimization_agent, self.traditional_chinese_agent],
                messages=[],
                max_round=6
            )
            
            manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": [self.openai_config]})
            
            # 建立初始訊息
            initial_message = f"請處理以下語音轉文字結果：{text}"
            
            # 開始對話
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = self.user_proxy.initiate_chat(
                    manager,
                    message=initial_message,
                    max_turns=3
                )
                
                # 提取最終結果
                if result and hasattr(result, 'chat_history'):
                    final_message = result.chat_history[-1].get('content', text)
                    optimized_text = self._extract_final_text(final_message)
                else:
                    optimized_text = text
                
                return f"原始文字：{text}\n優化結果：{optimized_text}"
                
            finally:
                loop.close()
            
        except Exception as e:
            logger.error(f"AutoGen 協作失敗: {str(e)}")
            return self._simple_optimize(text)
    
    def _simple_optimize(self, text: str) -> str:
        """簡單的文字優化（備用方案）"""
        try:
            # 基本的簡繁轉換
            simplified_chars = {
                '软件': '軟體', '网络': '網路', '信息': '資訊', '程序': '程式',
                '计算机': '電腦', '设置': '設定', '文件': '檔案', '用户': '使用者',
                '应用': '應用', '系统': '系統', '数据': '資料', '处理': '處理',
                '连接': '連線', '下载': '下載', '上传': '上傳', '存储': '儲存'
            }
            
            result = text
            for simplified, traditional in simplified_chars.items():
                result = result.replace(simplified, traditional)
            
            return f"原始文字：{text}\n結果：{result}"
            
        except Exception as e:
            logger.error(f"簡單優化失敗: {str(e)}")
            return f"原始文字：{text}\n結果：{text}"
    
    def _extract_final_text(self, message: str) -> str:
        """從最終訊息中提取處理後的文字"""
        # 簡單的文字提取邏輯
        if "結果：" in message:
            return message.split("結果：")[-1].strip()
        elif "優化後：" in message:
            return message.split("優化後：")[-1].strip()
        else:
            return message.strip()
    
    def get_stt_info(self) -> dict:
        """獲取 Speech-to-Text 模型資訊"""
        if self.stt_processor:
            return self.stt_processor.get_model_info()
        return {"status": "not_initialized"}
    
    def get_status(self) -> dict:
        """獲取處理器狀態"""
        return {
            "stt_processor": "initialized" if self.stt_processor else "not_initialized",
            "speech_agent": "initialized" if self.speech_agent else "not_initialized",
            "optimization_agent": "initialized" if self.optimization_agent else "not_initialized",
            "traditional_chinese_agent": "initialized" if self.traditional_chinese_agent else "not_initialized",
            "status": "ready"
        } 