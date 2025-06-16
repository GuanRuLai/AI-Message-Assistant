"""
AutoGen 語音處理器 (Google Cloud Speech-to-Text 版本)
結合 Google Cloud Speech-to-Text 和 AutoGen 三重 Agent 協作
"""

import os
import asyncio
import tempfile
from typing import Optional
from loguru import logger

# 導入 Google Cloud Speech-to-Text 處理器
from .google_stt_processor import GoogleSTTProcessor

# AutoGen 相關
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

class AutoGenVoiceProcessor:
    def __init__(self):
        """初始化 AutoGen 語音處理器"""
        self.model_client = None
        self.stt_processor = None
        self.speech_agent = None
        self.optimization_agent = None
        self.traditional_chinese_agent = None
        self.team = None
        
        # Google Cloud Speech-to-Text 配置
        self.stt_language = os.getenv('GOOGLE_STT_LANGUAGE', 'cmn-Hant-TW')
        
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化所有組件"""
        try:
            # 初始化 Google Cloud Speech-to-Text 處理器
            self.stt_processor = GoogleSTTProcessor()
            
            # 初始化 OpenAI 模型客戶端（用於 AutoGen）
            self.model_client = OpenAIChatCompletionClient(
                model=os.getenv('AUTOGEN_MODEL', 'gpt-4o'),
                api_key=os.getenv('OPENAI_API_KEY'),
                temperature=float(os.getenv('AUTOGEN_TEMPERATURE', '0.7'))
            )
            
            # 建立 SpeechAgent
            self.speech_agent = AssistantAgent(
                name="speech_processor",
                system_message="""你是專業的語音轉文字處理專家。

你的任務：
1. 接收語音轉文字的原始結果
2. 修正可能的語音辨識錯誤
3. 保持原意不變，只修正明顯的錯誤
4. 【重要】必須輸出繁體中文，絕對不能使用簡體中文

注意事項：
- 不要改變原始語意
- 修正標點符號和語法錯誤
- 保持自然的語言風格
- 【強制要求】將所有簡體中文字符轉換為繁體中文
- 使用台灣常用的詞彙和表達方式（如：軟體、網路、資訊、程式等）
- 完成後請說 "SPEECH_PROCESSED"

範例轉換：
- 软件 → 軟體
- 网络 → 網路
- 信息 → 資訊
- 程序 → 程式
- 计算机 → 電腦
- 设置 → 設定
""",
                model_client=self.model_client
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
5. 輸出優化後的中文內容

優化原則：
- 保持原始意思不變
- 改善語法和用詞
- 增強表達的清晰度
- 使用常用詞彙和自然表達
- 適合在訊息中使用的格式
- 完成後請說 "OPTIMIZATION_COMPLETE"

輸出格式：直接輸出優化後的中文文字，不需要額外說明。
""",
                model_client=self.model_client
            )
            
            # 建立 TraditionalChineseAgent（專門負責簡繁轉換）
            self.traditional_chinese_agent = AssistantAgent(
                name="traditional_chinese_converter",
                system_message="""你是專業的簡繁轉換專家。

你的唯一任務：
1. 接收任何中文文字（簡體或繁體）
2. 將所有簡體中文字符轉換為繁體中文
3. 使用台灣常用的繁體中文詞彙
4. 確保輸出100%繁體中文，不能有任何簡體字

轉換規則：
【常用詞彙轉換】
- 软件 → 軟體         - 网络 → 網路         - 信息 → 資訊
- 程序 → 程式         - 计算机 → 電腦       - 设置 → 設定
- 文件 → 檔案         - 文件夹 → 資料夾     - 应用程序 → 應用程式
- 用户 → 使用者       - 界面 → 介面         - 功能 → 功能
- 操作 → 操作         - 处理 → 處理         - 存储 → 儲存
- 下载 → 下載         - 上传 → 上傳         - 连接 → 連線
- 系统 → 系統         - 数据 → 資料         - 资料 → 資料

【字符對照】
们→們 这→這 那→那 个→個 说→說 话→話 时→時 间→間 问→問 题→題
现→現 开→開 结→結 关→關 于→於 对→對 应→應 该→該 处→處 进→進
发→發 变→變 会→會 议→議 讨→討 论→論 计→計 划→劃 设→設 备→備
准→準 确→確 认→認 识→識 实→實 际→際 内→內 数→數 据→據 资→資
经→經 验→驗 学→學 习→習 训→訓 练→練 业→業 务→務 环→環 统→統
网→網 络→絡 连→連 通→通 过→過 检→檢 测→測 试→試 证→證 显→顯
传→傳 递→遞 输→輸 导→導 载→載 储→儲 复→複 制→製 创→創 编→編
删→刪 优→優 简→簡 单→單 杂→雜 难→難 轻→輕 强→強 坏→壞 旧→舊
后→後 里→裡 边→邊 东→東 点→點 区→區

重要提醒：
- 你只負責簡繁轉換，不要改變文字的意思和結構
- 必須保持原文的完整性，只轉換字符
- 完成後請說 "TRADITIONAL_CHINESE_COMPLETE"

輸出格式：直接輸出轉換後的繁體中文，不需要任何解釋或說明。
""",
                model_client=self.model_client
            )
            
            # 建立團隊協作
            termination_condition = (
                MaxMessageTermination(8) |  # 增加到8輪對話確保所有agent都能執行
                TextMentionTermination("TRADITIONAL_CHINESE_COMPLETE")  # 或明確完成標記
            )
            
            self.team = RoundRobinGroupChat(
                [self.speech_agent, self.optimization_agent, self.traditional_chinese_agent],
                termination_condition=termination_condition
            )
            
            logger.info("AutoGen 語音處理器初始化成功 (Google Cloud Speech-to-Text + 三重 Agent 協作)")
            
        except Exception as e:
            logger.error(f"初始化 AutoGen 語音處理器失敗: {str(e)}")
            raise
    
    async def process_audio(self, audio_path: str) -> str:
        """處理語音檔案，返回優化後的文字"""
        try:
            # 1. 語音轉文字 (使用 Google Cloud Speech-to-Text)
            logger.info("開始語音轉文字 (Google Cloud Speech-to-Text)...")
            transcription = await self.stt_processor.transcribe_audio(audio_path)
            logger.info(f"語音轉文字結果: {transcription}")
            
            # 2. AutoGen 三重 Agent 協作優化
            logger.info("開始 AutoGen 三重 Agent 協作...")
            optimized_text = self._optimize_with_agents(transcription)
            
            return optimized_text
            
        except Exception as e:
            logger.error(f"處理語音時發生錯誤: {str(e)}")
            return f"處理失敗: {str(e)}"
    
    def get_stt_info(self) -> dict:
        """獲取 Speech-to-Text 模型資訊"""
        if self.stt_processor:
            return self.stt_processor.get_model_info()
        return {"status": "not_initialized"}
    
    def _optimize_with_agents(self, text: str) -> str:
        """使用 AutoGen 三重 Agent 協作優化文字"""
        try:
            if not os.getenv('ENABLE_TEXT_OPTIMIZATION', 'true').lower() == 'true':
                logger.info("文字優化已停用，但仍會轉換為繁體中文")
                converted_text = self._convert_to_traditional_chinese(text)
                return f"原始文字：{text}\n優化後的文字：{converted_text}"
            
            # 檢查文字長度，太短的文字可能不需要優化
            if len(text.strip()) < 3:
                logger.info("文字太短，但仍會轉換為繁體中文")
                converted_text = self._convert_to_traditional_chinese(text)
                return f"原始文字：{text}\n優化後的文字：{converted_text}"
            
            # 建立初始訊息
            initial_message = f"請處理以下語音轉文字結果：\n\n{text}"
            
            # 執行團隊協作
            logger.info("開始 AutoGen 三重 Agent 協作...")
            logger.info("協作流程: 語音處理 → 內容優化 → 繁體轉換")
            logger.debug(f"初始訊息: {initial_message}")
            
            # 創建新的事件循環來避免衝突
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(self.team.run(task=initial_message))
            finally:
                # 清理事件循環
                try:
                    loop.close()
                except:
                    pass
            
            # 詳細日誌記錄
            logger.debug(f"協作結果類型: {type(result)}")
            if result:
                logger.debug(f"結果屬性: {dir(result)}")
                if hasattr(result, 'messages'):
                    logger.debug(f"訊息數量: {len(result.messages)}")
                    for i, msg in enumerate(result.messages):
                        logger.debug(f"訊息 {i}: 來源={getattr(msg, 'source', 'unknown')}, 內容={msg.content[:100]}...")
            
            # 提取最終結果
            optimized_text = None
            
            if result and hasattr(result, 'messages') and result.messages:
                # 方法1: 優先尋找 traditional_chinese_converter 的輸出（最終繁體結果）
                for message in reversed(result.messages):
                    if (hasattr(message, 'source') and 
                        message.source == 'traditional_chinese_converter'):
                        content = message.content.strip()
                        # 提取 TRADITIONAL_CHINESE_COMPLETE 前的內容作為最終結果
                        if 'TRADITIONAL_CHINESE_COMPLETE' in content:
                            optimized_text = content.replace('TRADITIONAL_CHINESE_COMPLETE', '').strip()
                        elif len(content) > 5:
                            optimized_text = content
                        
                        if optimized_text:
                            logger.info(f"找到繁體轉換結果 (方法1): {optimized_text[:50]}...")
                            break
                
                # 方法2: 如果沒找到，尋找 content_optimizer 的結果
                if not optimized_text:
                    for message in reversed(result.messages):
                        if (hasattr(message, 'source') and 
                            message.source == 'content_optimizer'):
                            content = message.content.strip()
                            # 提取 OPTIMIZATION_COMPLETE 前的內容
                            if 'OPTIMIZATION_COMPLETE' in content:
                                optimized_text = content.replace('OPTIMIZATION_COMPLETE', '').strip()
                            elif len(content) > 5 and content != initial_message:
                                optimized_text = content
                            
                            if optimized_text:
                                logger.info(f"找到優化結果 (方法2): {optimized_text[:50]}...")
                                break
                
                # 方法3: 如果沒找到，尋找 speech_processor 的結果
                if not optimized_text:
                    for message in reversed(result.messages):
                        if (hasattr(message, 'source') and 
                            message.source == 'speech_processor'):
                            content = message.content.strip()
                            # 提取 SPEECH_PROCESSED 前的內容
                            if 'SPEECH_PROCESSED' in content:
                                optimized_text = content.replace('SPEECH_PROCESSED', '').strip()
                            elif len(content) > 5 and content != initial_message:
                                optimized_text = content
                            
                            if optimized_text:
                                logger.info(f"找到語音處理結果 (方法3): {optimized_text[:50]}...")
                                break
                
                # 方法4: 最後備用方案
                if not optimized_text:
                    for message in reversed(result.messages):
                        content = message.content.strip()
                        if (content and 
                            len(content) > 5 and
                            content != initial_message and
                            not content.startswith('請處理以下')):
                            # 清理系統標記
                            content = content.replace('TRADITIONAL_CHINESE_COMPLETE', '').replace('OPTIMIZATION_COMPLETE', '').replace('SPEECH_PROCESSED', '').strip()
                            if content:
                                optimized_text = content
                                logger.info(f"找到備用結果 (方法4): {optimized_text[:50]}...")
                                break
            
            # 如果找到優化結果
            if optimized_text:
                # 清理優化結果
                optimized_text = self._clean_optimized_text(optimized_text)
                result_text = f"原始文字：{text}\n優化後的文字：{optimized_text}"
                logger.info(f"AutoGen 三重 Agent 協作成功完成")
                return result_text
            else:
                logger.warning("AutoGen 三重 Agent 協作未產生有效結果，強制轉換原文為繁體")
                # 即使協作失敗，也要強制轉換為繁體中文
                converted_text = self._convert_to_traditional_chinese(text)
                return f"原始文字：{text}\n優化後的文字：{converted_text}"
            
        except Exception as e:
            logger.error(f"AutoGen 三重 Agent 協作失敗: {str(e)}")
            logger.debug(f"協作失敗詳細錯誤: {e}", exc_info=True)
            # 失敗時也要強制轉換為繁體中文
            converted_text = self._convert_to_traditional_chinese(text)
            return f"原始文字：{text}\n優化後的文字：{converted_text}"
    
    def _clean_optimized_text(self, text: str) -> str:
        """清理優化後的文字"""
        if not text:
            return text
        
        # 移除常見的系統回應
        text = text.replace('TASK_COMPLETE', '').replace('SPEECH_PROCESSED', '')
        
        # 移除多餘的引號和標記
        text = text.strip('"\'`')
        
        # 移除多餘空格和換行
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 強制轉換為繁體中文
        text = self._convert_to_traditional_chinese(text)
        
        # 確保句子結尾有標點符號
        if text and not text[-1] in '。！？.!?':
            text += '。'
        
        return text
    
    def _convert_to_traditional_chinese(self, text: str) -> str:
        """強制轉換簡體中文為繁體中文"""
        if not text:
            return text
            
        try:
            # 安裝並使用 opencc 進行簡繁轉換
            try:
                import opencc
                converter = opencc.OpenCC('s2t')  # 簡體轉繁體
                text = converter.convert(text)
            except ImportError:
                # 如果沒有 opencc，使用基本的字典轉換
                text = self._basic_s2t_convert(text)
                
            return text
        except Exception as e:
            logger.warning(f"繁體轉換失敗: {e}")
            return text
    
    def _basic_s2t_convert(self, text: str) -> str:
        """基本的簡繁轉換"""
        # 常見簡繁對照表
        s2t_dict = {
            '你': '你',
            '们': '們',
            '这': '這',
            '那': '那',
            '个': '個',
            '说': '說',
            '话': '話',
            '时': '時',
            '间': '間',
            '问': '問',
            '题': '題',
            '现': '現',
            '在': '在',
            '开': '開',
            '始': '始',
            '结': '結',
            '束': '束',
            '关': '關',
            '于': '於',
            '对': '對',
            '应': '應',
            '该': '該',
            '处': '處',
            '理': '理',
            '进': '進',
            '行': '行',
            '发': '發',
            '生': '生',
            '变': '變',
            '化': '化',
            '会': '會',
            '议': '議',
            '讨': '討',
            '论': '論',
            '计': '計',
            '划': '劃',
            '设': '設',
            '备': '備',
            '准': '準',
            '确': '確',
            '认': '認',
            '识': '識',
            '实': '實',
            '际': '際',
            '内': '內',
            '容': '容',
            '信': '信',
            '息': '息',
            '数': '數',
            '据': '據',
            '资': '資',
            '料': '料',
            '经': '經',
            '验': '驗',
            '学': '學',
            '习': '習',
            '教': '教',
            '育': '育',
            '训': '訓',
            '练': '練',
            '工': '工',
            '作': '作',
            '业': '業',
            '务': '務',
            '服': '服',
            '环': '環',
            '境': '境',
            '条': '條',
            '件': '件',
            '系': '系',
            '统': '統',
            '网': '網',
            '络': '絡',
            '连': '連',
            '接': '接',
            '通': '通',
            '过': '過',
            '检': '檢',
            '查': '查',
            '测': '測',
            '试': '試',
            '验': '驗',
            '证': '證',
            '明': '明',
            '显': '顯',
            '示': '示',
            '表': '表',
            '达': '達',
            '传': '傳',
            '递': '遞',
            '输': '輸',
            '入': '入',
            '输': '輸',
            '出': '出',
            '导': '導',
            '入': '入',
            '导': '導',
            '出': '出',
            '载': '載',
            '保': '保',
            '存': '存',
            '储': '儲',
            '备': '備',
            '份': '份',
            '复': '複',
            '制': '製',
            '创': '創',
            '建': '建',
            '编': '編',
            '辑': '輯',
            '修': '修',
            '改': '改',
            '删': '刪',
            '除': '除',
            '添': '添',
            '加': '加',
            '插': '插',
            '更': '更',
            '新': '新',
            '升': '升',
            '级': '級',
            '优': '優',
            '化': '化',
            '简': '簡',
            '单': '單',
            '复': '複',
            '杂': '雜',
            '难': '難',
            '易': '易',
            '快': '快',
            '慢': '慢',
            '高': '高',
            '低': '低',
            '大': '大',
            '小': '小',
            '长': '長',
            '短': '短',
            '宽': '寬',
            '窄': '窄',
            '深': '深',
            '浅': '淺',
            '厚': '厚',
            '薄': '薄',
            '重': '重',
            '轻': '輕',
            '强': '強',
            '弱': '弱',
            '多': '多',
            '少': '少',
            '好': '好',
            '坏': '壞',
            '新': '新',
            '旧': '舊',
            '早': '早',
            '晚': '晚',
            '前': '前',
            '后': '後',
            '左': '左',
            '右': '右',
            '上': '上',
            '下': '下',
            '中': '中',
            '间': '間',
            '东': '東',
            '西': '西',
            '南': '南',
            '北': '北',
            '内': '內',
            '外': '外',
            '里': '裡',
            '边': '邊',
            '侧': '側',
            '面': '面',
            '方': '方',
            '向': '向',
            '地': '地',
            '点': '點',
            '位': '位',
            '置': '置',
            '区': '區',
            '域': '域'
        }
        
        # 進行字符替換
        for simplified, traditional in s2t_dict.items():
            text = text.replace(simplified, traditional)
        
        return text
    
    async def optimize_text(self, text: str) -> str:
        """直接優化文字（不經過語音轉換）"""
        return self._optimize_with_agents(text)
    
    def get_status(self) -> dict:
        """獲取處理器狀態"""
        return {
            "stt_language": self.stt_language,
            "autogen_model": os.getenv('AUTOGEN_MODEL', 'gpt-4o'),
            "optimization_enabled": os.getenv('ENABLE_TEXT_OPTIMIZATION', 'true').lower() == 'true',
            "agents_count": 3,
            "agents": ["speech_processor", "content_optimizer", "traditional_chinese_converter"],
            "api_mode": True,
            "google_cloud_stt": True
        } 