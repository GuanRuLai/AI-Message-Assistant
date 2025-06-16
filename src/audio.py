"""
音訊處理模組
支援 LINE Bot SDK v3 和各種音訊格式
"""

import os
import tempfile
import requests
from pathlib import Path
from typing import Optional
from loguru import logger

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ pydub 未安裝，音訊轉換功能受限")
    PYDUB_AVAILABLE = False


class AudioProcessor:
    def __init__(self):
        """初始化音訊處理器"""
        self.supported_formats = ['.m4a', '.mp3', '.wav', '.ogg', '.aac']
        logger.info("🎵 音訊處理器已初始化")
    
    def download_audio(self, messaging_api_blob, message_id: str, output_dir: Path) -> Optional[str]:
        """
        下載 LINE 語音訊息
        
        Args:
            messaging_api_blob: LINE Bot MessagingApiBlob 實例 (v3)
            message_id: 訊息 ID
            output_dir: 輸出目錄
            
        Returns:
            下載的檔案路徑，失敗時返回 None
        """
        try:
            logger.info(f"🔽 開始下載語音檔案: {message_id}")
            
            # 使用 LINE Bot SDK v3 MessagingApiBlob API 獲取音訊內容
            message_content = messaging_api_blob.get_message_content(message_id)
            
            # 創建輸出目錄
            output_dir.mkdir(exist_ok=True)
            
            # 生成檔案路徑（預設為 .m4a 格式）
            audio_path = output_dir / f"audio_{message_id}.m4a"
            
            # 寫入音訊檔案
            with open(audio_path, 'wb') as f:
                for chunk in message_content.iter_content():
                    f.write(chunk)
            
            logger.info(f"✅ 語音檔案下載完成: {audio_path}")
            
            # 轉換為 WAV 格式（如果需要）
            wav_path = self.convert_to_wav(audio_path)
            if wav_path and wav_path != audio_path:
                # 刪除原始檔案，保留 WAV
                self.cleanup_file(audio_path)
                return str(wav_path)
            
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"❌ 下載語音檔案失敗: {e}")
            return None
    
    def convert_to_wav(self, audio_path: str) -> Optional[str]:
        """
        轉換音訊檔案為 WAV 格式
        
        Args:
            audio_path: 原始音訊檔案路徑
            
        Returns:
            WAV 檔案路徑，失敗時返回 None
        """
        try:
            if not PYDUB_AVAILABLE:
                logger.warning("⚠️ pydub 不可用，跳過音訊轉換")
                return audio_path
            
            audio_path = Path(audio_path)
            
            # 如果已經是 WAV 格式，直接返回
            if audio_path.suffix.lower() == '.wav':
                return str(audio_path)
            
            logger.info(f"🔄 轉換音訊格式: {audio_path.name}")
            
            # 載入音訊檔案
            try:
                audio = AudioSegment.from_file(str(audio_path))
            except Exception as e:
                logger.error(f"❌ 無法載入音訊檔案: {e}")
                return audio_path  # 返回原始檔案
            
            # 生成 WAV 檔案路徑
            wav_path = audio_path.with_suffix('.wav')
            
            # 轉換為 WAV 格式（16kHz, 單聲道，適合語音識別）
            audio = audio.set_frame_rate(16000)  # 設定取樣率
            audio = audio.set_channels(1)        # 設定為單聲道
            
            # 匯出為 WAV
            audio.export(str(wav_path), format="wav")
            
            logger.info(f"✅ 音訊轉換完成: {wav_path.name}")
            return str(wav_path)
            
        except Exception as e:
            logger.error(f"❌ 音訊轉換失敗: {e}")
            return audio_path  # 返回原始檔案
    
    def get_audio_info(self, audio_path: str) -> dict:
        """
        獲取音訊檔案資訊
        
        Args:
            audio_path: 音訊檔案路徑
            
        Returns:
            音訊資訊字典
        """
        try:
            if not PYDUB_AVAILABLE:
                file_path = Path(audio_path)
                return {
                    'filename': file_path.name,
                    'size': file_path.stat().st_size,
                    'format': file_path.suffix,
                    'pydub_available': False
                }
            
            audio = AudioSegment.from_file(audio_path)
            file_path = Path(audio_path)
            
            return {
                'filename': file_path.name,
                'size': file_path.stat().st_size,
                'format': file_path.suffix,
                'duration': len(audio) / 1000.0,  # 秒
                'frame_rate': audio.frame_rate,
                'channels': audio.channels,
                'sample_width': audio.sample_width,
                'pydub_available': True
            }
            
        except Exception as e:
            logger.error(f"❌ 獲取音訊資訊失敗: {e}")
            return {'error': str(e)}
    
    def validate_audio_file(self, audio_path: str) -> bool:
        """
        驗證音訊檔案是否有效
        
        Args:
            audio_path: 音訊檔案路徑
            
        Returns:
            是否有效
        """
        try:
            file_path = Path(audio_path)
            
            # 檢查檔案是否存在
            if not file_path.exists():
                logger.error(f"❌ 音訊檔案不存在: {audio_path}")
                return False
            
            # 檢查檔案大小
            file_size = file_path.stat().st_size
            if file_size == 0:
                logger.error(f"❌ 音訊檔案為空: {audio_path}")
                return False
            
            # 檢查檔案格式
            if file_path.suffix.lower() not in self.supported_formats:
                logger.warning(f"⚠️ 不支援的音訊格式: {file_path.suffix}")
            
            # 如果有 pydub，進行更詳細的驗證
            if PYDUB_AVAILABLE:
                try:
                    audio = AudioSegment.from_file(str(audio_path))
                    duration = len(audio) / 1000.0
                    
                    if duration < 0.1:  # 少於 0.1 秒
                        logger.error(f"❌ 音訊檔案太短: {duration}s")
                        return False
                    
                    if duration > 300:  # 超過 5 分鐘
                        logger.warning(f"⚠️ 音訊檔案較長: {duration}s")
                    
                except Exception as e:
                    logger.error(f"❌ 音訊檔案損壞: {e}")
                    return False
            
            logger.info(f"✅ 音訊檔案驗證通過: {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 音訊檔案驗證失敗: {e}")
            return False
    
    def cleanup_file(self, file_path: str) -> bool:
        """
        清理臨時檔案
        
        Args:
            file_path: 要刪除的檔案路徑
            
        Returns:
            是否成功刪除
        """
        try:
            if not file_path:
                return True
            
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"🗑️ 已清理檔案: {path.name}")
                return True
            else:
                logger.info(f"📁 檔案不存在，無需清理: {path.name}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 清理檔案失敗: {e}")
            return False
    
    def cleanup_directory(self, directory: str, max_age_hours: int = 24) -> int:
        """
        清理目錄中的舊檔案
        
        Args:
            directory: 目錄路徑
            max_age_hours: 檔案最大保留時間（小時）
            
        Returns:
            清理的檔案數量
        """
        try:
            from datetime import datetime, timedelta
            
            dir_path = Path(directory)
            if not dir_path.exists():
                return 0
            
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    # 檢查檔案修改時間
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if file_time < cutoff_time:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.info(f"🗑️ 清理舊檔案: {file_path.name}")
                        except Exception as e:
                            logger.error(f"❌ 無法刪除檔案 {file_path.name}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"✅ 共清理 {cleaned_count} 個舊檔案")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ 清理目錄失敗: {e}")
            return 0
    
    def get_processor_info(self) -> dict:
        """獲取處理器資訊"""
        return {
            'pydub_available': PYDUB_AVAILABLE,
            'supported_formats': self.supported_formats,
            'features': [
                '音訊下載',
                '格式轉換' if PYDUB_AVAILABLE else '格式轉換 (受限)',
                '檔案驗證',
                '自動清理'
            ]
        } 