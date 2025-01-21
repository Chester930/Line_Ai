import streamlit as st
from shared.database.document_crud import DocumentCRUD
from shared.utils.file_processor import FileProcessor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def show_local_knowledge_base():
    """顯示本地知識庫管理介面"""
    st.header("本地知識庫管理")
    
    doc_crud = DocumentCRUD()
    
    # 創建新知識庫
    with st.expander("➕ 創建新知識庫", expanded=False):
        with st.form("create_knowledge_base"):
            name = st.text_input(
                "知識庫名稱",
                placeholder="例如：產品手冊、客服FAQ",
                help="請輸入知識庫名稱"
            )
            description = st.text_area(
                "知識庫描述",
                placeholder="簡短描述此知識庫的用途和內容",
                help="請輸入知識庫描述"
            )
            
            if st.form_submit_button("創建"):
                if name:
                    try:
                        kb = doc_crud.create_knowledge_base(
                            name=name,
                            description=description,
                            type="local"
                        )
                        st.success(f"✅ 知識庫「{name}」創建成功！")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"❌ 創建失敗：{str(e)}")
                        logger.error(f"Create knowledge base failed: {str(e)}")
                else:
                    st.warning("⚠️ 請輸入知識庫名稱")
    
    # 獲取所有本地知識庫
    knowledge_bases = doc_crud.get_knowledge_bases(type="local")
    
    if not knowledge_bases:
        st.info("📚 目前沒有本地知識庫，請先創建一個新的知識庫")
        return
    
    # 選擇知識庫
    selected_kb = st.selectbox(
        "選擇知識庫",
        options=knowledge_bases,
        format_func=lambda x: f"{x.name} ({len(x.documents)} 份文件)"
    )
    
    if selected_kb:
        st.subheader(f"知識庫：{selected_kb.name}")
        st.write(f"描述：{selected_kb.description}")
        st.write(f"創建時間：{selected_kb.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 文件上傳區域
        with st.expander("📄 上傳文件", expanded=False):
            uploaded_file = st.file_uploader(
                "選擇文件",
                type=['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx'],
                help="支援的格式：TXT、PDF、Word、Excel"
            )
            
            if uploaded_file:
                with st.form("upload_form"):
                    title = st.text_input(
                        "文件標題",
                        value=uploaded_file.name
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        auto_chunk = st.checkbox(
                            "自動分段",
                            value=True,
                            help="自動將文件分割成小段落以優化搜索效果"
                        )
                    with col2:
                        if auto_chunk:
                            chunk_size = st.number_input(
                                "分段大小",
                                min_value=100,
                                max_value=1000,
                                value=500,
                                help="每個段落的最大字符數"
                            )
                    
                    if st.form_submit_button("上傳"):
                        try:
                            # 處理文件內容
                            file_processor = FileProcessor()
                            result = file_processor.process_file(uploaded_file)
                            
                            if result['success']:
                                # 創建文件記錄
                                document = doc_crud.create_document(
                                    knowledge_base_id=selected_kb.id,
                                    title=title,
                                    content=result['content'],
                                    file_type=uploaded_file.type,
                                    file_size=uploaded_file.size
                                )
                                st.success("✅ 文件上傳成功！")
                                st.experimental_rerun()
                            else:
                                st.error(f"❌ 文件處理失敗：{result.get('error', '未知錯誤')}")
                        except Exception as e:
                            st.error(f"❌ 上傳失敗：{str(e)}")
                            logger.error(f"Upload document failed: {str(e)}")
        
        # 文件列表
        st.subheader("文件列表")
        if not selected_kb.documents:
            st.info("📝 此知識庫還沒有任何文件")
        else:
            for doc in selected_kb.documents:
                with st.expander(f"{doc.title} ({doc.file_type})", expanded=False):
                    col1, col2, col3 = st.columns([2,2,1])
                    with col1:
                        st.write(f"上傳時間：{doc.created_at.strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"處理狀態：{doc.embedding_status}")
                    with col2:
                        st.write(f"檔案大小：{doc.file_size/1024:.1f} KB")
                        chunks = doc_crud.get_document_chunks(doc.id)
                        st.write(f"分段數量：{len(chunks) if chunks else 0}")
                    with col3:
                        if st.button("刪除", key=f"del_{doc.id}"):
                            if doc_crud.delete_document(doc.id):
                                st.success("✅ 文件已刪除")
                                st.experimental_rerun()
                            else:
                                st.error("❌ 刪除失敗") 