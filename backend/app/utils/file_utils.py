import os
import uuid
from typing import Optional

def save_uploaded_file(file_content: bytes, original_filename: str, upload_dir: str = "uploads") -> str:
    """保存上传的文件并返回新的文件名"""
    # 确保上传目录存在
    os.makedirs(upload_dir, exist_ok=True)

    # 获取文件扩展名
    _, ext = os.path.splitext(original_filename)

    # 生成唯一文件名
    new_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, new_filename)

    # 保存文件
    with open(file_path, 'wb') as f:
        f.write(file_content)

    return new_filename

def get_file_extension(filename: str) -> str:
    """获取文件扩展名（不包含点号）"""
    _, ext = os.path.splitext(filename)
    return ext.lower().lstrip('.')

def validate_file_format(filename: str, allowed_formats: list) -> bool:
    """验证文件格式是否支持"""
    ext = get_file_extension(filename)
    return ext in allowed_formats

def get_file_size(file_path: str) -> int:
    """获取文件大小（字节）"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    size = size_bytes
    i = 0

    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024
        i += 1

    return f"{size:.1f} {size_names[i]}"