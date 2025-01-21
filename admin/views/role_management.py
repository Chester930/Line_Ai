import streamlit as st
from shared.utils.role_manager import RoleManager
from shared.database.document_crud import DocumentCRUD
import json
import uuid

def show_page():
    """顯示角色管理頁面"""
    st.header("角色管理 (Role Management)")
    
    role_manager = RoleManager()
    
    # 創建新角色
    with st.expander("➕ 創建新角色 (Create New Role)", expanded=False):
        with st.form("create_role"):
            st.write("請填寫新角色的基本資訊：")
            role_id = st.text_input(
                "角色ID (英文) (Role ID)",
                help="唯一標識符，例如：custom_helper"
            )
            name = st.text_input(
                "角色名稱 (Role Name)",
                help="顯示名稱，例如：客服助手"
            )
            description = st.text_area(
                "角色描述 (Role Description)",
                help="角色的主要功能和特點"
            )
            
            # 選擇共用 prompts
            st.subheader("選擇共用 Prompts")
            
            # 基礎設定
            st.write("**基礎設定**")
            categories = {
                "語言設定": "language",
                "語氣風格": "tone",
                "輸出格式": "output_format",
                "寫作風格": "writing_style"
            }
            
            selected_prompts = {}
            available_prompts = role_manager.get_available_prompts()
            
            # 基礎設定的下拉選單
            for zh_cat, en_cat in categories.items():
                prompts = {k: v for k, v in available_prompts.items() if v.get('category') == en_cat}
                if prompts:
                    options = [""] + [data.get('description', pid) for pid, data in prompts.items()]
                    selected = st.selectbox(
                        f"{zh_cat}",
                        options=options,
                        format_func=lambda x: "請選擇" if x == "" else x
                    )
                    # 將選擇的描述轉回 prompt_id
                    for pid, data in prompts.items():
                        if data.get('description') == selected:
                            selected_prompts[pid] = True
            
            # MBTI 性格設定（獨立區塊）
            st.write("")  # 添加間距
            st.write("**MBTI 性格設定**")
            mbti_prompts = {k: v for k, v in available_prompts.items() if v.get('type') == 'MBTI'}
            if mbti_prompts:
                options = [""] + [data.get('description', pid) for pid, data in mbti_prompts.items()]
                selected_mbti = st.selectbox(
                    "選擇 MBTI 性格",
                    options=options,
                    format_func=lambda x: "請選擇" if x == "" else x
                )
                for pid, data in mbti_prompts.items():
                    if data.get('description') == selected_mbti:
                        selected_prompts[pid] = True
            
            # 進階性格設定（獨立區塊）
            st.write("")  # 添加間距
            st.write("**進階性格設定**")
            personality_prompts = {k: v for k, v in available_prompts.items() if v.get('type') == 'Personality'}
            if personality_prompts:
                options = [data.get('description', pid) for pid, data in personality_prompts.items()]
                selected_personalities = st.multiselect(
                    "選擇進階性格特質（可複選）",
                    options=options
                )
                for pid, data in personality_prompts.items():
                    if data.get('description') in selected_personalities:
                        selected_prompts[pid] = True
            
            # AI 模型進階設定
            st.write("")  # 添加間距
            st.subheader("AI 模型進階設定 (Advanced AI Settings)")
            col1, col2 = st.columns(2)
            with col1:
                temperature = st.slider(
                    "溫度 (Temperature)", 
                    0.0, 1.0, 0.7,
                    help="控制回應的創造性，越高越有創意"
                )
                max_tokens = st.number_input(
                    "最大 Token 數 (Max Tokens)",
                    100, 4000, 1000,
                    help="單次回應的最大長度"
                )
            
            with col2:
                top_p = st.slider(
                    "Top P",
                    0.0, 1.0, 0.9,
                    help="控制回應的多樣性"
                )
                frequency_penalty = st.slider(
                    "Frequency Penalty",
                    -2.0, 2.0, 0.0,
                    help="控制模型避免重複內容的程度"
                )
            
            if st.form_submit_button("創建角色 (Create)"):
                if role_id and name:
                    try:
                        settings = {
                            'temperature': temperature,
                            'top_p': top_p,
                            'max_tokens': max_tokens,
                            'frequency_penalty': frequency_penalty
                        }
                        
                        # 過濾出被選中的 prompts
                        selected_prompt_ids = [
                            pid for pid, selected in selected_prompts.items() 
                            if selected
                        ]
                        
                        if role_manager.create_role(
                            role_id=role_id,
                            name=name,
                            description=description,
                            base_prompts=selected_prompt_ids,
                            settings=settings
                        ):
                            st.success("✅ 角色創建成功！")
                            st.experimental_rerun()
                        else:
                            st.error("❌ 創建失敗")
                    except Exception as e:
                        st.error(f"❌ 創建失敗：{str(e)}")
                else:
                    st.warning("⚠️ 請填寫必要欄位")
    
    # 顯示現有角色列表
    show_roles_list(role_manager)

def show_roles_list(role_manager: RoleManager):
    """顯示現有角色列表"""
    st.subheader("現有角色列表 (Existing Roles)")
    roles = role_manager.list_roles()
    
    if not roles:
        st.info("⚠️ 目前沒有角色")
        return
    
    for role_id, role in roles.items():
        with st.expander(f"{role.name} ({role_id})", expanded=False):
            show_role_details(role, role_id, role_manager)

def show_role_details(role, role_id: str, role_manager: RoleManager):
    """顯示角色詳細資訊"""
    st.write(f"描述：{role.description}")
    
    # 顯示設定
    st.write("**AI 模型設定：**")
    st.json(role.settings)
    
    # 顯示使用的提示詞
    if role.base_prompts:
        st.write("**使用的提示詞：**")
        available_prompts = role_manager.get_available_prompts()
        for prompt_id in role.base_prompts:
            if prompt_id in available_prompts:
                st.write(f"- {available_prompts[prompt_id].get('description', prompt_id)}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("刪除角色", key=f"del_{role_id}"):
            if role_manager.delete_role(role_id):
                st.success("✅ 角色已刪除")
                st.experimental_rerun()
            else:
                st.error("❌ 刪除失敗")

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