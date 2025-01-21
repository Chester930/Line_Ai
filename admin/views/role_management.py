import streamlit as st
from shared.utils.role_manager import RoleManager
from shared.database.document_crud import DocumentCRUD
import json
import uuid

def show_page():
    """顯示角色管理頁面"""
    st.header("角色管理")
    
    st.info("""
    角色管理功能正在維護中...
    
    即將支援的功能：
    - 角色創建和編輯
    - 系統提示詞設定
    - 知識庫關聯
    - 對話參數調整
    """)
    
    role_manager = RoleManager()
    doc_crud = DocumentCRUD()
    
    # 創建新角色
    with st.expander("➕ 創建新角色", expanded=False):
        with st.form("create_role"):
            st.write("請填寫新角色的基本資訊：")
            role_id = st.text_input(
                "角色ID (英文)",
                help="唯一標識符，例如：custom_helper"
            )
            name = st.text_input(
                "角色名稱",
                help="顯示名稱，例如：客服助手"
            )
            description = st.text_area(
                "角色描述",
                help="角色的主要功能和特點"
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
            for zh_cat, en_cat in categories.items():
                st.write(f"**{zh_cat}**")
                prompts = role_manager.get_prompts_by_category(en_cat)
                if prompts:
                    for prompt_id, data in prompts.items():
                        selected_prompts[prompt_id] = st.checkbox(
                            data['description'],
                            key=f"prompt_{prompt_id}_{uuid.uuid4()}"
                        )
            
            # 選擇知識庫
            st.subheader("選擇知識庫")
            knowledge_bases = doc_crud.get_knowledge_bases()
            selected_kbs = {}
            
            if knowledge_bases:
                for kb in knowledge_bases:
                    selected_kbs[kb.id] = st.checkbox(
                        f"{kb.name} ({len(kb.documents)} 份文件)",
                        key=f"kb_{kb.id}"
                    )
            
            if st.form_submit_button("創建角色"):
                if role_id and name:
                    try:
                        # 創建角色
                        role = role_manager.create_role(
                            role_id=role_id,
                            name=name,
                            description=description
                        )
                        
                        # 添加選中的提示詞
                        for prompt_id, selected in selected_prompts.items():
                            if selected:
                                role_manager.add_prompt_to_role(role_id, prompt_id)
                        
                        # 添加選中的知識庫
                        for kb_id, selected in selected_kbs.items():
                            if selected:
                                doc_crud.add_knowledge_base_to_role(role_id, kb_id)
                        
                        st.success("✅ 角色創建成功！")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"❌ 創建失敗：{str(e)}")
                else:
                    st.warning("⚠️ 請填寫必要欄位")
    
    # 顯示現有角色列表
    st.subheader("角色列表")
    roles = role_manager.get_all_roles()
    
    for role in roles:
        with st.expander(f"{role['name']} ({role['role_id']})", expanded=False):
            st.write(f"描述：{role['description']}")
            
            # 顯示使用的提示詞
            st.write("**使用的提示詞：**")
            role_prompts = role_manager.get_role_prompts(role['role_id'])
            for prompt in role_prompts:
                st.write(f"- {prompt['description']}")
            
            # 顯示使用的知識庫
            st.write("**使用的知識庫：**")
            role_kbs = doc_crud.get_role_knowledge_bases(role['role_id'])
            for kb in role_kbs:
                st.write(f"- {kb.name}")
            
            # 刪除角色按鈕
            if st.button("刪除角色", key=f"del_role_{role['role_id']}"):
                try:
                    role_manager.delete_role(role['role_id'])
                    st.success("✅ 角色已刪除")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ 刪除失敗：{str(e)}")

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
        
        role_prompt = st.text_area(
            "角色 Prompt",
            height=200,
            help="定義角色的主要 Prompt"
        )
        
        # 選擇基礎 Prompts
        available_prompts = role_manager.get_available_prompts()
        if available_prompts:
            selected_prompts = st.multiselect(
                "選擇基礎 Prompts",
                options=list(available_prompts.keys()),
                format_func=lambda x: f"{available_prompts[x]['name']} ({x})"
            )
        
        # 進階設定
        st.subheader("進階設定")
        
        col1, col2 = st.columns(2)
        with col1:
            web_search = st.checkbox(
                "啟用網路搜尋",
                value=False
            )
            
            if web_search:
                web_search_weight = st.slider(
                    "搜尋結果權重",
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
                    "知識庫權重",
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
                    st.success("角色創建成功")
                    st.rerun()
                else:
                    st.error("創建失敗")
            except Exception as e:
                st.error(f"創建失敗: {str(e)}")

def show_roles_list(role_manager: RoleManager):
    """顯示現有角色列表"""
    roles = role_manager.list_roles()
    
    if not roles:
        st.info("目前沒有角色")
        return
    
    for role_id, role in roles.items():
        with st.expander(f"{role.name} ({role_id})", expanded=False):
            show_role_details(role, role_manager)

def show_role_details(role, role_manager: RoleManager):
    """顯示角色詳細資訊"""
    col1, col2 = st.columns([3,1])
    
    with col1:
        st.write(f"描述：{role.description}")
        st.write(f"類別：{role.category}")
        st.write(f"語言：{role.language}")
        
        with st.expander("角色 Prompt"):
            st.text_area(
                "內容",
                value=role.role_prompt,
                height=100,
                disabled=True
            )
        
        if role.base_prompts:
            with st.expander("使用的基礎 Prompts"):
                for prompt_id in role.base_prompts:
                    prompt = role_manager.get_prompt(prompt_id)
                    if prompt:
                        st.write(f"- {prompt['name']}")
    
    with col2:
        if st.button("刪除", key=f"del_role_{role_id}"):
            if role_manager.delete_role(role_id):
                st.success("已刪除")
                st.rerun()
            else:
                st.error("刪除失敗")
        
        if st.button("編輯", key=f"edit_role_{role_id}"):
            st.session_state.editing_role = role_id
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
                st.success(f"成功匯入 {success_count} 個角色")
                st.rerun()
            except Exception as e:
                st.error(f"匯入失敗: {str(e)}") 