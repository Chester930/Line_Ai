import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from .document_processor import DocumentProcessor
from .json_converter import JsonConverter

logger = logging.getLogger(__name__)

class BatchProcessor:
    """批量文件處理器"""
    
    def __init__(self, 
                 output_dir: str = "data/json_store",
                 max_workers: int = 5,
                 batch_size: int = 10):
        self.document_processor = DocumentProcessor()
        self.json_converter = JsonConverter()
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.batch_size = batch_size
        
        # 創建輸出目錄
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化進度追踪
        self.progress = {}
    
    async def process_files(self, 
                          file_paths: List[str], 
                          task_id: Optional[str] = None) -> Dict[str, Any]:
        """批量處理文件"""
        if not task_id:
            task_id = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            
        try:
            # 初始化任務進度
            self.progress[task_id] = {
                'total': len(file_paths),
                'processed': 0,
                'succeeded': 0,
                'failed': 0,
                'start_time': datetime.utcnow().isoformat(),
                'status': 'processing',
                'results': []
            }
            
            # 將文件分批處理
            batches = [file_paths[i:i + self.batch_size] 
                      for i in range(0, len(file_paths), self.batch_size)]
            
            # 使用線程池處理每個批次
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for batch in batches:
                    # 創建任務
                    tasks = [
                        self._process_single_file(file_path, task_id)
                        for file_path in batch
                    ]
                    
                    # 等待批次完成
                    await asyncio.gather(*tasks)
            
            # 更新任務狀態
            self.progress[task_id]['status'] = 'completed'
            self.progress[task_id]['end_time'] = datetime.utcnow().isoformat()
            
            # 生成報告
            report = self._generate_report(task_id)
            
            return report
            
        except Exception as e:
            logger.error(f"批量處理失敗: {str(e)}")
            self.progress[task_id]['status'] = 'failed'
            self.progress[task_id]['error'] = str(e)
            raise
    
    async def _process_single_file(self, file_path: str, task_id: str) -> None:
        """處理單個文件"""
        try:
            # 處理文件
            file_info = self.document_processor.process_file(file_path)
            
            # 轉換為 JSON
            json_doc = self.json_converter.convert_to_json(file_info)
            
            # 保存 JSON 文件
            output_path = self._save_json(json_doc, file_path)
            
            # 更新進度
            self._update_progress(task_id, True, {
                'file_path': file_path,
                'output_path': output_path,
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"處理文件失敗 {file_path}: {str(e)}")
            self._update_progress(task_id, False, {
                'file_path': file_path,
                'status': 'failed',
                'error': str(e)
            })
    
    def _save_json(self, json_doc: Dict[str, Any], original_file_path: str) -> str:
        """保存 JSON 文件"""
        # 生成輸出文件名
        file_name = Path(original_file_path).stem
        output_path = os.path.join(
            self.output_dir,
            f"{file_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        # 保存文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_doc, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def _update_progress(self, 
                        task_id: str, 
                        success: bool, 
                        result: Dict[str, Any]) -> None:
        """更新處理進度"""
        progress = self.progress[task_id]
        progress['processed'] += 1
        
        if success:
            progress['succeeded'] += 1
        else:
            progress['failed'] += 1
            
        progress['results'].append(result)
    
    def _generate_report(self, task_id: str) -> Dict[str, Any]:
        """生成處理報告"""
        progress = self.progress[task_id]
        
        return {
            'task_id': task_id,
            'status': progress['status'],
            'statistics': {
                'total': progress['total'],
                'processed': progress['processed'],
                'succeeded': progress['succeeded'],
                'failed': progress['failed']
            },
            'timing': {
                'start_time': progress['start_time'],
                'end_time': progress.get('end_time'),
                'duration': (
                    datetime.fromisoformat(progress['end_time']) -
                    datetime.fromisoformat(progress['start_time'])
                ).total_seconds() if progress.get('end_time') else None
            },
            'results': progress['results']
        }
    
    def get_progress(self, task_id: str) -> Dict[str, Any]:
        """獲取處理進度"""
        return self.progress.get(task_id, {})
        
    def clean_up(self, task_id: str) -> None:
        """清理任務數據"""
        if task_id in self.progress:
            del self.progress[task_id]
