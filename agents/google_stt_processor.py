"""
Google Cloud Speech-to-Text 處理器
使用 Google Cloud Speech-to-Text API 進行語音轉文字
"""

import os
import asyncio
import tempfile
from typing import Optional
from loguru import logger
from google.cloud import speech
import io


class GoogleSTTProcessor:
    def __init__(self):
        """初始化 Google Cloud Speech-to-Text 處理器"""
        self.client = None
        self.language_code = os.getenv('GOOGLE_STT_LANGUAGE', 'cmn-Hant-TW')  # 繁體中文台灣
        self.model = os.getenv('GOOGLE_STT_MODEL', 'default')  # 可選: default, command_and_search
        self.enable_automatic_punctuation = True
        self.enable_word_time_offsets = False
        
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化 Google Cloud Speech-to-Text 客戶端"""
        try:
            # 檢查是否有 JSON 格式的認證環境變數 (用於 Railway 部署)
            credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            if credentials_json:
                import json
                from google.oauth2 import service_account
                
                # 解析 JSON 認證
                credentials_info = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
                
                # 使用認證初始化客戶端
                self.client = speech.SpeechClient(credentials=credentials)
                logger.info("使用 JSON 環境變數認證初始化 Google Cloud Speech-to-Text")
            else:
                # 使用預設認證方式 (本地檔案)
                self.client = speech.SpeechClient()
                logger.info("使用預設認證初始化 Google Cloud Speech-to-Text")
            
            logger.info(f"Google Cloud Speech-to-Text 客戶端初始化成功")
            logger.info(f"語言設定: {self.language_code}")
            logger.info(f"模型設定: {self.model}")
            
        except Exception as e:
            logger.error(f"初始化 Google Cloud Speech-to-Text 客戶端失敗: {str(e)}")
            raise
    
    async def transcribe_audio(self, audio_path: str) -> str:
        """
        使用 Google Cloud Speech-to-Text 轉錄音檔
        
        Args:
            audio_path: 音檔路徑
            
        Returns:
            轉錄的文字結果
        """
        try:
            logger.info(f"開始使用 Google Cloud Speech-to-Text 轉錄音檔: {audio_path}")
            
            # 讀取音檔
            with io.open(audio_path, "rb") as audio_file:
                content = audio_file.read()
            
            # 建立音檔物件
            audio = speech.RecognitionAudio(content=content)
            
            # 建立辨識配置
            config = speech.RecognitionConfig(
                encoding=self._detect_encoding(audio_path),
                sample_rate_hertz=self._detect_sample_rate(audio_path),
                language_code=self.language_code,
                model=self.model,
                enable_automatic_punctuation=self.enable_automatic_punctuation,
                enable_word_time_offsets=self.enable_word_time_offsets,
                # 可以設定替代語言（如果需要混合語言支援）
                # alternative_language_codes=["en-US"] if self.language_code.startswith("cmn") else None
            )
            
            logger.info(f"辨識配置: 語言={config.language_code}, 編碼={config.encoding}, 採樣率={config.sample_rate_hertz}")
            
            # 執行語音辨識
            response = self.client.recognize(config=config, audio=audio)
            
            # 提取轉錄結果
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "
                logger.debug(f"辨識結果: {result.alternatives[0].transcript} (信心度: {result.alternatives[0].confidence:.2%})")
            
            transcript = transcript.strip()
            
            if transcript:
                logger.info(f"Google Cloud Speech-to-Text 轉錄成功: {transcript[:100]}...")
                return transcript
            else:
                logger.warning("Google Cloud Speech-to-Text 未能辨識出任何文字")
                return "無法辨識語音內容"
                
        except Exception as e:
            logger.error(f"Google Cloud Speech-to-Text 轉錄失敗: {str(e)}")
            return f"語音轉錄失敗: {str(e)}"
    
    def _detect_encoding(self, audio_path: str) -> speech.RecognitionConfig.AudioEncoding:
        """
        根據檔案副檔名偵測音檔編碼格式
        
        Args:
            audio_path: 音檔路徑
            
        Returns:
            Google Cloud Speech-to-Text 支援的編碼格式
        """
        file_extension = os.path.splitext(audio_path)[1].lower()
        
        encoding_map = {
            '.wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
            '.flac': speech.RecognitionConfig.AudioEncoding.FLAC,
            '.mp3': speech.RecognitionConfig.AudioEncoding.MP3,
            '.m4a': speech.RecognitionConfig.AudioEncoding.MP3,  # M4A 通常可以用 MP3 處理
            '.ogg': speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            '.webm': speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        }
        
        encoding = encoding_map.get(file_extension, speech.RecognitionConfig.AudioEncoding.LINEAR16)
        logger.debug(f"偵測到音檔格式: {file_extension} -> {encoding}")
        
        return encoding
    
    def _detect_sample_rate(self, audio_path: str) -> int:
        """
        偵測音檔採樣率
        
        Args:
            audio_path: 音檔路徑
            
        Returns:
            採樣率 (Hz)
        """
        try:
            # 嘗試使用 pydub 來偵測採樣率
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(audio_path)
                sample_rate = audio.frame_rate
                logger.debug(f"偵測到採樣率: {sample_rate} Hz")
                return sample_rate
            except ImportError:
                logger.warning("pydub 未安裝，使用預設採樣率")
                pass
            
            # 如果無法偵測，使用常見的預設值
            file_extension = os.path.splitext(audio_path)[1].lower()
            
            # 根據檔案格式設定預設採樣率
            if file_extension in ['.wav', '.flac']:
                return 16000  # 常見的語音採樣率
            elif file_extension in ['.mp3', '.m4a']:
                return 44100  # 常見的音樂採樣率
            else:
                return 16000  # 預設值
                
        except Exception as e:
            logger.warning(f"無法偵測採樣率: {e}，使用預設值 16000 Hz")
            return 16000
    
    async def transcribe_audio_with_timestamps(self, audio_path: str) -> dict:
        """
        使用 Google Cloud Speech-to-Text 轉錄音檔並返回時間戳記
        
        Args:
            audio_path: 音檔路徑
            
        Returns:
            包含轉錄文字和時間戳記的字典
        """
        try:
            # 暫時啟用時間戳記
            original_setting = self.enable_word_time_offsets
            self.enable_word_time_offsets = True
            
            logger.info(f"開始使用 Google Cloud Speech-to-Text 轉錄音檔（含時間戳記）: {audio_path}")
            
            # 讀取音檔
            with io.open(audio_path, "rb") as audio_file:
                content = audio_file.read()
            
            # 建立音檔物件
            audio = speech.RecognitionAudio(content=content)
            
            # 建立辨識配置
            config = speech.RecognitionConfig(
                encoding=self._detect_encoding(audio_path),
                sample_rate_hertz=self._detect_sample_rate(audio_path),
                language_code=self.language_code,
                model=self.model,
                enable_automatic_punctuation=self.enable_automatic_punctuation,
                enable_word_time_offsets=True,
            )
            
            # 執行語音辨識
            response = self.client.recognize(config=config, audio=audio)
            
            # 提取轉錄結果和時間戳記
            transcript = ""
            words_with_timestamps = []
            
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "
                
                # 提取單詞時間戳記
                for word in result.alternatives[0].words:
                    start_time = word.start_time.total_seconds()
                    end_time = word.end_time.total_seconds()
                    words_with_timestamps.append({
                        'word': word.word,
                        'start_time': start_time,
                        'end_time': end_time
                    })
            
            transcript = transcript.strip()
            
            # 恢復原始設定
            self.enable_word_time_offsets = original_setting
            
            result = {
                'transcript': transcript,
                'words': words_with_timestamps,
                'language': self.language_code
            }
            
            logger.info(f"Google Cloud Speech-to-Text 轉錄成功（含時間戳記）")
            return result
                
        except Exception as e:
            logger.error(f"Google Cloud Speech-to-Text 轉錄失敗（含時間戳記）: {str(e)}")
            # 恢復原始設定
            self.enable_word_time_offsets = original_setting
            return {
                'transcript': f"語音轉錄失敗: {str(e)}",
                'words': [],
                'language': self.language_code
            }
    
    def get_model_info(self) -> dict:
        """獲取模型資訊"""
        return {
            'provider': 'Google Cloud Speech-to-Text',
            'language_code': self.language_code,
            'model': self.model,
            'automatic_punctuation': self.enable_automatic_punctuation,
            'word_time_offsets': self.enable_word_time_offsets,
            'status': 'ready' if self.client else 'not_initialized'
        }
    
    def set_language(self, language_code: str):
        """設定語言代碼"""
        self.language_code = language_code
        logger.info(f"語言設定已更新為: {language_code}")
    
    def set_model(self, model: str):
        """設定模型"""
        self.model = model
        logger.info(f"模型設定已更新為: {model}") 