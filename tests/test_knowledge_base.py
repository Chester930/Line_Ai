import unittest
import os
from shared.utils.file_processor import FileProcessor
from shared.ai.knowledge_base import KnowledgeBase
from shared.utils.vector_store import VectorStore
from io import BytesIO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestKnowledgeBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """測試類初始化"""
        logger.info("初始化測試環境...")
        cls.file_processor = FileProcessor()
        cls.knowledge_base = KnowledgeBase()
        cls.vector_store = VectorStore()
        
        # 準備多個測試文件
        cls.test_files = {
            'ai': """
            人工智慧（AI）是電腦科學的一個分支，研究如何實現智慧機器。
            機器學習是人工智慧的一個重要領域，通過數據學習來改進性能。
            深度學習是機器學習的一個子集，使用多層神經網絡進行學習。
            """,
            'python': """
            Python是一種高級程式語言，以簡潔易讀的語法著稱。
            Python支持多種程式設計範式，包括程序式、物件導向和函數式程式設計。
            Python有豐富的標準庫和第三方套件，適合快速開發。
            """
        }
        
        # 創建並處理測試文件
        cls.processed_files = {}
        for name, content in cls.test_files.items():
            test_file = BytesIO(content.encode('utf-8'))
            test_file.name = f"{name}.txt"
            cls.processed_files[name] = test_file
    
    def test_01_file_processing(self):
        """測試文件處理"""
        logger.info("測試文件處理...")
        for name, file in self.processed_files.items():
            with self.subTest(file_name=name):
                result = self.file_processor.process_file(file)
                self.assertTrue(result['success'])
                self.assertIn('content', result)
                self.assertIn('chunks', result)
    
    def test_02_vector_embedding(self):
        """測試向量嵌入"""
        logger.info("測試向量嵌入...")
        test_text = "測試文本"
        embedding = self.vector_store.get_embedding(test_text)
        self.assertIsInstance(embedding, list)
        self.assertTrue(len(embedding) > 0)
    
    def test_03_knowledge_query(self):
        """測試知識庫查詢"""
        logger.info("測試知識庫查詢...")
        
        # 先處理所有文件
        for file in self.processed_files.values():
            self.file_processor.process_file(file)
        
        # 測試不同查詢
        test_queries = [
            ("什麼是機器學習？", "機器學習"),
            ("Python有什麼特點？", "Python"),
            ("深度學習是什麼？", "深度學習")
        ]
        
        for query, expected_term in test_queries:
            with self.subTest(query=query):
                results = self.knowledge_base.query(query)
                self.assertTrue(len(results) > 0)
                combined_content = ' '.join(r['content'].lower() for r in results)
                self.assertIn(expected_term.lower(), combined_content)
    
    def test_04_similarity_search(self):
        """測試相似度搜索"""
        logger.info("測試相似度搜索...")
        query = "程式設計語言"
        results = self.vector_store.search(query)
        self.assertTrue(len(results) > 0)
        self.assertTrue(all('similarity' in r for r in results))

if __name__ == '__main__':
    unittest.main(verbosity=2) 