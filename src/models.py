"""
AutoGen 0.4 模型處理器
使用最新的 AutoGen AgentChat 架構
"""

import os
import asyncio
from typing import Optional
from loguru import logger

# AutoGen 0.4 imports
try:
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    AUTOGEN_AVAILABLE = True
    logger.info("✅ AutoGen 0.4 模組載入成功")
except ImportError as e:
    AUTOGEN_AVAILABLE = False
    logger.warning(f"⚠️ AutoGen 0.4 不可用: {e}")
    logger.info("🔄 將使用備用文字處理功能")


class AutoGenProcessor:
    def __init__(self):
        """初始化 AutoGen 0.4 處理器"""
        self.client = None
        self.optimizer_agent = None
        self.traditional_agent = None
        self.team = None
        
        if AUTOGEN_AVAILABLE:
            try:
                self._initialize_client()
                self._initialize_agents()
                logger.info("🤖 AutoGen 0.4 處理器已初始化")
            except Exception as e:
                logger.error(f"❌ AutoGen 0.4 初始化失敗: {e}")
                logger.warning("⚠️ 將使用基礎文字處理")
        else:
            logger.warning("⚠️ AutoGen 0.4 不可用，將使用基礎文字處理")
    
    def _initialize_client(self):
        """初始化 OpenAI 客戶端"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY 未設定")
            
            model = os.getenv('AUTOGEN_MODEL', 'gpt-4o')
            
            # 修正環境變數讀取
            temperature_str = os.getenv('AUTOGEN_TEMPERATURE', '0.7')
            try:
                # 清理環境變數中可能的換行符和額外字符
                temperature_clean = temperature_str.strip().split('=')[-1]
                temperature = float(temperature_clean)
            except (ValueError, IndexError):
                logger.warning(f"⚠️ AUTOGEN_TEMPERATURE 格式錯誤: {temperature_str}，使用預設值 0.7")
                temperature = 0.7
            
            self.client = OpenAIChatCompletionClient(
                model=model,
                api_key=api_key,
                temperature=temperature,
            )
            
            logger.info("✅ AutoGen 0.4 OpenAI 客戶端初始化成功")
            
        except Exception as e:
            logger.error(f"❌ AutoGen 0.4 客戶端初始化失敗: {e}")
            raise
    
    def _initialize_agents(self):
        """初始化 AutoGen 0.4 Agents"""
        try:
            if not self.client:
                return
            
            # 內容優化專家 Agent
            self.optimizer_agent = AssistantAgent(
                name="content_optimizer",
                model_client=self.client,
                system_message="""你是專業的文字內容優化專家。

你的任務：
1. 接收語音轉文字的原始結果
2. 修正語音辨識錯誤並優化內容
3. 補充遺漏的標點符號
4. 修正同音異字錯誤
5. 整理語句結構並提升可讀性
6. 維持一定的人性化表達

處理重點：
- 修正語音辨識的斷句錯誤
- 修正同音字混淆（如：的/得、在/再、做/作）
- 改善語法結構和用詞
- 調整語句順序提升邏輯性
- 消除冗餘表達

請直接輸出優化後的文字，不要加入額外說明。"""
            )
            
            # 繁體中文轉換專家 Agent
            self.traditional_agent = AssistantAgent(
                name="traditional_chinese_converter",
                model_client=self.client,
                system_message="""你是專業的繁體中文轉換專家。

你的任務：
1. 接收已優化的文字內容
2. 將所有簡體中文字符轉換為繁體中文
3. 使用台灣常用的繁體中文詞彙和表達方式
4. 確保輸出100%符合台灣繁體中文標準

重要轉換對照：
- 软件→軟體、网络→網路、信息→資訊、程序→程式
- 计算机→電腦、设置→設定、文件→檔案、用户→使用者
- 应用→應用、系统→系統、数据→資料、处理→處理
- 连接→連線、下载→下載、上传→上傳、存储→儲存

請直接輸出轉換後的繁體中文文字，不要加入額外說明。"""
            )
            
            # 建立團隊協作（只有兩個Agent）
            self.team = RoundRobinGroupChat([
                self.optimizer_agent, 
                self.traditional_agent
            ])
            
            logger.info("✅ AutoGen 0.4 Agents 初始化成功（2個Agent）")
            
        except Exception as e:
            logger.error(f"❌ AutoGen 0.4 Agents 初始化失敗: {e}")
            raise
    
    def process_text(self, text: str) -> str:
        """
        處理文字（AutoGen 0.4 協作）
        
        Args:
            text: 輸入文字
            
        Returns:
            優化後的文字
        """
        try:
            if not AUTOGEN_AVAILABLE or not self.team:
                return self._fallback_processing(text)
            
            logger.info("🚀 開始 AutoGen 0.4 協作處理（2個Agent）")
            logger.info(f"📝 原始文字: {text}")
            
            # 嘗試使用簡化的直接處理方式
            try:
                result = asyncio.run(self._simple_agent_processing(text))
                logger.info(f"✅ AutoGen 0.4 處理完成: {result}")
                return result
            except Exception as e:
                logger.warning(f"⚠️ 簡化處理失敗，嘗試團隊協作: {e}")
                
                # 如果簡化處理失敗，嘗試團隊協作
                try:
                    task = f"請處理以下文字：{text}"
                    result = asyncio.run(self._run_team_collaboration(task))
                    logger.info(f"✅ AutoGen 0.4 團隊協作完成: {result}")
                    return result
                except Exception as e2:
                    logger.error(f"❌ AutoGen 0.4 協作失敗: {e2}")
                    return self._fallback_processing(text)
            
        except Exception as e:
            logger.error(f"❌ AutoGen 處理失敗: {e}")
            return self._fallback_processing(text)
    
    async def _run_team_collaboration(self, task: str) -> str:
        """運行團隊協作（簡化版本）"""
        try:
            # 使用 AutoGen 0.4 的正確協作方式
            from autogen_core import CancellationToken
            import asyncio
            
            # 創建取消令牌，設定超時時間
            cancellation_token = CancellationToken()
            
            # 運行團隊協作，設定超時防止卡住
            try:
                result = await asyncio.wait_for(
                    self.team.run(
                        task=task,
                        cancellation_token=cancellation_token
                    ),
                    timeout=30.0  # 30秒超時
                )
            except asyncio.TimeoutError:
                logger.error("❌ AutoGen 協作超時，使用備用處理")
                raise Exception("AutoGen collaboration timeout")
            
            # 提取最終結果
            if hasattr(result, 'messages') and result.messages:
                # 獲取最後一條消息的內容
                last_message = result.messages[-1]
                if hasattr(last_message, 'content'):
                    return last_message.content
                else:
                    return str(last_message)
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"❌ 團隊協作運行失敗: {e}")
            raise
    
    async def _simple_agent_processing(self, text: str) -> str:
        """簡化的Agent處理（直接調用Agent而不使用團隊協作）"""
        try:
            from autogen_core import CancellationToken
            from autogen_agentchat.messages import TextMessage
            import asyncio
            
            cancellation_token = CancellationToken()
            
            # 第一步：內容優化
            logger.info("🔧 步驟1: 內容優化")
            optimizer_response = await asyncio.wait_for(
                self.optimizer_agent.on_messages(
                    [TextMessage(content=text, source="user")], 
                    cancellation_token
                ),
                timeout=15.0
            )
            
            optimized_text = optimizer_response.chat_message.content
            logger.info(f"✅ 優化完成: {optimized_text}")
            
            # 第二步：繁體中文轉換
            logger.info("🔧 步驟2: 繁體中文轉換")
            traditional_response = await asyncio.wait_for(
                self.traditional_agent.on_messages(
                    [TextMessage(content=optimized_text, source="optimizer")], 
                    cancellation_token
                ),
                timeout=15.0
            )
            
            final_text = traditional_response.chat_message.content
            logger.info(f"✅ 轉換完成: {final_text}")
            
            return final_text
            
        except asyncio.TimeoutError:
            logger.error("❌ 簡化處理超時")
            raise Exception("Simple agent processing timeout")
        except Exception as e:
            logger.error(f"❌ 簡化處理失敗: {e}")
            raise
    
    def _fallback_processing(self, text: str) -> str:
        """
        備用文字處理（當 AutoGen 不可用時）
        
        Args:
            text: 輸入文字
            
        Returns:
            基礎處理後的文字
        """
        try:
            logger.info("🔄 使用備用文字處理")
            
            # 基礎的繁體中文轉換和標點符號處理
            processed_text = self._basic_traditional_conversion(text)
            processed_text = self._basic_punctuation_fix(processed_text)
            
            return processed_text
            
        except Exception as e:
            logger.error(f"❌ 備用處理失敗: {e}")
            return text  # 返回原始文字
    
    def _basic_traditional_conversion(self, text: str) -> str:
        """基礎繁體中文轉換"""
        conversions = {
            # 常見簡體轉繁體
            '软件': '軟體', '网络': '網路', '信息': '資訊', '程序': '程式',
            '计算机': '電腦', '设置': '設定', '文件': '檔案', '用户': '使用者',
            '应用': '應用', '系统': '系統', '数据': '資料', '处理': '處理',
            '连接': '連線', '下载': '下載', '上传': '上傳', '存储': '儲存',
            '视频': '影片', '音频': '音訊', '图片': '圖片', '照片': '相片',
            '打开': '開啟', '关闭': '關閉', '保存': '儲存', '删除': '刪除'
        }
        
        for simplified, traditional in conversions.items():
            text = text.replace(simplified, traditional)
        
        return text
    
    def _basic_punctuation_fix(self, text: str) -> str:
        """基礎標點符號處理"""
        # 在句子結尾添加句號（如果沒有的話）
        text = text.strip()
        if text and not text.endswith(('。', '！', '？', '...', '…')):
            text += '。'
        
        return text
    
    def get_agent_info(self) -> dict:
        """獲取 Agent 資訊"""
        return {
            'autogen_available': AUTOGEN_AVAILABLE,
            'agents_initialized': self.team is not None,
            'version': '0.4.0',
            'agents': [
                'content_optimizer', 
                'traditional_chinese_converter'
            ] if self.team else []
        }
    
    def test_agents(self) -> dict:
        """測試 Agents 可用性"""
        if not AUTOGEN_AVAILABLE:
            return {
                'available': False,
                'error': 'AutoGen 0.4 不可用'
            }
        
        try:
            test_text = "测试文字处理功能"
            result = self.process_text(test_text)
            
            return {
                'available': True,
                'test_input': test_text,
                'test_output': result,
                'agents_count': len(self.team.participants) if self.team else 0
            }
            
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            } 