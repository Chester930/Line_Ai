from .database import get_db
from .models import Document, User, UserSetting
from datetime import datetime

def create_initial_data():
    db = next(get_db())
    try:
        # 創建測試文檔
        test_doc = Document(
            title="測試文檔",
            content="這是一個測試文檔的內容。",
            file_type="text",
            embedding_status="pending",
            created_at=datetime.utcnow()
        )
        db.add(test_doc)
        db.commit()
        
    except Exception as e:
        print(f"初始化數據失敗: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_data()