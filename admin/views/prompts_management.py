import streamlit as st
from shared.utils.role_manager import RoleManager
import json
import uuid

def show_page():
    """顯示共用提示詞管理頁面"""
    st.header("共用 Prompts 管理")
    
    role_manager = RoleManager()
    
    # 定義類別映射
    category_mapping = {
        "語言設定 (Language)": "language",
        "語氣風格 (Tone)": "tone",
        "輸出格式 (Output Format)": "output_format",
        "寫作風格 (Writing Style)": "writing_style",
        "MBTI 性格 (MBTI Personality)": "mbti",
        "進階性格 (Advanced Personality)": "personality"
    }
    
    # 新增提示詞
    with st.expander("➕ 新增提示詞", expanded=False):
        with st.form("add_prompt"):
            category = st.selectbox(
                "類別",
                options=list(category_mapping.keys())
            )
            
            description = st.text_input(
                "描述",
                help="簡短描述這個提示詞的用途"
            )
            
            content = st.text_area(
                "內容",
                help="提示詞的具體內容"
            )
            
            if st.form_submit_button("新增"):
                if description and content:
                    en_category = category_mapping[category]
                    try:
                        role_manager.add_prompt(
                            category=en_category,
                            description=description,
                            content=content
                        )
                        st.success("✅ 提示詞新增成功！")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"❌ 新增失敗：{str(e)}")
                else:
                    st.warning("⚠️ 請填寫所有必要欄位")
    
    # 顯示分類標籤
    tabs = st.tabs(list(category_mapping.keys()))
    
    for tab, (zh_category, en_category) in zip(tabs, category_mapping.items()):
        with tab:
            prompts = role_manager.get_prompts_by_category(en_category)
            if prompts:
                for prompt_id, data in prompts.items():
                    with st.expander(f"{data['description']}", expanded=False):
                        st.code(data['content'], language="markdown")
                        col1, col2, col3 = st.columns([2,2,1])
                        with col1:
                            st.write(f"使用次數：{data.get('usage_count', 0)}")
                        with col2:
                            st.write(f"最後更新：{data.get('updated_at', '無記錄')}")
                        with col3:
                            if st.button("刪除", key=f"del_{prompt_id}_{uuid.uuid4()}"):
                                try:
                                    role_manager.delete_prompt(prompt_id)
                                    st.success("✅ 提示詞已刪除")
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"❌ 刪除失敗：{str(e)}")
            else:
                st.info(f"目前沒有 {zh_category} 的提示詞")

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
                if st.button("刪除", key=f"del_{prompt_id}_{uuid.uuid4()}"):
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