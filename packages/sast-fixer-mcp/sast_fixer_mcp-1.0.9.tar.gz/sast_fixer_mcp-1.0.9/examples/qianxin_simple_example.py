#!/usr/bin/env python3
"""
QiAnXin SAST 转换简单使用示例
演示如何在代码中直接使用 convert_sast_docx_to_json 函数
"""

import sys
from pathlib import Path

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from sast_fixer_mcp.server import convert_sast_docx_to_json


def simple_qianxin_example():
    """简单的QiAnXin转换示例"""

    # 获取项目根目录
    project_root = Path(__file__).parent.parent

    # 设置正确的文件路径
    docx_file = project_root / "tests" / "qianxin_report" / "奇安信-sast报告-webgoat.docx"
    working_directory = project_root / "tests" / "qianxin_report"
    # docx_file = project_root / "tests" / "moan_report" / "默安-sast报告-acepilot-server.docx"
    # working_directory = project_root / "tests" / "moan_report"

    print("QiAnXin SAST 转换示例")
    print("-" * 40)
    print(f"输入文件: {docx_file}")
    print(f"工作目录: {working_directory}")

    # 检查文件是否存在
    if not docx_file.exists():
        print(f"错误: 文件不存在 {docx_file}")
        return

    try:
        # 调用转换函数
        result = convert_sast_docx_to_json(str(docx_file), str(working_directory))

        print(f"转换结果: {result}")
        print("转换成功!")

        # 检查输出文件
        output_dir = working_directory / ".scanissuefix"
        if output_dir.exists():
            json_files = list(output_dir.glob("*_new.json"))
            print(f"生成了 {len(json_files)} 个JSON文件")

            # 显示前3个文件名
            for i, file in enumerate(json_files[:3], 1):
                print(f"  {i}. {file.name}")

            if len(json_files) > 3:
                print(f"  ... 还有 {len(json_files) - 3} 个文件")

    except Exception as e:
        print(f"转换失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    simple_qianxin_example()