"""
SAST解析器包
支持多厂商SAST报告解析
"""

from .base import ISASTParser
from .factory import SASTParserFactory, sast_parser_factory
from .moan_parser import MoAnParser
from .qianxin_parser import QiAnXinParser

# 注册解析器
sast_parser_factory.register_parser(MoAnParser())     # 默安优先级较高
sast_parser_factory.register_parser(QiAnXinParser())  # 奇安信作为备选


__all__ = [
    'ISASTParser',
    'SASTParserFactory',
    'sast_parser_factory',
    'MoAnParser',
    'QiAnXinParser'
]