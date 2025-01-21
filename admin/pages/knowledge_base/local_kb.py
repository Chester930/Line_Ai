import streamlit as st
from shared.utils.file_processor import FileProcessor
from .kb_utils import display_file_list, show_file_details

def show_local_kb():
    """本地知識庫管理"""
    file_processor = FileProcessor()
    
    # 上傳區域
    st.subheader("上傳文件 (Upload Documents)")
    uploaded_files = st.file_uploader(
        "選擇文件 (Select Files)",
        accept_multiple_files=True,
        type=['txt', 'pdf', 'doc', 'docx', 'csv', 'xlsx']
    )
    
    if uploaded_files:
        for file in uploaded_files:
            with st.spinner(f'處理文件: {file.name}...'):
                result = file_processor.process_file(file)
                if result['success']:
                    st.success(f"成功處理文件: {file.name}")
                else:
                    st.error(f"處理失敗: {result['error']}")
    
    # 顯示文件列表
    display_file_list() 