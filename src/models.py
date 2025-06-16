"""
AutoGen 模型處理器
負責三重 Agent 協作優化文字
"""

import os
import asyncio
from typing import Optional
from loguru import logger
from autogen import AssistantAgent, UserProxyAgent


class AutoGenProcessor:
    def __init__(self):
        """初始化 AutoGen 處理器"""
        self.llm_config = None
        self.speech_agent = None
        self.optimizer_agent = None
        self.traditional_agent = None
        self.user_proxy = None
        
        self._initialize_config()
        self._initialize_agents()
        logger.info("🤖 AutoGen 處理器已初始化")
    
    def _initialize_config(self):
        """初始化 LLM 配置"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY 未設定")
            
            self.llm_config = {
                "config_list": [
                    {
                        "model": os.getenv('AUTOGEN_MODEL', 'gpt-4o'),
                        "api_key": api_key,
                        "temperature": float(os.getenv('AUTOGEN_TEMPERATURE', '0.7')),
                    }
                ],
                "timeout": 120,
            }
            
            logger.info("✅ AutoGen LLM 配置初始化成功")
            
        except Exception as e:
            logger.error(f"❌ AutoGen LLM 配置初始化失敗: {e}")
            raise
    
    def _initialize_agents(self):
        """初始化三重 Agent"""
        try:
            # 語音處理專家 Agent
            self.speech_agent = AssistantAgent(
                name="speech_processor",
                system_message="""你是專業的語音辨識後處理專家。

你的任務：
1. 接收語音轉文字的原始結果
2. 修正常見的語音辨識錯誤
3. 補充遺漏的標點符號
4. 修正同音異字錯誤
5. 整理語句結構

常見修正：
- 語音辨識的斷句錯誤
- 同音字混淆（如：的/得、在/再、做/作）
- 缺少標點符號
- 口語化表達的整理

請直接輸出修正後的文字，不要加入額外說明。""",
                llm_config=self.llm_config
            )
            
            # 內容優化專家 Agent
            self.optimizer_agent = AssistantAgent(
                name="content_optimizer",
                system_message="""你是專業的文字內容優化專家。

你的任務：
1. 接收已修正的文字內容
2. 優化語法結構和用詞
3. 提升文字的可讀性和專業度
4. 保持原意不變的前提下改善表達
5. 確保語句通順自然

優化重點：
- 改善語法結構
- 選用更精確的詞彙
- 調整語句順序提升邏輯性
- 消除冗餘表達
- 提升整體文字品質

請直接輸出優化後的文字，不要加入額外說明。""",
                llm_config=self.llm_config
            )
            
            # 繁體中文轉換專家 Agent
            self.traditional_agent = AssistantAgent(
                name="traditional_chinese_converter",
                system_message="""你是專業的繁體中文轉換專家。

你的任務：
1. 接收任何中文文字內容
2. 將所有簡體中文字符轉換為繁體中文
3. 使用台灣常用的繁體中文詞彙和表達方式
4. 確保輸出100%符合台灣繁體中文標準

重要轉換對照：
- 软件→軟體、网络→網路、信息→資訊、程序→程式
- 计算机→電腦、设置→設定、文件→檔案、用户→使用者
- 应用→應用、系统→系統、数据→資料、处理→處理
- 连接→連線、下载→下載、上传→上傳、存储→儲存

請直接輸出轉換後的繁體中文文字，不要加入額外說明。""",
                llm_config=self.llm_config
            )
            
            # 用戶代理
            self.user_proxy = UserProxyAgent(
                name="user_proxy",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=1,
                code_execution_config=False
            )
            
            logger.info("✅ AutoGen 三重 Agent 初始化成功")
            
        except Exception as e:
            logger.error(f"❌ AutoGen Agent 初始化失敗: {e}")
            raise
    
    def process_text(self, text: str) -> str:
        """
        處理文字（三重 Agent 協作）
        
        Args:
            text: 輸入文字
            
        Returns:
            優化後的文字
        """
        try:
            logger.info("🚀 開始 AutoGen 三重 Agent 協作處理")
            logger.info(f"📝 原始文字: {text}")
            
            # 階段1: 語音處理專家修正
            logger.info("🔧 階段1: 語音辨識後處理")
            speech_result = self._process_with_agent(self.speech_agent, text)
            logger.info(f"✅ 語音處理結果: {speech_result}")
            
            # 階段2: 內容優化專家優化
            logger.info("📈 階段2: 內容優化處理")
            optimized_result = self._process_with_agent(self.optimizer_agent, speech_result)
            logger.info(f"✅ 內容優化結果: {optimized_result}")
            
            # 階段3: 繁體中文轉換專家轉換
            logger.info("🇹🇼 階段3: 繁體中文轉換")
            final_result = self._process_with_agent(self.traditional_agent, optimized_result)
            logger.info(f"✅ 最終結果: {final_result}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ AutoGen 處理失敗: {e}")
            return self._fallback_processing(text)
    
    def _process_with_agent(self, agent: AssistantAgent, text: str) -> str:
        """
        使用指定 Agent 處理文字
        
        Args:
            agent: 要使用的 Agent
            text: 輸入文字
            
        Returns:
            處理後的文字
        """
        try:
            # 發起對話
            self.user_proxy.initiate_chat(
                agent,
                message=text,
                clear_history=True
            )
            
            # 獲取最後一條回覆
            chat_history = self.user_proxy.chat_messages[agent]
            if chat_history:
                last_message = chat_history[-1]
                result = last_message.get('content', text)
                return self._extract_clean_text(result)
            
            return text
            
        except Exception as e:
            logger.error(f"❌ Agent 處理失敗: {e}")
            return text
    
    def _extract_clean_text(self, message: str) -> str:
        """
        從 Agent 回覆中提取純文字
        
        Args:
            message: Agent 回覆訊息
            
        Returns:
            提取的純文字
        """
        # 移除可能的格式標記和說明文字
        text = message.strip()
        
        # 移除常見的回覆前綴
        prefixes_to_remove = [
            "修正後的文字：", "優化後的文字：", "轉換後的文字：",
            "結果：", "輸出：", "答案：", "修正：", "優化：", "轉換："
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        return text
    
    def _fallback_processing(self, text: str) -> str:
        """
        備用處理方案（簡單的文字優化）
        
        Args:
            text: 輸入文字
            
        Returns:
            簡單優化後的文字
        """
        try:
            logger.info("🔄 使用備用處理方案")
            
            # 基本的簡繁轉換
            simplified_to_traditional = {
                '软件': '軟體', '网络': '網路', '信息': '資訊', '程序': '程式',
                '计算机': '電腦', '设置': '設定', '文件': '檔案', '用户': '使用者',
                '应用': '應用', '系统': '系統', '数据': '資料', '处理': '處理',
                '连接': '連線', '下载': '下載', '上传': '上傳', '存储': '儲存',
                '软': '軟', '硬': '硬', '网': '網', '电': '電', '计': '計'
            }
            
            result = text
            for simplified, traditional in simplified_to_traditional.items():
                result = result.replace(simplified, traditional)
            
            # 基本標點符號整理
            result = result.replace('。。', '。')
            result = result.replace('，，', '，')
            result = result.replace('  ', ' ')
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"❌ 備用處理也失敗: {e}")
            return text
    
    async def process_text_async(self, text: str) -> str:
        """
        異步處理文字
        
        Args:
            text: 輸入文字
            
        Returns:
            優化後的文字
        """
        try:
            # 在新的執行緒中運行同步處理
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.process_text, text)
            return result
            
        except Exception as e:
            logger.error(f"❌ 異步處理失敗: {e}")
            return self._fallback_processing(text)
    
    def get_agent_info(self) -> dict:
        """
        獲取 Agent 資訊
        
        Returns:
            Agent 資訊字典
        """
        return {
            'speech_agent': self.speech_agent.name if self.speech_agent else None,
            'optimizer_agent': self.optimizer_agent.name if self.optimizer_agent else None,
            'traditional_agent': self.traditional_agent.name if self.traditional_agent else None,
            'llm_config': {
                'model': self.llm_config['config_list'][0]['model'] if self.llm_config else None,
                'temperature': self.llm_config['config_list'][0]['temperature'] if self.llm_config else None,
            } if self.llm_config else None
        }
    
    def test_agents(self) -> dict:
        """
        測試所有 Agent 是否正常工作
        
        Returns:
            測試結果字典
        """
        test_text = "这是一个测试文本"
        results = {}
        
        try:
            # 測試語音處理 Agent
            if self.speech_agent:
                speech_result = self._process_with_agent(self.speech_agent, test_text)
                results['speech_agent'] = {
                    'status': 'success',
                    'result': speech_result
                }
            else:
                results['speech_agent'] = {'status': 'not_initialized'}
            
            # 測試優化 Agent
            if self.optimizer_agent:
                optimizer_result = self._process_with_agent(self.optimizer_agent, test_text)
                results['optimizer_agent'] = {
                    'status': 'success',
                    'result': optimizer_result
                }
            else:
                results['optimizer_agent'] = {'status': 'not_initialized'}
            
            # 測試繁體轉換 Agent
            if self.traditional_agent:
                traditional_result = self._process_with_agent(self.traditional_agent, test_text)
                results['traditional_agent'] = {
                    'status': 'success',
                    'result': traditional_result
                }
            else:
                results['traditional_agent'] = {'status': 'not_initialized'}
            
        except Exception as e:
            logger.error(f"❌ Agent 測試失敗: {e}")
            results['error'] = str(e)
        
        return results 