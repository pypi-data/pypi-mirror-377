import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def get_all_watch_directories(watch_topics: Dict[str, List[str]]) -> List[str]:
    """
    获取所有监控目录的绝对路径
    
    Args:
        watch_topics: 主题-目录映射
        
    Returns:
        所有监控目录的绝对路径列表
    """
    directories = []
    for topic, dirs in watch_topics.items():
        for directory in dirs:
            abs_dir = os.path.abspath(directory)
            directories.append(abs_dir)
    return directories

def is_supported_file_type(file_path: str) -> bool:
    """
    检查文件类型是否支持
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否支持该文件类型
    """
    supported_extensions = ['.txt', '.pdf', '.docx', '.md', '.ppt', '.pptx', '.jpg', '.jpeg', '.png']
    ext = os.path.splitext(file_path)[1].lower()
    return ext in supported_extensions

def get_relative_path(base_dir: str, file_path: str) -> str:
    """
    获取文件相对于基准目录的路径
    
    Args:
        base_dir: 基准目录
        file_path: 文件路径
        
    Returns:
        相对路径
    """
    return os.path.relpath(file_path, base_dir)

def format_timestamp(timestamp: str) -> str:
    """
    格式化ISO时间戳为可读格式
    
    Args:
        timestamp: ISO格式时间戳
        
    Returns:
        可读时间字符串
    """
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return timestamp