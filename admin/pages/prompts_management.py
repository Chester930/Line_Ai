import streamlit as st
from shared.utils.role_manager import RoleManager
import json
from typing import Dict, Any

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
        # 基本資訊
        col1, col2 = st.columns(2)
        with col1:
            prompt_id = st.text_input(
                "Prompt ID",
                help="唯一識別碼，例如：greeting_prompt"
            )
            name = st.text_input(
                "名稱",
                help="顯示用的名稱"
            )
        
        with col2:
            category = st.selectbox(
                "類別",
                [
                    "語言設定 (Language)",
                    "語氣風格 (Tone)",
                    "輸出格式 (Output Format)",
                    "寫作風格 (Writing Style)",
                    "MBTI 性格 (MBTI Personality)",
                    "進階性格 (Advanced Personality)"
                ]
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
                # 轉換類別名稱為英文代碼
                category_code = category.split(" (")[1].rstrip(")")
                
                role_manager.add_prompt(
                    prompt_id=prompt_id,
                    name=name,
                    description=description,
                    content=content,
                    category=category_code.lower(),
                    tags=tags
                )
                st.success("✅ Prompt 新增成功")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 新增失敗: {str(e)}")

def show_prompts_list(role_manager: RoleManager):
    """顯示提示詞列表"""
    # 獲取所有角色
    roles = role_manager.get_all_roles()
    
    if not roles:
        st.info("目前沒有任何角色設定")
        return
    
    # 創建分頁 - 修正角色數據的訪問方式
    tabs = st.tabs([role['name'] for role in roles])  # 使用字典訪問
    
    # 顯示每個角色的提示詞
    for role, tab in zip(roles, tabs):
        with tab:
            show_role_prompts(role_manager, role)

def show_role_prompts(role_manager: RoleManager, role: Dict[str, Any]):
    """顯示單個角色的提示詞"""
    # 顯示當前提示詞
    st.subheader(f"當前提示詞 - {role['name']}")  # 使用字典訪問
    current_prompt = st.text_area(
        "系統提示詞",
        value=role['prompt'],  # 使用字典訪問
        height=200,
        key=f"prompt_{role['id']}"  # 使用字典訪問
    )
    
    # 顯示設定
    st.subheader("模型設定")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=role.get('settings', {}).get('temperature', 0.7),
            step=0.1,
            key=f"temp_{role['id']}"
        )
    
    with col2:
        top_p = st.slider(
            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=role.get('settings', {}).get('top_p', 0.9),
            step=0.1,
            key=f"top_p_{role['id']}"
        )
    
    with col3:
        max_tokens = st.number_input(
            "最大 Tokens",
            min_value=100,
            max_value=4000,
            value=role.get('settings', {}).get('max_tokens', 2000),
            step=100,
            key=f"tokens_{role['id']}"
        )
    
    # 保存按鈕
    if st.button("保存設定", key=f"save_{role['id']}"):
        # 更新設定
        updated_settings = {
            'temperature': temperature,
            'top_p': top_p,
            'max_tokens': max_tokens
        }
        
        # 保存更新
        if role_manager.update_role(
            role['id'],
            prompt=current_prompt,
            settings=updated_settings
        ):
            st.success("✅ 設定已更新")
            st.rerun()
        else:
            st.error("❌ 更新失敗")

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
                
                st.success(f"✅ 成功匯入 {success_count} 個 Prompts")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 匯入失敗: {str(e)}") 