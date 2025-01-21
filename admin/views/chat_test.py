import streamlit as st
from shared.ai.chat_tester import ChatTester
from shared.config.config import Config

def show_page():
    """對話測試頁面"""
    st.header("對話測試")
    
    # 初始化聊天記錄
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # 設定區域
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 選擇模型
        model = st.selectbox(
            "選擇模型 (Select Model)",
            ["gemini-pro", "gpt-3.5-turbo", "claude-3-sonnet"]
        )
    
    with col2:
        # 臨時參數調整
        st.write("臨時參數調整 (Temporary Settings)")
        temperature = st.slider(
            "溫度 (Temperature)", 
            0.0, 1.0, 
            value=0.7
        )
        top_p = st.slider(
            "Top P",
            0.0, 1.0,
            value=0.9
        )
    
    with col3:
        # 插件設定
        st.write("插件設定 (Plugin Settings)")
        web_search = st.checkbox(
            "網路搜尋 (Web Search)",
            value=False,
            help="啟用網路搜尋功能"
        )
        
        if web_search:
            web_search_weight = st.slider(
                "搜尋參考權重",
                0.0, 1.0,
                value=0.3
            )
        
        knowledge_base = st.checkbox(
            "知識庫 (Knowledge Base)",
            value=False,
            help="啟用知識庫功能"
        )
        
        if knowledge_base:
            kb_weight = st.slider(
                "知識庫參考權重",
                0.0, 1.0,
                value=0.5
            )
    
    # 顯示對話歷史
    for message in st.session_state.chat_history:
        role_icon = "🧑" if message["role"] == "user" else "🤖"
        st.write(f"{role_icon} {message['content']}")
    
    # 文字輸入區
    with st.form(key="chat_form"):
        user_input = st.text_area("輸入訊息 (Enter Message)", height=100)
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.form_submit_button("發送")
        with col2:
            clear_button = st.form_submit_button("清除歷史")
    
    # 處理發送按鈕
    if submit_button and user_input:
        try:
            # 添加用戶訊息到歷史
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # 獲取 AI 回應
            with st.spinner("AI思考中..."):
                chat_tester = ChatTester()
                
                # 準備對話參數
                chat_params = {
                    "temperature": temperature,
                    "top_p": top_p
                }
                
                response = chat_tester.get_response(
                    model=model,
                    messages=st.session_state.chat_history,
                    **chat_params
                )
            
            # 添加 AI 回應到歷史
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # 重新載入頁面以顯示新訊息
            st.experimental_rerun()
            
        except Exception as e:
            st.error(f"發生錯誤：{str(e)}")
    
    # 處理清除按鈕
    if clear_button:
        st.session_state.chat_history = []
        st.experimental_rerun()
    
    # 檔案上傳區域
    st.subheader("檔案處理 (File Processing)")
    uploaded_file = st.file_uploader(
        "上傳檔案 (Upload File)", 
        type=['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg', 'wav', 'mp3']
    )
    
    if uploaded_file:
        try:
            file_processor = FileProcessor()
            result = file_processor.process_file(uploaded_file, save_to_db=False)
            
            if result['success']:
                content = result['content']
                
                if content['type'] == 'image':
                    # 使用 Gemini Vision API 進行圖片描述
                    image_description = chat_tester.describe_image(content['image'])
                    st.write("圖片描述：", image_description)
                    message = f"這是一張圖片，內容描述如下：\n{image_description}"
                else:
                    message = content.get('text', '無法讀取檔案內容')
                
                # 添加到對話歷史
                st.session_state.chat_history.append({"role": "user", "content": message})
                
                # 顯示處理結果
                st.success("檔案處理成功！")
                
            else:
                st.error(f"檔案處理失敗：{result.get('error', '未知錯誤')}")
                
        except Exception as e:
            st.error(f"處理檔案時發生錯誤：{str(e)}") 