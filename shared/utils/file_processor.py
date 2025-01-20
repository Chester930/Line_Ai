import os
import tempfile
import asyncio
from typing import List, Dict, Optional, Tuple, Union, Any
import docx
import pandas as pd
import PyPDF2
from PIL import Image
import speech_recognition as sr
import io
import logging
from datetime import datetime
from shared.database.crud import DocumentCRUD
from shared.database.models import Document
from shared.ai.media_agent import MediaAgent

logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self, db=None):
        self.db = db
        self.temp_dir = tempfile.mkdtemp()
        self.media_agent = MediaAgent()
        self.MAX_FILE_SIZE = 300 * 1024 * 1024  # LINE限制：300MB
        
    async def process_file_with_timeout(
        self,
        file: Union[str, bytes, io.BytesIO],
        file_type: str,
        timeout: int = 25,
        save_to_db: bool = False
    ) -> Dict:
        """處理檔案（帶有超時限制）
        
        Args:
            file: 檔案內容（可以是路徑、bytes或BytesIO）
            file_type: 檔案MIME類型
            timeout: 處理超時時間（秒）
            save_to_db: 是否保存到資料庫
            
        Returns:
            Dict: 處理結果
        """
        try:
            # 檢查檔案大小
            if isinstance(file, (bytes, io.BytesIO)):
                file_size = len(file.getvalue()) if isinstance(file, io.BytesIO) else len(file)
                if not self.check_file_size(file_size):
                    raise ValueError(f"檔案大小超過限制（最大 {self.MAX_FILE_SIZE/1024/1024}MB）")
            
            # 使用 asyncio 處理超時
            result = await asyncio.wait_for(
                self._process_file_async(file, file_type, save_to_db),
                timeout=timeout
            )
            
            return result
            
        except asyncio.TimeoutError:
            logger.error("檔案處理超時")
            return {
                'success': False,
                'error': "處理超時，請稍後再試"
            }
        except Exception as e:
            logger.error(f"處理檔案時發生錯誤：{str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _process_file_async(
        self,
        file: Union[str, bytes, io.BytesIO],
        file_type: str,
        save_to_db: bool = False
    ) -> Dict:
        """非同步處理檔案"""
        try:
            # 將檔案轉換為 BytesIO 對象
            if isinstance(file, str):  # 檔案路徑
                with open(file, 'rb') as f:
                    file_content = io.BytesIO(f.read())
            elif isinstance(file, bytes):
                file_content = io.BytesIO(file)
            else:  # 已經是 BytesIO
                file_content = file
            
            # 提取內容
            content = await self._extract_content_async(file_content, file_type)
            
            if save_to_db and self.db:
                # 保存到資料庫
                file_path = self._save_file(file_content, file_type)
                doc = DocumentCRUD.create_document(
                    self.db,
                    title=f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    content=content['text'],
                    file_path=file_path,
                    file_type=file_type
                )
                return {
                    'success': True,
                    'document_id': doc.id,
                    'content': content
                }
            else:
                return {
                    'success': True,
                    'content': content
                }
                
        except Exception as e:
            raise ValueError(f"處理檔案時發生錯誤：{str(e)}")
    
    async def _extract_content_async(self, file: io.BytesIO, file_type: str) -> Dict:
        """非同步提取檔案內容"""
        try:
            # 圖片檔案
            if file_type.startswith('image/'):
                image = Image.open(file)
                result = await self.media_agent.process_media_async(image, 'image')
                if result['success']:
                    return {'type': 'text', 'text': result['text']}
                else:
                    raise ValueError(result['error'])
            
            # 音訊檔案
            elif file_type.startswith('audio/'):
                result = await self.media_agent.process_media_async(file.getvalue(), 'audio')
                if result['success']:
                    return {'type': 'text', 'text': result['text']}
                else:
                    raise ValueError(result['error'])
            
            # 其他檔案類型處理（同步處理）
            return await asyncio.to_thread(self._extract_content_sync, file, file_type)
            
        except Exception as e:
            raise ValueError(f"提取內容時發生錯誤：{str(e)}")
    
    def _extract_content_sync(self, file: io.BytesIO, file_type: str) -> Dict:
        """同步提取檔案內容"""
        try:
            # 文本檔案
            if file_type == "text/plain":
                text = file.getvalue().decode('utf-8')
                return {'type': 'text', 'text': text}
            
            # PDF 檔案
            elif file_type == "application/pdf":
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return {'type': 'pdf', 'text': text}
            
            # Word 檔案
            elif file_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                doc = docx.Document(file)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                return {'type': 'word', 'text': text}
            
            # Excel 檔案
            elif file_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                df = pd.read_excel(file)
                text = "Excel 檔案內容：\n"
                text += f"表格大小：{df.shape[0]}行 x {df.shape[1]}列\n"
                text += f"欄位名稱：{', '.join(df.columns)}\n"
                text += "\n前5行資料：\n"
                text += df.head().to_string()
                return {'type': 'excel', 'text': text}
            
            else:
                raise ValueError(f"不支援的檔案類型：{file_type}")
            
        except Exception as e:
            raise ValueError(f"處理檔案內容時發生錯誤：{str(e)}")
    
    def check_file_size(self, size: int) -> bool:
        """檢查檔案大小是否符合限制"""
        return size <= self.MAX_FILE_SIZE
    
    def _save_file(self, file: io.BytesIO, file_type: str) -> str:
        """保存檔案到永久存儲"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extension = self._get_file_extension(file_type)
        filename = f"{timestamp}{extension}"
        file_path = os.path.join('data', 'uploads', filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file.getvalue())
            
        return file_path
    
    def _get_file_extension(self, file_type: str) -> str:
        """根據MIME類型獲取檔案副檔名"""
        extensions = {
            'text/plain': '.txt',
            'application/pdf': '.pdf',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'audio/wav': '.wav',
            'audio/mp3': '.mp3'
        }
        return extensions.get(file_type, '')
    
    def __del__(self):
        """清理臨時檔案"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def process_file(self, file) -> Dict[str, Any]:
        """處理上傳的文件"""
        try:
            file_type = file.type
            content = None
            
            # 根據文件類型選擇處理方法
            if file_type == "text/plain":
                content = self._process_txt(file)
            elif file_type == "application/pdf":
                content = self._process_pdf(file)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                content = self._process_docx(file)
            elif file_type == "text/markdown":
                content = self._process_txt(file)  # Markdown 當作純文本處理
            else:
                return {
                    'success': False,
                    'error': f'不支援的文件類型：{file_type}'
                }
            
            if content:
                return {
                    'success': True,
                    'content': content
                }
            else:
                return {
                    'success': False,
                    'error': '無法讀取文件內容'
                }
                
        except Exception as e:
            logger.error(f"處理文件時發生錯誤：{str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_txt(self, file) -> str:
        """處理文本文件"""
        return file.getvalue().decode('utf-8')
    
    def _process_pdf(self, file) -> str:
        """處理 PDF 文件"""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def _process_docx(self, file) -> str:
        """處理 Word 文件"""
        doc = docx.Document(io.BytesIO(file.getvalue()))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text