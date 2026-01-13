from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.models.converter import ConversionResponse
from app.services.converter_service import EbookConverter
import os
import uuid
from typing import Optional, Dict
import json
import urllib.parse

router = APIRouter()
converter = EbookConverter()

# 文件名映射存储（使用文件持久化）
MAPPING_FILE = "uploads/file_mapping.json"

def load_file_mapping() -> Dict[str, Dict[str, str]]:
    """加载文件映射"""
    try:
        if os.path.exists(MAPPING_FILE):
            with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_file_mapping(mapping: Dict[str, Dict[str, str]]) -> None:
    """保存文件映射"""
    try:
        os.makedirs(os.path.dirname(MAPPING_FILE), exist_ok=True)
        with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def get_file_mapping() -> Dict[str, Dict[str, str]]:
    """获取文件映射"""
    return load_file_mapping()

def update_file_mapping(filename: str, mapping_data: Dict[str, str]) -> None:
    """更新文件映射"""
    current_mapping = load_file_mapping()
    current_mapping[filename] = mapping_data
    save_file_mapping(current_mapping)

def remove_file_mapping(filename: str) -> None:
    """删除文件映射"""
    current_mapping = load_file_mapping()
    if filename in current_mapping:
        del current_mapping[filename]
        save_file_mapping(current_mapping)

SUPPORTED_FORMATS = ["txt", "epub", "pdf"]
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def get_file_extension(filename: str) -> str:
    """获取文件扩展名（不包含点号）"""
    _, ext = os.path.splitext(filename)
    return ext.lower().lstrip('.')

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全的字符"""
    import re
    # 移除或替换不安全的字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 移除前后空格
    filename = filename.strip()
    # 如果文件名为空或只包含点，使用默认名称
    if not filename or filename.replace('.', '') == '':
        filename = '转换的电子书'
    return filename

def generate_download_filename(original_filename: str, title: str, target_ext: str) -> str:
    """生成下载文件名"""
    # 优先使用标题，如果标题为空或是默认值，则使用原始文件名
    if title and title != "转换的电子书":
        base_name = sanitize_filename(title)
    else:
        # 使用原始文件名（不包含扩展名）
        base_name = sanitize_filename(os.path.splitext(original_filename)[0])
        if not base_name:
            base_name = "转换的电子书"

    return f"{base_name}.{target_ext}"

def encode_filename_for_header(filename: str) -> str:
    """为HTTP头部正确编码文件名，支持中文字符"""
    try:
        # 尝试ASCII编码
        filename.encode('ascii')
        return f'attachment; filename="{filename}"'
    except UnicodeEncodeError:
        # 包含非ASCII字符，使用RFC 5987编码
        encoded_filename = urllib.parse.quote(filename.encode('utf-8'))
        return f"attachment; filename*=UTF-8''{encoded_filename}"

def save_uploaded_file(file_content: bytes, original_filename: str, upload_dir: str = "uploads") -> str:
    """保存上传的文件并返回新的文件名"""
    os.makedirs(upload_dir, exist_ok=True)
    _, ext = os.path.splitext(original_filename)
    new_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, new_filename)

    with open(file_path, 'wb') as f:
        f.write(file_content)

    return new_filename

@router.post("/convert", response_model=ConversionResponse)
async def convert_file(
    file: UploadFile = File(...),
    target_format: str = Form(...),
    title: Optional[str] = Form("转换的电子书"),
    author: Optional[str] = Form("未知作者")
):
    """文件格式转换API"""
    try:
        # 验证文件大小
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="文件大小超过限制（50MB）")

        # 验证文件格式
        source_ext = get_file_extension(file.filename)
        if source_ext not in SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的源文件格式: {source_ext}. 支持的格式: {', '.join(SUPPORTED_FORMATS)}"
            )

        # 验证目标格式
        if target_format not in SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的目标格式: {target_format}. 支持的格式: {', '.join(SUPPORTED_FORMATS)}"
            )

        # 检查是否是相同格式
        if source_ext == target_format:
            raise HTTPException(status_code=400, detail="源格式和目标格式相同，无需转换")

        # 保存上传的文件
        input_filename = save_uploaded_file(file_content, file.filename)
        input_path = os.path.join("uploads", input_filename)

        # 执行转换
        output_filename = None

        try:
            if source_ext == "txt" and target_format == "epub":
                output_filename = converter.txt_to_epub(input_path, title, author)
            elif source_ext == "epub" and target_format == "pdf":
                output_filename = converter.epub_to_pdf(input_path, title)
            elif source_ext == "pdf" and target_format == "epub":
                output_filename = converter.pdf_to_epub(input_path, title, author)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"暂不支持从 {source_ext} 转换到 {target_format}"
                )

            # 获取输出文件信息
            _, file_size = converter.get_file_info(output_filename)

            # 生成下载文件名
            download_filename = generate_download_filename(file.filename, title, target_format)

            # 保存文件映射信息
            mapping_data = {
                "original_filename": file.filename,
                "title": title,
                "download_filename": download_filename,
                "target_format": target_format
            }
            update_file_mapping(output_filename, mapping_data)

            # 添加调试日志
            print(f"DEBUG: 保存文件映射 - {output_filename} -> {download_filename}")
            current_mapping = get_file_mapping()
            print(f"DEBUG: 当前映射数量: {len(current_mapping)}")

            return ConversionResponse(
                success=True,
                message="转换成功",
                download_url=f"/api/v1/download/{output_filename}",
                file_size=file_size,
                original_filename=file.filename,
                title=title
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

        finally:
            # 清理输入文件
            converter.cleanup_file(input_filename)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理文件时出错: {str(e)}")

@router.get("/download/{filename}")
async def download_file(filename: str):
    """文件下载API"""
    file_path = os.path.join("uploads", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件未找到")

    # 根据文件扩展名设置Content-Type
    ext = get_file_extension(filename)
    media_types = {
        "epub": "application/epub+zip",
        "pdf": "application/pdf",
        "txt": "text/plain"
    }

    media_type = media_types.get(ext, "application/octet-stream")

    # 获取映射的下载文件名，如果没有映射则使用默认名称
    current_mapping = get_file_mapping()
    print(f"DEBUG: 查找文件映射 - {filename}")
    print(f"DEBUG: 当前映射: {list(current_mapping.keys())}")

    if filename in current_mapping:
        download_name = current_mapping[filename]["download_filename"]
        print(f"DEBUG: 找到映射 - {download_name}")
        # 清理映射（文件下载后删除映射）
        remove_file_mapping(filename)
    else:
        download_name = f"converted.{ext}"
        print(f"DEBUG: 未找到映射，使用默认名称 - {download_name}")

    # 生成正确编码的Content-Disposition头部
    content_disposition = encode_filename_for_header(download_name)

    return FileResponse(
        file_path,
        media_type=media_type,
        filename=download_name,
        headers={"Content-Disposition": content_disposition}
    )

@router.get("/formats")
async def get_supported_formats():
    """获取支持的格式列表"""
    return {
        "supported_formats": SUPPORTED_FORMATS,
        "conversions": [
            {"from": "txt", "to": "epub", "description": "文本文件转EPUB电子书"},
            {"from": "epub", "to": "pdf", "description": "EPUB电子书转PDF文档"},
            {"from": "pdf", "to": "epub", "description": "PDF文档转EPUB电子书"}
        ]
    }