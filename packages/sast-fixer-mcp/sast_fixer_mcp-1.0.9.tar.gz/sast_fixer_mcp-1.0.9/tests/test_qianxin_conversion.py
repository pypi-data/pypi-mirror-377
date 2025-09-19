#!/usr/bin/env python3
"""
QiAnXin SAST 报告转换测试
演示如何使用 convert_sast_docx_to_json 函数处理奇安信SAST报告
"""

import os
import sys
import shutil
import json
from pathlib import Path

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from sast_fixer_mcp.server import convert_sast_docx_to_json


def test_qianxin_conversion():
    """测试QiAnXin SAST报告转换"""

    print("=" * 60)
    print("QiAnXin SAST 报告转换测试")
    print("=" * 60)

    # 1. 设置测试文件路径
    test_dir = Path(__file__).parent.parent
    qianxin_file = test_dir / "test_data" / "qianxin" / "奇安信-sast报告-webgoat.docx"
    working_dir = test_dir / "test_data" / "qianxin"

    print(f"测试文件: {qianxin_file}")
    print(f"工作目录: {working_dir}")

    # 2. 检查文件是否存在
    if not qianxin_file.exists():
        print(f"错误: 测试文件不存在 {qianxin_file}")
        return False

    print(f"测试文件存在")

    # 3. 清理之前的输出
    output_dir = working_dir / ".scanissuefix"
    if output_dir.exists():
        shutil.rmtree(output_dir)
        print(f"清理旧输出目录")

    # 4. 执行转换
    print(f"\n开始转换...")
    try:
        result = convert_sast_docx_to_json(str(qianxin_file), str(working_dir))
        print(f"转换完成: {result}")
    except Exception as e:
        print(f"转换失败: {e}")
        return False

    # 5. 验证输出结果
    print(f"\n验证输出结果...")

    if not output_dir.exists():
        print(f"输出目录不存在: {output_dir}")
        return False

    json_files = list(output_dir.glob("*_new.json"))
    print(f"生成JSON文件数量: {len(json_files)}")

    if len(json_files) == 0:
        print(f"没有生成JSON文件")
        return False

    # 6. 分析结果统计
    high_count = 0
    medium_count = 0
    total_defects = 0
    vulnerability_summary = []

    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        issue_level = data.get('issue_level', 'Unknown')
        issue_title = data.get('issue_title', 'Unknown')
        issue_count = data.get('issue_count', '0')
        code_list_count = len(data.get('code_list', []))

        if issue_level == 'High':
            high_count += 1
        elif issue_level == 'Medium':
            medium_count += 1

        total_defects += code_list_count

        vulnerability_summary.append({
            'title': issue_title,
            'level': issue_level,
            'reported_count': issue_count,
            'actual_defects': code_list_count,
            'filename': json_file.name
        })

    # 7. 输出统计报告
    print(f"\n转换统计报告:")
    print(f"   高危漏洞: {high_count} 种")
    print(f"   中危漏洞: {medium_count} 种")
    print(f"   总漏洞类型: {len(json_files)} 种")
    print(f"   总缺陷数量: {total_defects} 个")

    # 8. 显示前5种漏洞详情
    print(f"\n前5种漏洞详情:")
    for i, vuln in enumerate(vulnerability_summary[:5], 1):
        print(f"   {i}. {vuln['title']}")
        print(f"      风险级别: {vuln['level']}")
        print(f"      报告数量: {vuln['reported_count']}")
        print(f"      实际缺陷: {vuln['actual_defects']} 个")
        print(f"      文件名: {vuln['filename']}")
        print()

    if len(vulnerability_summary) > 5:
        print(f"   ... 还有 {len(vulnerability_summary) - 5} 种其他漏洞")

    # 9. 验证JSON格式
    print(f"\n验证JSON格式...")
    sample_file = json_files[0]
    with open(sample_file, 'r', encoding='utf-8') as f:
        sample_data = json.load(f)

    required_fields = ['issue_title', 'issue_level', 'issue_count',
                      'issue_desc', 'fix_advice', 'code_list']

    missing_fields = []
    for field in required_fields:
        if field not in sample_data:
            missing_fields.append(field)

    if missing_fields:
        print(f"缺少必需字段: {missing_fields}")
        return False

    print(f"JSON格式验证通过")

    # 10. 显示示例内容
    if sample_data.get('code_list'):
        print(f"\n示例缺陷信息:")
        first_defect = sample_data['code_list'][0]
        print(f"   位置: {first_defect.get('code_location', 'N/A')}")
        print(f"   行号: {first_defect.get('code_line_num', 'N/A')}")
        print(f"   详情: {first_defect.get('code_details', 'N/A')[:100]}...")

    print(f"\nQiAnXin转换测试完成!")
    return True


def main():
    """主函数"""
    try:
        success = test_qianxin_conversion()
        if success:
            print(f"\n所有测试通过!")
            return 0
        else:
            print(f"\n测试失败!")
            return 1
    except Exception as e:
        print(f"\n测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())