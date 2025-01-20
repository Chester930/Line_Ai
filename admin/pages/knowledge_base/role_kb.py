import streamlit as st
from shared.database.document_crud import DocumentCRUD
from shared.utils.role_manager import RoleManager

def show_role_kb():
    """顯示角色知識庫配置頁面"""
    # 初始化必要的類別
    doc_crud = DocumentCRUD()
    role_manager = RoleManager()
    
    # 獲取當前用戶ID (暫時使用測試ID)
    current_user_id = 1  # TODO: 從session獲取實際用戶ID
    
    # 獲取所有角色
    roles = role_manager.get_all_roles()
    if not roles:
        st.warning("尚未創建任何角色")
        return
    
    # 選擇角色
    selected_role_id = st.selectbox(
        "選擇角色",
        options=[role['id'] for role in roles],
        format_func=lambda x: next(role['name'] for role in roles if role['id'] == x)
    )
    
    # 顯示選中角色的信息
    selected_role = next(role for role in roles if role['id'] == selected_role_id)
    st.subheader(f"角色：{selected_role['name']}")
    if selected_role.get('description'):
        st.write(selected_role['description'])
    
    # 獲取用戶的所有知識庫
    knowledge_bases = doc_crud.get_user_knowledge_bases(current_user_id)
    if not knowledge_bases:
        st.warning("尚未創建任何知識庫")
        return
    
    # 獲取角色已配置的知識庫
    role_kbs = doc_crud.get_role_knowledge_bases(selected_role_id)
    configured_kb_ids = [kb.id for kb in role_kbs]
    
    # 顯示知識庫配置
    st.subheader("知識庫配置")
    
    # 使用 form 來一次性提交所有更改
    with st.form("role_kb_config"):
        changed = False
        new_configs = []
        
        for kb in knowledge_bases:
            is_configured = kb.id in configured_kb_ids
            if st.checkbox(
                f"{kb.name}",
                value=is_configured,
                help=kb.description or "無描述"
            ):
                if not is_configured:
                    changed = True
                new_configs.append(kb.id)
            elif is_configured:
                changed = True
        
        if st.form_submit_button("保存配置"):
            if changed:
                try:
                    # 更新角色的知識庫配置
                    if doc_crud.update_role_knowledge_bases(selected_role_id, new_configs):
                        st.success("✅ 配置已更新")
                        st.rerun()
                    else:
                        st.error("❌ 更新失敗")
                except Exception as e:
                    st.error(f"❌ 更新失敗：{str(e)}")
            else:
                st.info("配置未變更")
    
    # 顯示當前配置的統計
    show_role_kb_stats(doc_crud, selected_role_id)

def show_role_kb_stats(doc_crud, role_id):
    """顯示角色知識庫統計"""
    st.subheader("知識庫統計")
    
    # 獲取角色配置的所有知識庫
    role_kbs = doc_crud.get_role_knowledge_bases(role_id)
    
    if not role_kbs:
        st.info("尚未配置任何知識庫")
        return
    
    # 顯示每個知識庫的統計信息
    for kb in role_kbs:
        with st.expander(f"知識庫：{kb.name}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "文件總數",
                    doc_crud.count_documents(kb_id=kb.id)
                )
            
            with col2:
                st.metric(
                    "已處理文件數",
                    doc_crud.count_documents(
                        kb_id=kb.id,
                        embedding_status="completed"
                    )
                )
            
            with col3:
                st.metric(
                    "文本片段數",
                    doc_crud.count_chunks(kb_id=kb.id)
                ) 