import psutil
import platform
import sys
import os
from datetime import datetime

def get_system_info() -> dict:
    """獲取系統資訊
    
    Returns:
        dict: 包含系統資訊的字典
    """
    try:
        # CPU 資訊
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # 記憶體資訊
        memory = psutil.virtual_memory()
        memory_total = memory.total / (1024 * 1024 * 1024)  # GB
        memory_used = memory.used / (1024 * 1024 * 1024)    # GB
        memory_percent = memory.percent
        
        # 硬碟資訊
        disk = psutil.disk_usage('/')
        disk_total = disk.total / (1024 * 1024 * 1024)      # GB
        disk_used = disk.used / (1024 * 1024 * 1024)        # GB
        disk_percent = disk.percent
        
        return {
            # 系統資訊
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": sys.version.split()[0],
            "hostname": platform.node(),
            
            # CPU 資訊
            "cpu_percent": cpu_percent,
            "cpu_count": cpu_count,
            
            # 記憶體資訊
            "memory_total": round(memory_total, 2),
            "memory_used": round(memory_used, 2),
            "memory_percent": memory_percent,
            
            # 硬碟資訊
            "disk_total": round(disk_total, 2),
            "disk_used": round(disk_used, 2),
            "disk_percent": disk_percent,
            
            # 運行資訊
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pid": os.getpid()
        }
    except Exception as e:
        return {
            "error": str(e),
            "python_version": sys.version.split()[0]
        } 