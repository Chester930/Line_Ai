import streamlit as st
import sys
import os
import subprocess
import psutil
import time
import json

# 將專案根目錄加入到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config.settings_manager import SettingsManager
from shared.database.database import db

class ProjectManager:
    def __init__(self):
        self.pid_file = "data/project.pid"
        self.process = None
    
    def save_pid(self, pid):
        """保存進程 ID"""
        with open(self.pid_file, 'w') as f:
            json.dump({'pid': pid}, f)
    
    def load_pid(self):
        """載入進程 ID"""
        try:
            if os.path.exists(self.pid_file):
                with open(self.pid_file, 'r') as f:
                    data = json.load(f)
                    return data.get('pid')
        except:
            pass
        return None
    
    def is_running(self):
        """檢查專案是否正在運行"""
        pid = self.load_pid()
        if pid:
            try:
                process = psutil.Process(pid)
                return process.is_running() and "python" in process.name().lower()
            except:
                pass
        return False
    
    def start_project(self):
        """啟動專案"""
        if self.is_running():
            return False, "專案已在運行中"
        
        try:
            # 使用 subprocess.Popen 啟動專案
            process = subprocess.Popen(
                ["python", "run.py", "--mode", "app"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # 保存進程 ID
            self.save_pid(process.pid)
            self.process = process
            
            # 等待幾秒確保啟動成功
            time.sleep(3)
            
            if process.poll() is None:  # 如果進程仍在運行
                return True, "專案啟動成功"
            else:
                # 獲取錯誤輸出
                _, stderr = process.communicate()
                return False, f"專案啟動失敗: {stderr}"
                
        except Exception as e:
            return False, f"啟動錯誤: {str(e)}"
    
    def stop_project(self):
        """停止專案"""
        pid = self.load_pid()
        if pid:
            try:
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=5)  # 等待進程結束
                os.remove(self.pid_file)
                return True, "專案已停止"
            except psutil.NoSuchProcess:
                return True, "專案已不在運行"
            except Exception as e:
                return False, f"停止失敗: {str(e)}"
        return False, "找不到運行中的專案"

def main():
    st.set_page_config(
        page_title="Line AI Assistant 管理後台",
        page_icon="🤖",
        layout="wide"
    )

    settings_manager = SettingsManager()
    project_manager = ProjectManager()

    st.title("Line AI Assistant 管理後台 🤖")

    # 側邊欄選單
    menu = st.sidebar.selectbox(
        "功能選單",
        ["專案控制", "API Keys 設定", "角色管理", "文件管理", "系統狀態"]
    )

    # 在側邊欄顯示專案狀態
    with st.sidebar:
        st.write("---")
        project_status = "🟢 運行中" if project_manager.is_running() else "🔴 已停止"
        st.write(f"專案狀態: {project_status}")

    if menu == "專案控制":
        show_project_control(project_manager, settings_manager)
    elif menu == "API Keys 設定":
        show_api_keys_settings(settings_manager)
    elif menu == "角色管理":
        show_role_management(settings_manager)
    elif menu == "文件管理":
        show_document_management()
    else:
        show_system_status(settings_manager, project_manager)

def show_project_control(project_manager, settings_manager):
    st.header("專案控制")
    
    # 檢查是否已初始化
    if not settings_manager.is_initialized():
        st.warning("請先完成系統初始化設定")
        return
    
    # 檢查專案狀態
    if project_manager.is_running():
        st.info("LINE BOT 正在運行中")
        st.warning("如需修改設定，請先停止 LINE BOT")
        
        if st.button("🛑 停止 LINE BOT", use_container_width=True):
            success, message = project_manager.stop_project()
            if success:
                st.success(message)
                st.experimental_rerun()
            else:
                st.error(message)
    else:
        if st.button("🚀 啟動 LINE BOT", use_container_width=True):
            success, message = project_manager.start_project()
            if success:
                st.success(message)
                st.experimental_rerun()
            else:
                st.error(message)
    
    # 顯示日誌輸出
    if os.path.exists("logs/app.log"):
        st.subheader("應用程式日誌")
        with open("logs/app.log", "r", encoding="utf-8") as f:
            logs = f.readlines()[-50:]  # 只顯示最後50行
            st.code("".join(logs))
    
    # 添加測試區域
    st.subheader("測試區")
    
    # 選擇角色
    roles = settings_manager.list_roles()
    selected_role = st.selectbox(
        "選擇測試角色",
        options=list(roles.keys()),
        format_func=lambda x: roles[x]['name']
    )
    
    # 測試輸入
    test_input = st.text_area("測試問題")
    
    if st.button("測試回應"):
        if test_input:
            try:
                from shared.ai_engine import AIEngine
                
                # 初始化 AI 引擎
                ai_engine = AIEngine()
                
                # 獲取角色設定
                role_data = roles[selected_role]
                
                # 組合提示詞
                prompt = f"{role_data['prompt']}\n\n問題：{test_input}\n回答："
                
                # 生成回應
                response = ai_engine.generate_response(
                    prompt,
                    temperature=role_data['settings']['temperature'],
                    top_p=role_data['settings']['top_p'],
                    max_tokens=role_data['settings']['max_tokens']
                )
                
                st.write("AI 回應：")
                st.write(response)
                
            except Exception as e:
                st.error(f"測試失敗：{str(e)}")
        else:
            st.warning("請輸入測試問題")

def show_api_keys_settings(settings_manager):
    st.header("API Keys 設定")

    with st.form("api_keys_form"):
        line_channel_secret = st.text_input(
            "LINE Channel Secret",
            value=settings_manager.get_api_key("line_channel_secret"),
            type="password"
        )
        
        line_channel_access_token = st.text_input(
            "LINE Channel Access Token",
            value=settings_manager.get_api_key("line_channel_access_token"),
            type="password"
        )
        
        google_api_key = st.text_input(
            "Google API Key",
            value=settings_manager.get_api_key("google_api_key"),
            type="password"
        )
        
        ngrok_auth_token = st.text_input(
            "Ngrok Auth Token",
            value=settings_manager.get_api_key("ngrok_auth_token"),
            type="password"
        )

        if st.form_submit_button("儲存設定"):
            success = settings_manager.update_api_keys(
                line_channel_secret=line_channel_secret,
                line_channel_access_token=line_channel_access_token,
                google_api_key=google_api_key,
                ngrok_auth_token=ngrok_auth_token
            )
            
            if success:
                st.success("API Keys 已更新")
                if not settings_manager.is_initialized():
                    settings_manager.mark_initialized()
            else:
                st.error("更新失敗")

def show_role_management(settings_manager):
    st.header("角色管理")

    # 顯示現有角色
    st.subheader("現有角色")
    roles = settings_manager.list_roles()
    
    for role_id, role_data in roles.items():
        with st.expander(f"角色: {role_data.get('name', role_id)}"):
            st.json(role_data)
            if st.button("刪除", key=f"del_{role_id}"):
                if settings_manager.delete_role(role_id):
                    st.success("角色已刪除")
                    st.experimental_rerun()
                else:
                    st.error("刪除失敗")

    # 新增角色
    st.subheader("新增角色")
    with st.form("add_role"):
        role_id = st.text_input("角色 ID")
        role_name = st.text_input("角色名稱")
        role_description = st.text_area("角色描述")
        role_prompt = st.text_area("角色提示詞")
        
        if st.form_submit_button("新增角色"):
            if role_id and role_name:
                success = settings_manager.update_role(role_id, {
                    "name": role_name,
                    "description": role_description,
                    "prompt": role_prompt
                })
                
                if success:
                    st.success("角色已新增")
                    st.experimental_rerun()
                else:
                    st.error("新增失敗")
            else:
                st.error("請填寫必要欄位")

def show_document_management():
    st.header("文件管理")
    
    # 上傳文件
    uploaded_file = st.file_uploader(
        "上傳文件",
        type=['txt', 'pdf', 'doc', 'docx', 'xlsx'],
        help="支援的格式：TXT, PDF, DOC, DOCX, XLSX"
    )
    
    if uploaded_file:
        save_path = os.path.join("uploads", uploaded_file.name)
        try:
            doc = db.save_document(1, uploaded_file, save_path)  # 假設 bot_id = 1
            st.success(f"文件 {uploaded_file.name} 上傳成功！")
        except Exception as e:
            st.error(f"上傳失敗：{str(e)}")

    # 顯示文件列表
    st.subheader("文件列表")
    try:
        documents = db.get_bot_documents(1)  # 假設 bot_id = 1
        for doc in documents:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {doc.filename}")
                st.write(f"類型：{doc.file_type} | 大小：{doc.file_size} bytes")
            with col2:
                if st.button("刪除", key=f"del_doc_{doc.id}"):
                    # TODO: 實現刪除功能
                    st.warning("刪除功能尚未實現")

    except Exception as e:
        st.error(f"獲取文件列表失敗：{str(e)}")

def show_system_status(settings_manager, project_manager):
    st.header("系統狀態")
    
    # 顯示初始化狀態
    initialized = settings_manager.is_initialized()
    st.subheader("初始化狀態")
    if initialized:
        st.success("系統已完成初始化")
    else:
        st.warning("系統尚未完成初始化")

    # 顯示最後更新時間
    last_updated = settings_manager.settings.get("last_updated")
    if last_updated:
        st.write(f"最後更新時間：{last_updated}")

if __name__ == "__main__":
    main() 