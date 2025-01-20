import streamlit as st
from shared.utils.role_manager import RoleManager
from shared.database.document_crud import DocumentCRUD
import json

def show_page():
    """角色管理頁面"""
    st.header("角色管理")
    
    role_manager = RoleManager()
    
    # 新增角色
    with st.expander("新增角色", expanded=True):
        show_add_role_form(role_manager)
    
    # 現有角色列表
    st.subheader("現有角色")
    show_roles_list(role_manager)
    
    # 角色匯入/匯出
    show_import_export(role_manager)

def show_add_role_form(role_manager: RoleManager):
    """顯示新增角色表單"""
    with st.form("add_role_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            role_id = st.text_input(
                "角色 ID",
                help="唯一識別碼，例如：customer_service"
            )
            name = st.text_input(
                "名稱",
                help="顯示用的名稱"
            )
        
        with col2:
            category = st.selectbox(
                "類別",
                ["一般", "客服", "專業", "創意"]
            )
            language = st.selectbox(
                "主要語言",
                ["中文", "英文", "日文", "多語言"]
            )
        
        description = st.text_area(
            "描述",
            help="角色的詳細說明"
        )
        
        # 選擇共用 prompts
        st.subheader("選擇共用 Prompts")
        
        # 依類別選擇 Prompts
        categories = {
            "語言設定": "language",
            "語氣風格": "tone",
            "輸出格式": "output_format",
            "寫作風格": "writing_style",
            "MBTI 性格": "mbti",
            "進階性格": "personality"
        }
        
        selected_prompts = {}
        available_prompts = role_manager.get_available_prompts()
        
        for zh_category, en_category in categories.items():
            # 獲取該類別的所有 prompts
            category_prompts = role_manager.get_prompts_by_category(en_category)
            
            if en_category == "mbti":
                # MBTI 性格使用單選
                st.write(f"選擇 {zh_category}：")
                prompt_options = ["預設 (Default)"] + [
                    f"{k} - {v['description']}"
                    for k, v in category_prompts.items()
                ]
                
                selected = st.selectbox(
                    "選擇 MBTI 性格類型",
                    options=prompt_options,
                    key=f"select_{en_category}"
                )
                
                if selected != "預設 (Default)":
                    prompt_id = selected.split(" - ")[0]
                    selected_prompts[en_category] = prompt_id
                    
            elif en_category == "personality":
                # 進階性格使用多選
                st.write(f"選擇{zh_category}（可複選）：")
                prompt_options = [
                    f"{k} - {v['description']}"
                    for k, v in category_prompts.items()
                ]
                
                selected_traits = st.multiselect(
                    "選擇進階性格特徵",
                    options=prompt_options,
                    key=f"select_{en_category}"
                )
                
                if selected_traits:
                    selected_prompts[en_category] = [
                        trait.split(" - ")[0] for trait in selected_traits
                    ]
            else:
                # 其他類別使用單選
                prompt_options = ["預設 (Default)"] + [
                    f"{k} - {v['description']}"
                    for k, v in category_prompts.items()
                ]
                
                selected = st.selectbox(
                    f"選擇{zh_category}",
                    options=prompt_options,
                    key=f"select_{en_category}"
                )
                
                if selected != "預設 (Default)":
                    prompt_id = selected.split(" - ")[0]
                    selected_prompts[en_category] = prompt_id
        
        role_prompt = st.text_area(
            "角色專屬提示詞",
            help="設定角色的特定行為和回應方式"
        )
        
        # 插件設定
        st.subheader("插件設定")
        col1, col2 = st.columns(2)
        
        with col1:
            web_search = st.checkbox(
                "啟用網路搜尋",
                value=False
            )
            
            if web_search:
                web_search_weight = st.slider(
                    "網路搜尋參考權重",
                    0.0, 1.0, 0.3
                )
                max_search_results = st.number_input(
                    "最大搜尋結果數",
                    1, 10, 3
                )
        
        with col2:
            knowledge_base = st.checkbox(
                "啟用知識庫",
                value=False
            )
            
            if knowledge_base:
                kb_weight = st.slider(
                    "知識庫參考權重",
                    0.0, 1.0, 0.5
                )
                
                # 選擇知識庫文件
                documents = DocumentCRUD().get_all_documents()
                if documents:
                    selected_docs = st.multiselect(
                        "選擇文件",
                        options=[doc.id for doc in documents],
                        format_func=lambda x: next(
                            (doc.title for doc in documents if doc.id == x),
                            str(x)
                        )
                    )
        
        if st.form_submit_button("新增角色"):
            try:
                settings = {
                    'web_search': {
                        'enabled': web_search,
                        'weight': web_search_weight if web_search else 0,
                        'max_results': max_search_results if web_search else 3
                    },
                    'knowledge_base': {
                        'enabled': knowledge_base,
                        'weight': kb_weight if knowledge_base else 0,
                        'documents': selected_docs if knowledge_base else []
                    }
                }
                
                if role_manager.create_role(
                    role_id=role_id,
                    name=name,
                    description=description,
                    role_prompt=role_prompt,
                    category=category,
                    language=language,
                    base_prompts=selected_prompts,
                    settings=settings
                ):
                    st.success("✅ 角色創建成功")
                    st.rerun()
                else:
                    st.error("❌ 創建失敗")
            except Exception as e:
                st.error(f"❌ 創建失敗: {str(e)}")

def show_roles_list(role_manager: RoleManager):
    """顯示角色列表"""
    roles = role_manager.get_all_roles()
    
    if not roles:
        st.info("目前沒有任何角色")
        return
    
    for role in roles:
        with st.expander(f"{role['name']} ({role['id']})", expanded=False):
            col1, col2 = st.columns([3,1])
            
            with col1:
                st.text_area(
                    "提示詞",
                    value=role['prompt'],
                    height=150,
                    key=f"prompt_{role['id']}"
                )
                
                st.json(role['settings'])

def show_role_details(role, role_manager: RoleManager):
    """顯示角色詳細資訊"""
    col1, col2 = st.columns([3,1])
    
    with col1:
        st.write(f"描述：{getattr(role, 'description', '無描述')}")
        st.write(f"類別：{getattr(role, 'category', '未分類')}")
        st.write(f"語言：{getattr(role, 'language', '未設定')}")
        
        # 使用 columns 代替嵌套的 expander
        st.subheader("角色 Prompt")
        st.text_area(
            "內容",
            value=getattr(role, 'role_prompt', ''),
            height=100,
            disabled=True,
            key=f"prompt_{role.id}"  # 添加唯一的 key
        )
        
        base_prompts = getattr(role, 'base_prompts', [])
        if base_prompts:
            st.subheader("使用的基礎 Prompts")
            for prompt_id in base_prompts:
                prompt = role_manager.get_prompt(prompt_id)
                if prompt:
                    st.write(f"- {prompt.get('name', prompt_id)}")
    
    with col2:
        if st.button("刪除", key=f"del_role_{role.id}"):
            if role_manager.delete_role(role.id):
                st.success("✅ 已刪除")
                st.rerun()
            else:
                st.error("❌ 刪除失敗")
        
        if st.button("編輯", key=f"edit_role_{role.id}"):
            st.session_state.editing_role = role.id
            st.rerun()

def show_import_export(role_manager: RoleManager):
    """顯示角色匯入/匯出功能"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("匯出角色")
        if st.button("匯出為 JSON"):
            roles = role_manager.export_roles()
            if roles:
                st.download_button(
                    "下載 JSON 檔案",
                    json.dumps(roles, ensure_ascii=False, indent=2),
                    "roles.json",
                    "application/json"
                )
    
    with col2:
        st.subheader("匯入角色")
        uploaded_file = st.file_uploader(
            "選擇 JSON 檔案",
            type=['json']
        )
        
        if uploaded_file:
            try:
                content = json.loads(uploaded_file.getvalue())
                success_count = role_manager.import_roles(content)
                st.success(f"✅ 成功匯入 {success_count} 個角色")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 匯入失敗: {str(e)}")