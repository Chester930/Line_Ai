import os
from typing import List
import docx
import pandas as pd
import PyPDF2
from shared.database.models import Document

class FileProcessor:
    @staticmethod
    def process_document(document: Document) -> dict:
        """處理上傳的文件，提取文本內容"""
        if not os.path.exists(document.file_path):
            raise FileNotFoundError(f"File not found: {document.file_path}")
            
        if document.file_type == 'pdf':
            return FileProcessor._process_pdf(document.file_path)
        elif document.file_type in ['docx', 'doc']:
            return FileProcessor._process_docx(document.file_path)
        elif document.file_type in ['xlsx', 'xls']:
            return FileProcessor._process_excel(document.file_path)
        else:
            raise ValueError(f"Unsupported file type: {document.file_type}")

    @staticmethod
    def _process_pdf(file_path: str) -> dict:
        """處理 PDF 文件"""
        content = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                content.append(page.extract_text())
        return {'content': '\n'.join(content)}

    @staticmethod
    def _process_docx(file_path: str) -> dict:
        """處理 Word 文件"""
        doc = docx.Document(file_path)
        content = []
        for para in doc.paragraphs:
            if para.text.strip():
                content.append(para.text)
        return {'content': '\n'.join(content)}

    @staticmethod
    def _process_excel(file_path: str) -> dict:
        """處理 Excel 文件"""
        df = pd.read_excel(file_path)
        return {'content': df.to_json(orient='records')} 