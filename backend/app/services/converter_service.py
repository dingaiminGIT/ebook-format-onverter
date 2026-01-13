import os
import uuid
from typing import Tuple
import ebooklib
from ebooklib import epub
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import re
from bs4 import BeautifulSoup
import html
import logging
import PyPDF2
from io import BytesIO

# 设置日志
logging.basicConfig(level=logging.INFO)

class EbookConverter:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    def txt_to_epub(self, txt_path: str, title: str = "转换的电子书", author: str = "未知作者") -> str:
        """将TXT文件转换为EPUB格式"""
        # 读取TXT文件
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 创建EPUB书籍
        book = epub.EpubBook()

        # 设置元数据
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(title)
        book.set_language('zh')
        book.add_author(author)

        # 按段落分割内容
        paragraphs = content.split('\n\n')
        chapters = []

        # 每10段作为一章
        for i in range(0, len(paragraphs), 10):
            chapter_paragraphs = paragraphs[i:i+10]
            chapter_content = '\n\n'.join(chapter_paragraphs)

            # 创建章节
            chapter = epub.EpubHtml(
                title=f'第{i//10 + 1}章',
                file_name=f'chapter_{i//10 + 1}.xhtml',
                lang='zh'
            )

            # 设置章节内容
            chapter_html = f"""
            <html>
            <head>
                <title>第{i//10 + 1}章</title>
            </head>
            <body>
                <h1>第{i//10 + 1}章</h1>
                {''.join(f'<p>{p}</p>' for p in chapter_paragraphs if p.strip())}
            </body>
            </html>
            """
            chapter.content = chapter_html

            book.add_item(chapter)
            chapters.append(chapter)

        # 添加导航
        book.toc = [(epub.Link(f"chapter_{i+1}.xhtml", f"第{i+1}章", f"chapter_{i+1}"), ) for i in range(len(chapters))]

        # 添加spine
        book.spine = ['nav'] + chapters

        # 添加导航文件
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # 生成输出文件名
        output_filename = f"{uuid.uuid4().hex}.epub"
        output_path = os.path.join(self.upload_dir, output_filename)

        # 写入EPUB文件
        epub.write_epub(output_path, book)

        return output_filename

    def epub_to_pdf(self, epub_path: str, title: str = "转换的电子书") -> str:
        """将EPUB文件转换为PDF格式"""
        logging.info(f"开始转换EPUB文件: {epub_path}")

        # 生成输出文件名
        output_filename = f"{uuid.uuid4().hex}.pdf"
        output_path = os.path.join(self.upload_dir, output_filename)

        # 创建PDF文档
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()

        try:
            # 注册中文字体 - 使用系统内置的中文字体
            try:
                # 尝试注册中文字体
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                chinese_font = 'STSong-Light'
            except:
                try:
                    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
                    chinese_font = 'HeiseiMin-W3'
                except:
                    # 如果都不可用，使用默认字体，但这可能导致中文显示问题
                    chinese_font = 'Helvetica'
                    logging.warning("无法注册中文字体，使用默认字体")

            # 创建支持中文的自定义样式
            title_style = ParagraphStyle(
                'ChineseTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                fontName=chinese_font,
                encoding='utf-8'
            )

            content_style = ParagraphStyle(
                'ChineseContent',
                parent=styles['Normal'],
                fontSize=12,
                leading=18,
                spaceAfter=12,
                fontName=chinese_font,
                encoding='utf-8'
            )

            story = []

            # 读取EPUB文件
            book = epub.read_epub(epub_path)
            logging.info(f"成功读取EPUB文件，包含 {len(list(book.get_items()))} 个项目")

            # 添加标题
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2*inch))

            # 收集所有文档内容
            all_text_content = []

            # 提取所有文档项目
            document_items = []

            # 首先尝试按spine顺序获取
            try:
                for spine_id, _ in book.spine:
                    for item in book.get_items():
                        if item.get_id() == spine_id and item.get_type() == ebooklib.ITEM_DOCUMENT:
                            document_items.append(item)
                            break
            except:
                # 如果spine方法失败，直接获取所有文档项目
                document_items = [item for item in book.get_items() if item.get_type() == ebooklib.ITEM_DOCUMENT]

            # 如果没有找到任何文档，尝试所有项目
            if not document_items:
                document_items = list(book.get_items())

            for item in document_items:
                # 检查项目类型，接受文档类型或任何包含文本的项目
                if item and (item.get_type() == ebooklib.ITEM_DOCUMENT or hasattr(item, 'get_content')):
                    try:
                        # 获取内容
                        content = None
                        try:
                            content = item.get_content()
                            if isinstance(content, bytes):
                                content = content.decode('utf-8')
                        except Exception as decode_error:
                            logging.error(f"解码文档 {getattr(item, 'file_name', 'unknown')} 时出错: {decode_error}")
                            continue

                        if not content:
                            continue

                        logging.info(f"处理文档: {getattr(item, 'file_name', 'unknown')}, 内容长度: {len(content)}")

                        # 使用BeautifulSoup解析HTML
                        soup = BeautifulSoup(content, 'html.parser')

                        # 移除脚本和样式标签
                        for script in soup(["script", "style"]):
                            script.decompose()

                        # 提取文本内容，保持段落结构
                        # 处理标题
                        for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                            header_text = header.get_text().strip()
                            if header_text:
                                all_text_content.append(f"## {header_text}")

                        # 处理段落
                        paragraphs_found = False
                        for para in soup.find_all('p'):
                            para_text = para.get_text().strip()
                            if para_text:
                                all_text_content.append(para_text)
                                paragraphs_found = True

                        # 如果没有找到段落标签，直接提取所有文本
                        if not paragraphs_found:
                            text = soup.get_text()
                            # 清理文本
                            text = html.unescape(text)
                            text = re.sub(r'\s+', ' ', text).strip()
                            if text:
                                # 按双换行分割段落
                                paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                                all_text_content.extend(paragraphs)

                        # 如果仍然没有内容，尝试按行分割
                        if not all_text_content:
                            text = soup.get_text()
                            text = html.unescape(text)
                            lines = [line.strip() for line in text.split('\n') if line.strip()]
                            all_text_content.extend(lines)

                    except Exception as e:
                        logging.error(f"处理文档 {getattr(item, 'file_name', 'unknown')} 时出错: {str(e)}")
                        # 尝试直接提取原始文本
                        try:
                            if hasattr(item, 'get_content'):
                                raw_content = item.get_content()
                                if isinstance(raw_content, bytes):
                                    raw_content = raw_content.decode('utf-8', errors='ignore')
                                if raw_content:
                                    all_text_content.append(raw_content[:1000])  # 限制长度
                        except:
                            pass
                        continue

            logging.info(f"提取到 {len(all_text_content)} 个段落")

            # 将内容添加到PDF
            for i, para_text in enumerate(all_text_content):
                if para_text:
                    try:
                        # 处理标题
                        if para_text.startswith('## '):
                            clean_text = para_text[3:].strip()
                            story.append(Paragraph(clean_text, title_style))
                            story.append(Spacer(1, 0.1*inch))
                        else:
                            # 普通段落
                            # 限制段落长度避免过长
                            if len(para_text) > 1000:
                                # 将长段落分割
                                chunks = [para_text[i:i+1000] for i in range(0, len(para_text), 1000)]
                                for chunk in chunks:
                                    story.append(Paragraph(chunk, content_style))
                                    story.append(Spacer(1, 6))
                            else:
                                story.append(Paragraph(para_text, content_style))
                                story.append(Spacer(1, 6))
                    except Exception as e:
                        logging.error(f"添加段落 {i} 时出错: {str(e)}")
                        # 尝试用简化的文本
                        try:
                            safe_text = ''.join(c for c in para_text if ord(c) < 65536)
                            story.append(Paragraph(safe_text, content_style))
                            story.append(Spacer(1, 6))
                        except:
                            logging.error(f"段落 {i} 完全无法处理，跳过")
                            continue

            if not story or len(story) <= 2:  # 只有标题和间距
                error_msg = "未能从EPUB文件中提取到有效内容"
                story.append(Paragraph(error_msg, content_style))

        except Exception as e:
            logging.error(f"EPUB解析过程中出错: {str(e)}")
            story = []
            error_msg = f"EPUB解析错误: {str(e)}"
            story.append(Paragraph(error_msg, content_style))

        try:
            # 生成PDF
            logging.info("开始生成PDF文件")
            doc.build(story)
            logging.info(f"PDF文件生成完成: {output_path}")

            # 检查生成的文件大小
            file_size = os.path.getsize(output_path)
            logging.info(f"生成的PDF文件大小: {file_size} 字节")

        except Exception as e:
            logging.error(f"生成PDF时出错: {str(e)}")
            # 创建一个包含错误信息的简单PDF
            error_story = [Paragraph(f"PDF生成错误: {str(e)}", styles['Normal'])]
            doc.build(error_story)

        return output_filename

    def _escape_for_pdf(self, text: str) -> str:
        """为PDF输出转义特殊字符（简化版本）"""
        if not text:
            return ""

        # 只处理基本的XML转义字符
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')

        return text

    def pdf_to_epub(self, pdf_path: str, title: str = "转换的电子书", author: str = "未知作者") -> str:
        """将PDF文件转换为EPUB格式"""
        logging.info(f"开始将PDF转换为EPUB: {pdf_path}")

        try:
            # 读取PDF文件
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""

                # 提取所有页面的文本
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n\n"

                logging.info(f"PDF页面数: {len(pdf_reader.pages)}")
                logging.info(f"提取的文本长度: {len(text_content)}")

        except Exception as e:
            logging.error(f"读取PDF文件时出错: {str(e)}")
            raise Exception(f"无法读取PDF文件: {str(e)}")

        if not text_content.strip():
            raise Exception("PDF文件中没有找到可提取的文本内容")

        # 创建EPUB书籍
        book = epub.EpubBook()

        # 设置元数据
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(title)
        book.set_language('zh')
        book.add_author(author)

        # 清理和分割文本内容
        # 移除多余的空白字符
        text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
        text_content = re.sub(r' +', ' ', text_content)

        # 按段落分割内容
        paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
        chapters = []

        # 每15段作为一章（PDF通常内容较密集）
        for i in range(0, len(paragraphs), 15):
            chapter_paragraphs = paragraphs[i:i+15]
            chapter_content = '\n\n'.join(chapter_paragraphs)

            # 创建章节
            chapter = epub.EpubHtml(
                title=f'第{i//15 + 1}章',
                file_name=f'chapter_{i//15 + 1}.xhtml',
                lang='zh'
            )

            # 设置章节内容（HTML格式）
            html_content = f"""
            <html>
            <head><title>第{i//15 + 1}章</title></head>
            <body>
            <h2>第{i//15 + 1}章</h2>
            """

            # 将段落转换为HTML
            for paragraph in chapter_paragraphs:
                # 转义HTML特殊字符
                escaped_paragraph = html.escape(paragraph)
                html_content += f"<p>{escaped_paragraph}</p>\n"

            html_content += """
            </body>
            </html>
            """

            chapter.content = html_content
            book.add_item(chapter)
            chapters.append(chapter)

        # 创建目录
        book.toc = [(epub.Link(f"chapter_{i}.xhtml", f"第{i+1}章", f"chapter_{i}"), [])
                    for i in range(len(chapters))]

        # 添加导航文件
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # 创建spine
        book.spine = ['nav'] + chapters

        # 生成输出文件名
        output_filename = f"{uuid.uuid4().hex}.epub"
        output_path = os.path.join(self.upload_dir, output_filename)

        # 保存EPUB文件
        try:
            epub.write_epub(output_path, book, {})
            logging.info(f"EPUB文件生成完成: {output_path}")

            # 检查生成的文件大小
            file_size = os.path.getsize(output_path)
            logging.info(f"生成的EPUB文件大小: {file_size} 字节")

        except Exception as e:
            logging.error(f"保存EPUB文件时出错: {str(e)}")
            raise Exception(f"保存EPUB文件失败: {str(e)}")

        return output_filename

    def get_file_info(self, filename: str) -> Tuple[str, int]:
        """获取文件信息"""
        file_path = os.path.join(self.upload_dir, filename)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            return file_path, size
        return None, 0

    def cleanup_file(self, filename: str) -> bool:
        """清理临时文件"""
        file_path = os.path.join(self.upload_dir, filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False