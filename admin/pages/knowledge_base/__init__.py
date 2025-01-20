import streamlit as st
from . import local_kb
from . import role_kb
from . import search_kb
from . import permission_kb
from . import import_export_kb

def show_page():
    """知識庫管理頁面"""
    st.header("知識庫管理")
    
    # 使用標籤頁來組織不同功能
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "本地知識庫",
        "角色知識庫配置",
        "知識庫搜索",
        "權限管理",
        "導入/導出"
    ])
    
    with tab1:
        local_kb.show_local_kb()
    
    with tab2:
        role_kb.show_role_kb()
    
    with tab3:
        search_kb.show_search_kb()
    
    with tab4:
        permission_kb.show_permission_kb()
    
    with tab5:
        import_export_kb.show_import_export_kb()
    
    # TODO: 雲端知識庫功能待實現
    # with st.expander("雲端知識庫 (開發中)", expanded=False):
    #     st.info("雲端知識庫功能開發中...") 