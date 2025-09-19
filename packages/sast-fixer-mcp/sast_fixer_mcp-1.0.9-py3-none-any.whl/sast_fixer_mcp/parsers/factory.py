"""
SAST解析器工厂类
"""
from typing import Dict, List, Any, Optional
import os
from docx import Document

from .base import ISASTParser


class SASTParserFactory:
    """SAST解析器工厂"""

    def __init__(self):
        self._parsers: List[ISASTParser] = []

    def register_parser(self, parser: ISASTParser) -> None:
        """
        注册解析器

        Args:
            parser: 解析器实例
        """
        self._parsers.append(parser)
        # 按优先级排序
        self._parsers.sort(key=lambda x: x.get_priority())

    def get_parser(self, docx_path: str) -> Optional[ISASTParser]:
        """
        自动选择合适的解析器

        Args:
            docx_path: Word文档路径

        Returns:
            ISASTParser: 合适的解析器实例，如果没有找到返回None
        """
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"文件不存在: {docx_path}")

        for parser in self._parsers:
            try:
                if parser.can_parse(docx_path):
                    return parser
            except Exception as e:
                # 记录检测失败，但继续尝试其他解析器
                print(f"解析器 {parser.get_vendor_name()} 检测失败: {e}")
                continue

        return None

    def parse_docx(self, docx_path: str) -> Dict[str, Any]:
        """
        解析docx文档

        Args:
            docx_path: Word文档路径

        Returns:
            Dict: 解析结果

        Raises:
            ValueError: 当没有找到合适的解析器时
        """
        parser = self.get_parser(docx_path)
        if parser is None:
            raise ValueError(f"无法找到支持该文档格式的解析器: {docx_path}")

        try:
            result = parser.parse_docx_to_json(docx_path)

            # 添加元数据
            result["vendor"] = parser.get_vendor_name()
            result["report_type"] = "SAST"

            return result
        finally:
            # 解析完成后清理缓存
            parser._clear_cache()

    def get_supported_vendors(self) -> List[str]:
        """
        获取支持的厂商列表

        Returns:
            List[str]: 支持的厂商名称列表
        """
        return [parser.get_vendor_name() for parser in self._parsers]


# 全局工厂实例
sast_parser_factory = SASTParserFactory()


def detect_vendor_by_content(docx_path: str) -> Optional[str]:
    """
    通过文档内容检测厂商类型的辅助函数

    Args:
        docx_path: Word文档路径

    Returns:
        Optional[str]: 检测到的厂商名称，未检测到返回None
    """
    try:
        doc = Document(docx_path)

        # 收集文档内容用于检测
        content_text = ""
        for paragraph in doc.paragraphs[:10]:  # 只检查前10个段落
            content_text += paragraph.text + " "

        content_lower = content_text.lower()

        # 厂商特征关键词
        vendor_keywords = {
            "moan": ["默安", "moan", "代码卫士"],
            "qianxin": ["奇安信", "qianxin", "360", "代码安全"],
            "checkmarx": ["checkmarx", "cx"],
            "sonarqube": ["sonarqube", "sonar"],
            "fortify": ["fortify", "micro focus"],
            "veracode": ["veracode"],
        }

        for vendor, keywords in vendor_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return vendor

        return None

    except Exception:
        return None