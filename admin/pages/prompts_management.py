import streamlit as st
from shared.utils.role_manager import RoleManager
import json

def show_page():
    """Prompts 管理頁面"""
    st.header("共用 Prompts 管理")
    
    role_manager = RoleManager()
    
    # 新增 Prompt
    with st.expander("新增 Prompt", expanded=True):
        show_add_prompt_form(role_manager)
    
    # 現有 Prompts 列表
    st.subheader("現有 Prompts")
    show_prompts_list(role_manager)
    
    # 匯入/匯出功能
    show_import_export(role_manager)

def show_add_prompt_form(role_manager: RoleManager):
    """顯示新增 Prompt 表單"""
    with st.form("add_prompt_form"):
        prompt_id = st.text_input(
            "Prompt ID",
            help="唯一識別碼，例如：greeting_prompt"
        )
        
        name = st.text_input(
            "名稱",
            help="顯示用的名稱"
        )
        
        description = st.text_area(
            "描述",
            help="Prompt 的用途說明"
        )
        
        content = st.text_area(
            "內容",
            height=200,
            help="Prompt 的實際內容"
        )
        
        # 標籤
        tags = st.multiselect(
            "標籤",
            options=["一般", "客服", "專業", "創意", "其他"],
            default=["一般"]
        )
        
        if st.form_submit_button("新增"):
            if not all([prompt_id, name, content]):
                st.error("請填寫必要欄位")
                return
            
            try:
                role_manager.add_prompt(
                    prompt_id=prompt_id,
                    name=name,
                    description=description,
                    content=content,
                    tags=tags
                )
                st.success("Prompt 新增成功")
                st.rerun()
            except Exception as e:
                st.error(f"新增失敗: {str(e)}")

def show_prompts_list(role_manager: RoleManager):
    """顯示現有 Prompts 列表"""
    prompts = role_manager.get_available_prompts()
    
    if not prompts:
        st.info("目前沒有共用 Prompts")
        return
    
    for prompt_id, prompt in prompts.items():
        with st.expander(f"{prompt['name']} ({prompt_id})", expanded=False):
            col1, col2 = st.columns([3,1])
            
            with col1:
                st.write(f"描述：{prompt['description']}")
                st.write(f"標籤：{', '.join(prompt['tags'])}")
                st.text_area(
                    "內容預覽",
                    value=prompt['content'],
                    height=100,
                    disabled=True
                )
            
            with col2:
                if st.button("刪除", key=f"del_{prompt_id}"):
                    if role_manager.delete_prompt(prompt_id):
                        st.success("已刪除")
                        st.rerun()
                    else:
                        st.error("刪除失敗")

def show_import_export(role_manager: RoleManager):
    """顯示匯入/匯出功能"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("匯出 Prompts")
        if st.button("匯出為 JSON"):
            prompts = role_manager.get_available_prompts()
            if prompts:
                json_str = json.dumps(prompts, ensure_ascii=False, indent=2)
                st.download_button(
                    "下載 JSON 檔案",
                    json_str,
                    "prompts.json",
                    "application/json"
                )
            else:
                st.warning("沒有可匯出的 Prompts")
    
    with col2:
        st.subheader("匯入 Prompts")
        uploaded_file = st.file_uploader(
            "選擇 JSON 檔案",
            type=['json']
        )
        
        if uploaded_file:
            try:
                content = json.loads(uploaded_file.getvalue())
                success_count = 0
                for prompt_id, prompt in content.items():
                    if role_manager.add_prompt(
                        prompt_id=prompt_id,
                        **prompt
                    ):
                        success_count += 1
                
                st.success(f"成功匯入 {success_count} 個 Prompts")
                st.rerun()
            except Exception as e:
                st.error(f"匯入失敗: {str(e)}") 