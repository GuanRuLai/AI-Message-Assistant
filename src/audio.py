"""
音頻處理模組
負責下載和處理 LINE 語音檔案
"""

import os
import tempfile
import requests
from pathlib import Path
from typing import Optional
from loguru import logger


class AudioProcessor:
    def __init__(self):
        """初始化音頻處理器"""
        self.supported_formats = ['.m4a', '.wav', '.mp3', '.ogg']
        logger.info("🎵 音頻處理器已初始化")
    
    def download_audio(self, line_bot_api, message_id: str, temp_dir: Path) -> Optional[str]:
        """
        從 LINE 下載語音檔案
        
        Args:
            line_bot_api: LINE Bot API 實例
            message_id: 語音訊息 ID
            temp_dir: 臨時檔案目錄
            
        Returns:
            下載的檔案路徑，失敗時返回 None
        """
        try:
            logger.info(f"📥 開始下載語音檔案: {message_id}")
            
            # 獲取語音內容 (v3 API)
            message_content = line_bot_api.get_message_content(message_id)
            
            # 創建臨時檔案
            temp_file = temp_dir / f"audio_{message_id}.m4a"
            
            # 寫入檔案
            with open(temp_file, 'wb') as f:
                for chunk in message_content.iter_content():
                    f.write(chunk)
            
            # 檢查檔案大小
            file_size = os.path.getsize(temp_file)
            logger.info(f"📊 語音檔案大小: {file_size} bytes")
            
            if file_size == 0:
                logger.error("❌ 下載的語音檔案為空")
                self.cleanup_file(str(temp_file))
                return None
            
            logger.info(f"✅ 語音檔案下載成功: {temp_file}")
            return str(temp_file)
            
        except Exception as e:
            logger.error(f"❌ 下載語音檔案失敗: {e}")
            return None
    
    def convert_audio_format(self, input_path: str, output_format: str = 'wav') -> Optional[str]:
        """
        轉換音頻格式（如果需要）
        
        Args:
            input_path: 輸入檔案路徑
            output_format: 輸出格式
            
        Returns:
            轉換後的檔案路徑，失敗時返回 None
        """
        try:
            from pydub import AudioSegment
            
            logger.info(f"🔄 轉換音頻格式: {input_path} -> {output_format}")
            
            # 載入音頻檔案
            audio = AudioSegment.from_file(input_path)
            
            # 生成輸出檔案路徑
            input_path_obj = Path(input_path)
            output_path = input_path_obj.parent / f"{input_path_obj.stem}.{output_format}"
            
            # 導出為指定格式
            audio.export(str(output_path), format=output_format)
            
            logger.info(f"✅ 音頻格式轉換成功: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.warning("⚠️ pydub 未安裝，跳過格式轉換")
            return input_path
        except Exception as e:
            logger.error(f"❌ 音頻格式轉換失敗: {e}")
            return None
    
    def get_audio_info(self, file_path: str) -> dict:
        """
        獲取音頻檔案資訊
        
        Args:
            file_path: 音頻檔案路徑
            
        Returns:
            音頻資訊字典
        """
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(file_path)
            
            return {
                'duration': len(audio) / 1000.0,  # 秒
                'channels': audio.channels,
                'sample_rate': audio.frame_rate,
                'format': Path(file_path).suffix.lower(),
                'file_size': os.path.getsize(file_path)
            }
            
        except ImportError:
            # 如果沒有 pydub，返回基本資訊
            return {
                'file_size': os.path.getsize(file_path),
                'format': Path(file_path).suffix.lower()
            }
        except Exception as e:
            logger.error(f"❌ 獲取音頻資訊失敗: {e}")
            return {}
    
    def validate_audio_file(self, file_path: str) -> bool:
        """
        驗證音頻檔案是否有效
        
        Args:
            file_path: 音頻檔案路徑
            
        Returns:
            檔案是否有效
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"❌ 音頻檔案不存在: {file_path}")
                return False
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                logger.error(f"❌ 音頻檔案為空: {file_path}")
                return False
            
            # 檢查檔案格式
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                logger.warning(f"⚠️ 不支援的音頻格式: {file_ext}")
            
            logger.info(f"✅ 音頻檔案驗證通過: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 音頻檔案驗證失敗: {e}")
            return False
    
    def cleanup_file(self, file_path: str):
        """
        清理臨時檔案
        
        Args:
            file_path: 要清理的檔案路徑
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🗑️ 已清理臨時檔案: {file_path}")
        except Exception as e:
            logger.warning(f"⚠️ 清理臨時檔案失敗: {e}")
    
    def cleanup_directory(self, directory: Path, max_age_hours: int = 24):
        """
        清理過期的臨時檔案
        
        Args:
            directory: 要清理的目錄
            max_age_hours: 檔案最大保留時間（小時）
        """
        try:
            import time
            
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in directory.glob("audio_*"):
                if file_path.is_file():
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        self.cleanup_file(str(file_path))
                        
            logger.info(f"🧹 已清理過期檔案: {directory}")
            
        except Exception as e:
            logger.warning(f"⚠️ 清理目錄失敗: {e}") 