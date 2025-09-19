"""
SAST解析器基础接口定义
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from docx import Document


class ISASTParser(ABC):
    """SAST报告解析器接口"""

    def __init__(self):
        self._cached_doc: Optional[Document] = None
        self._cached_path: Optional[str] = None

    def _get_document(self, docx_path: str) -> Document:
        """获取文档，使用缓存避免重复读取"""
        if self._cached_path != docx_path or self._cached_doc is None:
            self._cached_doc = Document(docx_path)
            self._cached_path = docx_path
        return self._cached_doc

    def _clear_cache(self):
        """清理缓存"""
        self._cached_doc = None
        self._cached_path = None

    @abstractmethod
    def can_parse(self, docx_path: str) -> bool:
        """
        检测是否能解析该文档

        Args:
            docx_path: Word文档路径

        Returns:
            bool: 是否支持解析该文档
        """
        pass

    @abstractmethod
    def get_vendor_name(self) -> str:
        """
        获取厂商名称

        Returns:
            str: 厂商名称标识
        """
        pass

    @abstractmethod
    def parse_docx_to_json(self, docx_path: str) -> Dict[str, Any]:
        """
        解析docx为标准JSON格式

        Args:
            docx_path: Word文档路径

        Returns:
            Dict: 标准化的漏洞数据
        """
        pass

    @abstractmethod
    def get_priority(self) -> int:
        """
        获取解析器优先级（数字越小优先级越高）

        Returns:
            int: 优先级数值
        """
        pass