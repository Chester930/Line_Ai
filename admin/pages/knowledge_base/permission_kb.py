import streamlit as st
from shared.database.document_crud import DocumentCRUD
from shared.database.models import PermissionType
from datetime import datetime, timedelta

def show_permission_kb():
    """顯示知識庫權限管理頁面"""
    # 初始化必要的類別
    doc_crud = DocumentCRUD()
    
    # 獲取當前用戶ID (暫時使用測試ID)
    current_user_id = 1  # TODO: 從session獲取實際用戶ID
    
    # 獲取用戶的所有知識庫
    knowledge_bases = doc_crud.get_user_knowledge_bases(current_user_id)
    if not knowledge_bases:
        st.warning("尚未創建任何知識庫")
        return
    
    # 選擇知識庫
    selected_kb = st.selectbox(
        "選擇知識庫",
        options=knowledge_bases,
        format_func=lambda x: x.name
    )
    
    if not selected_kb:
        return
    
    # 顯示知識庫信息
    st.subheader(f"知識庫：{selected_kb.name}")
    if selected_kb.description:
        st.write(selected_kb.description)
    
    # 使用標籤頁組織不同功能
    tab1, tab2, tab3 = st.tabs(["權限設置", "分享管理", "操作日誌"])
    
    with tab1:
        show_permission_settings(doc_crud, selected_kb.id)
    
    with tab2:
        show_share_management(doc_crud, selected_kb.id)
    
    with tab3:
        show_action_logs(doc_crud, selected_kb.id)

def show_permission_settings(doc_crud, kb_id):
    """顯示權限設置"""
    st.subheader("權限設置")
    
    # 公開設置
    kb = doc_crud.get_knowledge_base(kb_id)
    is_public = st.checkbox("公開知識庫", value=kb.is_public)
    if is_public != kb.is_public:
        # TODO: 更新公開設置
        pass
    
    # 顯示現有權限
    st.write("### 已授權用戶")
    permissions = doc_crud.get_kb_permissions(kb_id)
    
    if permissions:
        for perm in permissions:
            cols = st.columns([3, 2, 1])
            with cols[0]:
                st.write(f"用戶：{perm.user.display_name}")
            with cols[1]:
                current_type = perm.permission_type
                new_type = st.selectbox(
                    "權限類型",
                    options=list(PermissionType),
                    index=list(PermissionType).index(current_type),
                    key=f"perm_{perm.id}"
                )
                if new_type != current_type:
                    if doc_crud.grant_permission(kb_id, perm.user_id, new_type):
                        st.success("✅ 權限已更新")
                        st.rerun()
            with cols[2]:
                if st.button("撤銷", key=f"revoke_{perm.id}"):
                    if doc_crud.revoke_permission(kb_id, perm.user_id):
                        st.success("✅ 權限已撤銷")
                        st.rerun()
    else:
        st.info("尚未授權任何用戶")
    
    # 添加新權限
    with st.form("add_permission"):
        st.write("### 添加權限")
        # TODO: 實現用戶搜索
        user_id = st.number_input("用戶ID", min_value=1)
        permission_type = st.selectbox(
            "權限類型",
            options=list(PermissionType)
        )
        
        if st.form_submit_button("授予權限"):
            if doc_crud.grant_permission(kb_id, user_id, permission_type):
                st.success("✅ 權限已授予")
                st.rerun()
            else:
                st.error("❌ 授予失敗")

def show_share_management(doc_crud, kb_id):
    """顯示分享管理"""
    st.subheader("分享管理")
    
    # 顯示現有分享
    st.write("### 現有分享")
    shares = doc_crud.get_kb_shares(kb_id)
    
    if shares:
        for share in shares:
            with st.expander(f"分享碼：{share.share_code}", expanded=True):
                cols = st.columns([2, 2, 1])
                with cols[0]:
                    st.write(f"權限：{share.permission_type.value}")
                    if share.expires_at:
                        st.write(f"過期時間：{share.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        st.write("永不過期")
                with cols[1]:
                    st.write(f"創建時間：{share.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                with cols[2]:
                    if st.button("刪除", key=f"del_share_{share.id}"):
                        if doc_crud.delete_share(share.share_code):
                            st.success("✅ 分享已刪除")
                            st.rerun()
    else:
        st.info("尚未創建任何分享")
    
    # 創建新分享
    with st.form("create_share"):
        st.write("### 創建分享")
        permission_type = st.selectbox(
            "權限類型",
            options=list(PermissionType)
        )
        
        # 過期時間設置
        expire_options = ["永不過期", "1天", "7天", "30天", "自定義"]
        expire_type = st.selectbox("過期時間", expire_options)
        
        expires_at = None
        if expire_type == "自定義":
            expires_at = st.date_input("選擇過期日期")
            if expires_at:
                expires_at = datetime.combine(expires_at, datetime.max.time())
        elif expire_type != "永不過期":
            days = int(expire_type.replace("天", ""))
            expires_at = datetime.now() + timedelta(days=days)
        
        if st.form_submit_button("創建分享"):
            share_code = doc_crud.create_share(
                kb_id,
                permission_type,
                expires_at
            )
            if share_code:
                st.success(f"✅ 分享已創建，分享碼：{share_code}")
                st.rerun()
            else:
                st.error("❌ 創建失敗")

def show_action_logs(doc_crud, kb_id):
    """顯示操作日誌"""
    st.subheader("操作日誌")
    
    # 獲取日誌
    logs = doc_crud.get_kb_logs(kb_id)
    
    if logs:
        for log in logs:
            with st.expander(
                f"{log.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {log.action}",
                expanded=False
            ):
                st.write(f"操作者：{log.user.display_name}")
                st.write(f"操作：{log.action}")
                if log.details:
                    st.json(log.details)
    else:
        st.info("暫無操作日誌") 