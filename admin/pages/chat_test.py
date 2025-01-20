import streamlit as st
import asyncio
from shared.ai.chat_tester import ChatTester
from shared.utils.role_manager import RoleManager
from shared.ai.model_manager import ModelManager
from shared.utils.file_processor import FileProcessor

def show_page():
    """對話測試頁面"""
    st.header("對話測試")
    
    # 初始化必要的管理器
    chat_tester = ChatTester()
    role_manager = RoleManager()
    model_manager = ModelManager()
    
    # 側邊設定
    with st.sidebar:
        show_test_settings(role_manager, model_manager)
    
    # 主要對話區域
    show_chat_interface(chat_tester)
    
    # 檔案處理區域
    show_file_processing()

def show_test_settings(role_manager: RoleManager, model_manager: ModelManager):
    """顯示測試設定"""
    # 獲取所有角色
    roles = role_manager.get_all_roles()
    
    if not roles:
        st.warning("尚未設定任何角色")
        return
    
    # 轉換為字典格式，方便查找
    roles_dict = {role['id']: role for role in roles}
    
    # 選擇角色
    selected_role_id = st.selectbox(
        "選擇角色",
        options=list(roles_dict.keys()),
        format_func=lambda x: roles_dict[x]['name']
    )
    
    selected_role = roles_dict[selected_role_id]
    
    # 顯示角色設定
    with st.expander("角色設定", expanded=True):
        st.write(f"名稱：{selected_role['name']}")
        st.write(f"提示詞：{selected_role['prompt']}")
        st.write("模型設定：")
        st.json(selected_role['settings'])

def show_chat_interface(chat_tester: ChatTester):
    """顯示對話介面"""
    # 初始化對話歷史
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 顯示對話歷史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 輸入區域
    if prompt := st.chat_input("輸入訊息..."):
        # 添加用戶訊息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 獲取 AI 回應
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    settings = st.session_state.get('chat_settings', {})
                    response = asyncio.run(chat_tester.get_response(
                        prompt,
                        role_id=settings.get('role_id'),
                        model=settings.get('model'),
                        temperature=settings.get('temperature', 0.7),
                        max_tokens=settings.get('max_tokens', 1000),
                        enable_kb=settings.get('enable_kb', True),
                        enable_web=settings.get('enable_web', False)
                    ))
                    st.markdown(response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                except Exception as e:
                    st.error(f"生成回應時發生錯誤: {str(e)}")
    
    # 清除對話按鈕
    if st.button("清除對話"):
        st.session_state.messages = []
        st.rerun()

def show_file_processing():
    """顯示檔案處理區域"""
    st.subheader("檔案處理")
    
    uploaded_file = st.file_uploader(
        "上傳檔案",
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
                    image_description = model_manager.describe_image(content['image'])
                    st.write("圖片描述：", image_description)
                    message = f"這是一張圖片，內容描述如下：\n{image_description}"
                else:
                    message = content.get('text', '無法讀取檔案內容')
                
                # 添加到對話歷史
                st.session_state.messages.append({
                    "role": "user",
                    "content": message
                })
                
                st.success("檔案處理成功！")
                st.rerun()
                
            else:
                st.error(f"檔案處理失敗：{result.get('error', '未知錯誤')}")
                
        except Exception as e:
            st.error(f"處理檔案時發生錯誤：{str(e)}") 