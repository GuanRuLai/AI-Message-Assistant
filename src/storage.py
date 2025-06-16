"""
用戶資料儲存模組
使用 TinyDB 儲存用戶互動記錄和統計資料
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
from loguru import logger

try:
    from tinydb import TinyDB, Query
    TINYDB_AVAILABLE = True
except ImportError:
    TINYDB_AVAILABLE = False
    logger.warning("⚠️ TinyDB 未安裝，將使用 JSON 檔案儲存")


class UserStorage:
    def __init__(self):
        """初始化用戶資料儲存"""
        self.db_path = Path('tinydb') / 'user_data.json'
        self.db_path.parent.mkdir(exist_ok=True)
        
        if TINYDB_AVAILABLE:
            self.db = TinyDB(str(self.db_path))
            self.users_table = self.db.table('users')
            self.interactions_table = self.db.table('interactions')
            logger.info("✅ TinyDB 用戶資料儲存已初始化")
        else:
            self.db = None
            self.json_file = self.db_path.parent / 'user_data_fallback.json'
            self._init_json_storage()
            logger.info("✅ JSON 檔案用戶資料儲存已初始化")
    
    def _init_json_storage(self):
        """初始化 JSON 檔案儲存"""
        if not self.json_file.exists():
            initial_data = {
                'users': {},
                'interactions': []
            }
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)
    
    def _load_json_data(self) -> dict:
        """載入 JSON 資料"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ 載入 JSON 資料失敗: {e}")
            return {'users': {}, 'interactions': []}
    
    def _save_json_data(self, data: dict):
        """儲存 JSON 資料"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 儲存 JSON 資料失敗: {e}")
    
    def save_interaction(self, user_id: str, original_text: str, optimized_text: str):
        """
        儲存用戶互動記錄
        
        Args:
            user_id: 用戶 ID
            original_text: 原始文字
            optimized_text: 優化後文字
        """
        try:
            timestamp = datetime.now().isoformat()
            
            interaction_data = {
                'user_id': user_id,
                'original_text': original_text,
                'optimized_text': optimized_text,
                'timestamp': timestamp,
                'text_length': len(original_text),
                'optimization_ratio': len(optimized_text) / len(original_text) if original_text else 1.0
            }
            
            if TINYDB_AVAILABLE and self.db:
                # 使用 TinyDB 儲存
                self.interactions_table.insert(interaction_data)
                self._update_user_stats_tinydb(user_id, timestamp)
            else:
                # 使用 JSON 檔案儲存
                data = self._load_json_data()
                data['interactions'].append(interaction_data)
                self._update_user_stats_json(data, user_id, timestamp)
                self._save_json_data(data)
            
            logger.info(f"✅ 已儲存用戶互動記錄: {user_id}")
            
        except Exception as e:
            logger.error(f"❌ 儲存用戶互動記錄失敗: {e}")
    
    def _update_user_stats_tinydb(self, user_id: str, timestamp: str):
        """更新用戶統計（TinyDB）"""
        try:
            User = Query()
            user_record = self.users_table.search(User.user_id == user_id)
            
            if user_record:
                # 更新現有用戶
                user_data = user_record[0]
                user_data['last_use'] = timestamp
                user_data['total_interactions'] += 1
                user_data['audio_count'] += 1  # 假設都是語音互動
                
                self.users_table.update(user_data, User.user_id == user_id)
            else:
                # 新用戶
                new_user = {
                    'user_id': user_id,
                    'first_use': timestamp,
                    'last_use': timestamp,
                    'total_interactions': 1,
                    'audio_count': 1,
                    'text_count': 0
                }
                self.users_table.insert(new_user)
                
        except Exception as e:
            logger.error(f"❌ 更新用戶統計失敗: {e}")
    
    def _update_user_stats_json(self, data: dict, user_id: str, timestamp: str):
        """更新用戶統計（JSON）"""
        try:
            if user_id in data['users']:
                # 更新現有用戶
                user_data = data['users'][user_id]
                user_data['last_use'] = timestamp
                user_data['total_interactions'] += 1
                user_data['audio_count'] += 1
            else:
                # 新用戶
                data['users'][user_id] = {
                    'user_id': user_id,
                    'first_use': timestamp,
                    'last_use': timestamp,
                    'total_interactions': 1,
                    'audio_count': 1,
                    'text_count': 0
                }
                
        except Exception as e:
            logger.error(f"❌ 更新用戶統計失敗: {e}")
    
    def get_user_stats(self, user_id: str) -> Dict:
        """
        獲取用戶統計資料
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            用戶統計資料字典
        """
        try:
            if TINYDB_AVAILABLE and self.db:
                # 使用 TinyDB 查詢
                User = Query()
                user_record = self.users_table.search(User.user_id == user_id)
                
                if user_record:
                    return user_record[0]
                else:
                    return self._get_default_user_stats()
            else:
                # 使用 JSON 檔案查詢
                data = self._load_json_data()
                return data['users'].get(user_id, self._get_default_user_stats())
                
        except Exception as e:
            logger.error(f"❌ 獲取用戶統計失敗: {e}")
            return self._get_default_user_stats()
    
    def _get_default_user_stats(self) -> Dict:
        """獲取預設用戶統計"""
        return {
            'total_interactions': 0,
            'audio_count': 0,
            'text_count': 0,
            'first_use': '未知',
            'last_use': '未知'
        }
    
    def get_user_interactions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        獲取用戶互動記錄
        
        Args:
            user_id: 用戶 ID
            limit: 返回記錄數量限制
            
        Returns:
            用戶互動記錄列表
        """
        try:
            if TINYDB_AVAILABLE and self.db:
                # 使用 TinyDB 查詢
                Interaction = Query()
                interactions = self.interactions_table.search(
                    Interaction.user_id == user_id
                )
                # 按時間排序，返回最新的記錄
                interactions.sort(key=lambda x: x['timestamp'], reverse=True)
                return interactions[:limit]
            else:
                # 使用 JSON 檔案查詢
                data = self._load_json_data()
                user_interactions = [
                    interaction for interaction in data['interactions']
                    if interaction['user_id'] == user_id
                ]
                # 按時間排序，返回最新的記錄
                user_interactions.sort(key=lambda x: x['timestamp'], reverse=True)
                return user_interactions[:limit]
                
        except Exception as e:
            logger.error(f"❌ 獲取用戶互動記錄失敗: {e}")
            return []
    
    def get_all_users_stats(self) -> Dict:
        """
        獲取所有用戶統計
        
        Returns:
            所有用戶統計字典
        """
        try:
            if TINYDB_AVAILABLE and self.db:
                # 使用 TinyDB 查詢
                all_users = self.users_table.all()
                total_users = len(all_users)
                total_interactions = sum(user.get('total_interactions', 0) for user in all_users)
                total_audio = sum(user.get('audio_count', 0) for user in all_users)
                total_text = sum(user.get('text_count', 0) for user in all_users)
            else:
                # 使用 JSON 檔案查詢
                data = self._load_json_data()
                all_users = list(data['users'].values())
                total_users = len(all_users)
                total_interactions = sum(user.get('total_interactions', 0) for user in all_users)
                total_audio = sum(user.get('audio_count', 0) for user in all_users)
                total_text = sum(user.get('text_count', 0) for user in all_users)
            
            return {
                'total_users': total_users,
                'total_interactions': total_interactions,
                'total_audio_processed': total_audio,
                'total_text_processed': total_text,
                'average_interactions_per_user': total_interactions / total_users if total_users > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ 獲取所有用戶統計失敗: {e}")
            return {
                'total_users': 0,
                'total_interactions': 0,
                'total_audio_processed': 0,
                'total_text_processed': 0,
                'average_interactions_per_user': 0
            }
    
    def cleanup_old_interactions(self, days: int = 30):
        """
        清理舊的互動記錄
        
        Args:
            days: 保留天數
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_iso = cutoff_date.isoformat()
            
            if TINYDB_AVAILABLE and self.db:
                # 使用 TinyDB 清理
                Interaction = Query()
                removed_count = len(self.interactions_table.search(
                    Interaction.timestamp < cutoff_iso
                ))
                self.interactions_table.remove(Interaction.timestamp < cutoff_iso)
            else:
                # 使用 JSON 檔案清理
                data = self._load_json_data()
                original_count = len(data['interactions'])
                data['interactions'] = [
                    interaction for interaction in data['interactions']
                    if interaction['timestamp'] >= cutoff_iso
                ]
                removed_count = original_count - len(data['interactions'])
                self._save_json_data(data)
            
            logger.info(f"🧹 已清理 {removed_count} 條過期互動記錄")
            
        except Exception as e:
            logger.error(f"❌ 清理舊互動記錄失敗: {e}")
    
    def export_user_data(self, user_id: str) -> Dict:
        """
        匯出用戶資料
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            用戶完整資料
        """
        try:
            user_stats = self.get_user_stats(user_id)
            user_interactions = self.get_user_interactions(user_id, limit=100)
            
            return {
                'user_stats': user_stats,
                'interactions': user_interactions,
                'export_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 匯出用戶資料失敗: {e}")
            return {}
    
    def close(self):
        """關閉資料庫連接"""
        try:
            if TINYDB_AVAILABLE and self.db:
                self.db.close()
                logger.info("✅ 資料庫連接已關閉")
        except Exception as e:
            logger.error(f"❌ 關閉資料庫連接失敗: {e}") 