"""
語音轉文字模組
使用 Google Cloud Speech-to-Text API 進行語音識別
"""

import os
import asyncio
import json
from typing import Optional
from loguru import logger
from google.cloud import speech
import io


class SpeechProcessor:
    def __init__(self):
        """初始化語音轉文字處理器"""
        self.client = None
        self.language_code = os.getenv('GOOGLE_STT_LANGUAGE', 'cmn-Hant-TW')
        self.model = os.getenv('GOOGLE_STT_MODEL', 'default')
        self.enable_automatic_punctuation = True
        self.enable_word_time_offsets = False
        
        self._initialize_client()
        logger.info("🎤 語音轉文字處理器已初始化")
    
    def _initialize_client(self):
        """初始化 Google Cloud Speech-to-Text 客戶端"""
        try:
            # 除錯：顯示所有相關環境變數
            logger.info("🔍 Google Cloud 認證環境變數檢查:")
            
            credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            credentials_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            logger.info(f"  - GOOGLE_APPLICATION_CREDENTIALS_JSON: {'已設定' if credentials_json else '未設定'}")
            if credentials_json:
                logger.info(f"    * 長度: {len(credentials_json)} 字元")
                logger.info(f"    * 開頭: {credentials_json[:50]}...")
                logger.info(f"    * 結尾: ...{credentials_json[-50:]}")
            
            logger.info(f"  - GOOGLE_APPLICATION_CREDENTIALS: {'已設定' if credentials_file else '未設定'}")
            if credentials_file:
                logger.info(f"    * 內容: {credentials_file[:100]}...")
                logger.info(f"    * 檔案存在: {os.path.exists(credentials_file)}")
            
            # 方法1: 檢查是否有 JSON 格式的認證資訊
            if credentials_json:
                try:
                    import json
                    from google.oauth2 import service_account
                    
                    logger.info("🔄 嘗試解析 JSON 認證...")
                    credentials_dict = json.loads(credentials_json)
                    logger.info(f"✅ JSON 解析成功，包含欄位: {list(credentials_dict.keys())}")
                    
                    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
                    self.client = speech.SpeechClient(credentials=credentials)
                    logger.info("✅ 使用 JSON 認證初始化 Google Speech 客戶端成功")
                    return
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON 格式錯誤: {e}")
                except Exception as e:
                    logger.error(f"❌ JSON 認證失敗: {e}")
            else:
                logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS_JSON 未設定，跳過 JSON 認證")
            
            # 方法2: 檢查認證檔案路徑
            if credentials_file and os.path.exists(credentials_file):
                try:
                    from google.oauth2 import service_account
                    logger.info("🔄 嘗試使用檔案認證...")
                    credentials = service_account.Credentials.from_service_account_file(credentials_file)
                    self.client = speech.SpeechClient(credentials=credentials)
                    logger.info("✅ 使用檔案認證初始化 Google Speech 客戶端成功")
                    return
                except Exception as e:
                    logger.error(f"❌ 檔案認證失敗: {e}")
            else:
                logger.warning("⚠️ 認證檔案不存在或未設定，跳過檔案認證")
            
            # 方法3: 使用預設認證（ADC）
            logger.info("🔄 嘗試使用預設認證（ADC）...")
            try:
                self.client = speech.SpeechClient()
                logger.info("✅ 使用預設認證初始化 Google Speech 客戶端成功")
                return
            except Exception as e:
                logger.error(f"❌ 預設認證失敗: {e}")
            
            # 如果所有方法都失敗，設為 None 但不中斷程式
            logger.error("❌ 所有 Google Cloud 認證方法都失敗，語音轉文字功能將不可用")
            logger.error("💡 請檢查 Railway 環境變數設定:")
            logger.error("   1. 確認變數名稱是 GOOGLE_APPLICATION_CREDENTIALS_JSON")
            logger.error("   2. 確認 JSON 格式正確且壓縮成一行")
            logger.error("   3. 刪除 GOOGLE_APPLICATION_CREDENTIALS 變數（如果有的話）")
            self.client = None
                
        except Exception as e:
            logger.error(f"❌ 初始化 Google Speech 客戶端失敗: {e}")
            self.client = None
    
    def transcribe(self, audio_path: str) -> Optional[str]:
        """
        同步語音轉文字
        
        Args:
            audio_path: 音頻檔案路徑
            
        Returns:
            轉錄文字，失敗時返回 None
        """
        try:
            # 使用 asyncio 運行異步方法
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(self.transcribe_async(audio_path))
                return result
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"❌ 同步語音轉文字失敗: {e}")
            return None
    
    def speech_to_text(self, audio_path: str) -> Optional[str]:
        """
        語音轉文字方法（transcribe 的別名）
        
        Args:
            audio_path: 音頻檔案路徑
            
        Returns:
            轉錄文字，失敗時返回 None
        """
        return self.transcribe(audio_path)
    
    async def transcribe_async(self, audio_path: str) -> Optional[str]:
        """
        異步語音轉文字
        
        Args:
            audio_path: 音頻檔案路徑
            
        Returns:
            轉錄文字，失敗時返回 None
        """
        try:
            if not self.client:
                logger.error("❌ Google Speech 客戶端未初始化")
                return None
            
            logger.info(f"🎤 開始語音轉文字: {audio_path}")
            
            # 讀取音頻檔案
            with io.open(audio_path, "rb") as audio_file:
                content = audio_file.read()
            
            # 配置音頻
            audio = speech.RecognitionAudio(content=content)
            
            # 配置識別參數
            config = speech.RecognitionConfig(
                encoding=self._detect_encoding(audio_path),
                sample_rate_hertz=16000,  # 預設採樣率
                language_code=self.language_code,
                model=self.model,
                enable_automatic_punctuation=self.enable_automatic_punctuation,
                enable_word_time_offsets=self.enable_word_time_offsets,
                audio_channel_count=1,  # 單聲道
                use_enhanced=True,  # 使用增強模型
            )
            
            # 執行語音識別
            response = self.client.recognize(config=config, audio=audio)
            
            # 處理結果
            if not response.results:
                logger.warning("⚠️ 語音識別無結果")
                return None
            
            # 取得最佳識別結果
            transcription = ""
            for result in response.results:
                if result.alternatives:
                    transcription += result.alternatives[0].transcript
                    logger.info(f"🎯 識別信心度: {result.alternatives[0].confidence:.2f}")
            
            if transcription:
                logger.info(f"✅ 語音轉文字成功: {transcription}")
                return transcription.strip()
            else:
                logger.warning("⚠️ 語音識別結果為空")
                return None
                
        except Exception as e:
            logger.error(f"❌ 語音轉文字失敗: {e}")
            return None
    
    def _detect_encoding(self, audio_path: str) -> speech.RecognitionConfig.AudioEncoding:
        """
        根據檔案副檔名檢測音頻編碼格式
        
        Args:
            audio_path: 音頻檔案路徑
            
        Returns:
            音頻編碼格式
        """
        file_extension = audio_path.lower().split('.')[-1]
        
        encoding_map = {
            'm4a': speech.RecognitionConfig.AudioEncoding.MP3,  # M4A 使用 MP3 編碼
            'mp3': speech.RecognitionConfig.AudioEncoding.MP3,
            'wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
            'flac': speech.RecognitionConfig.AudioEncoding.FLAC,
            'ogg': speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            'webm': speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        }
        
        encoding = encoding_map.get(file_extension, speech.RecognitionConfig.AudioEncoding.MP3)
        logger.info(f"🔍 檢測到音頻編碼: {file_extension} -> {encoding}")
        
        return encoding
    
    def transcribe_long_audio(self, audio_path: str) -> Optional[str]:
        """
        長音頻轉文字（使用異步識別）
        
        Args:
            audio_path: 音頻檔案路徑
            
        Returns:
            轉錄文字，失敗時返回 None
        """
        try:
            if not self.client:
                logger.error("❌ Google Speech 客戶端未初始化")
                return None
            
            logger.info(f"🎤 開始長音頻轉文字: {audio_path}")
            
            # 上傳到 Google Cloud Storage（這裡簡化處理）
            # 實際應用中需要先上傳到 GCS
            with io.open(audio_path, "rb") as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            
            config = speech.RecognitionConfig(
                encoding=self._detect_encoding(audio_path),
                sample_rate_hertz=16000,
                language_code=self.language_code,
                model=self.model,
                enable_automatic_punctuation=self.enable_automatic_punctuation,
                enable_word_time_offsets=self.enable_word_time_offsets,
            )
            
            # 使用長音頻識別
            operation = self.client.long_running_recognize(config=config, audio=audio)
            
            logger.info("⏳ 等待長音頻識別完成...")
            response = operation.result(timeout=300)  # 5分鐘超時
            
            # 處理結果
            transcription = ""
            for result in response.results:
                if result.alternatives:
                    transcription += result.alternatives[0].transcript + " "
            
            if transcription:
                logger.info(f"✅ 長音頻轉文字成功")
                return transcription.strip()
            else:
                logger.warning("⚠️ 長音頻識別結果為空")
                return None
                
        except Exception as e:
            logger.error(f"❌ 長音頻轉文字失敗: {e}")
            return None
    
    def get_supported_languages(self) -> list:
        """
        獲取支援的語言列表
        
        Returns:
            支援的語言代碼列表
        """
        return [
            'cmn-Hant-TW',  # 繁體中文（台灣）
            'cmn-Hans-CN',  # 簡體中文（中國）
            'en-US',        # 英語（美國）
            'ja-JP',        # 日語
            'ko-KR',        # 韓語
        ]
    
    def get_model_info(self) -> dict:
        """
        獲取模型資訊
        
        Returns:
            模型資訊字典
        """
        return {
            'language_code': self.language_code,
            'model': self.model,
            'automatic_punctuation': self.enable_automatic_punctuation,
            'word_time_offsets': self.enable_word_time_offsets,
            'client_initialized': self.client is not None
        }
    
    def test_connection(self) -> bool:
        """
        測試 Google Cloud Speech API 連接
        
        Returns:
            連接是否成功
        """
        try:
            if not self.client:
                return False
            
            # 創建一個簡單的測試請求
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=self.language_code,
            )
            
            # 使用空音頻測試（這會失敗但能測試連接）
            audio = speech.RecognitionAudio(content=b"")
            
            try:
                self.client.recognize(config=config, audio=audio)
            except Exception:
                # 預期會失敗，但如果能到達這裡說明連接正常
                pass
            
            logger.info("✅ Google Speech API 連接測試成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ Google Speech API 連接測試失敗: {e}")
            return False 