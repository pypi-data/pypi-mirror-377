"""
测试奇安信SAST报告解析器
"""
import sys
import os
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sast_fixer_mcp.parsers import sast_parser_factory, QiAnXinParser
from sast_fixer_mcp.server import convert_sast_docx_to_json


def test_qianxin_parser():
    """测试奇安信解析器功能"""
    print("=" * 60)
    print("测试奇安信SAST报告解析器")
    print("=" * 60)

    # 测试文件路径
    test_file = Path(__file__).parent.parent / "test_data" / "qianxin" / "奇安信-sast报告-webgoat.docx"

    if not test_file.exists():
        print(f"错误: 测试文件不存在: {test_file}")
        return False

    print(f"测试文件: {test_file.name}")

    try:
        # 测试1: 验证解析器注册
        print("\n测试1: 验证解析器注册")
        supported_vendors = sast_parser_factory.get_supported_vendors()
        print(f"支持的厂商: {supported_vendors}")
        assert "qianxin" in supported_vendors, "奇安信解析器应该已注册"
        print("✅ 奇安信解析器已正确注册")

        # 测试2: 测试厂商检测
        print("\n测试2: 测试厂商检测")
        parser = sast_parser_factory.get_parser(str(test_file))
        if parser:
            print(f"检测到的厂商: {parser.get_vendor_name()}")
            print(f"解析器优先级: {parser.get_priority()}")
        else:
            print("警告: 未找到合适的解析器")

        # 测试3: 测试奇安信解析器直接检测
        print("\n测试3: 测试奇安信解析器直接检测")
        qianxin_parser = QiAnXinParser()
        can_parse = qianxin_parser.can_parse(str(test_file))
        print(f"奇安信解析器能否解析: {can_parse}")

        # 测试4: 通过MCP服务器接口测试
        print("\n测试4: 通过MCP服务器接口测试")
        temp_dir = test_file.parent
        result = convert_sast_docx_to_json(str(test_file), str(temp_dir))
        print(f"转换结果: {result}")

        if "已保存到" in result:
            # 检查生成的JSON文件
            output_dir = temp_dir / ".scanissuefix"
            if output_dir.exists():
                json_files = list(output_dir.glob("*_new.json"))
                print(f"生成的JSON文件数量: {len(json_files)}")

                if json_files:
                    # 分析第一个JSON文件
                    import json
                    with open(json_files[0], 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    print(f"JSON文件样本分析:")
                    print(f"  漏洞标题: {data.get('issue_title', 'N/A')}")
                    print(f"  漏洞级别: {data.get('issue_level', 'N/A')}")
                    print(f"  代码位置数量: {len(data.get('code_list', []))}")

        print("\n✅ 奇安信解析器测试完成")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_vendor_selection():
    """测试多厂商解析器选择机制"""
    print("\n" + "=" * 60)
    print("测试多厂商解析器选择机制")
    print("=" * 60)

    # 测试文件路径
    qianxin_file = Path(__file__).parent.parent / "test_data" / "qianxin" / "奇安信-sast报告-webgoat.docx"
    moan_file = Path(__file__).parent.parent / "test_data" / "moan" / "默安-sast报告-acepilot-server.docx"

    files_to_test = []
    if qianxin_file.exists():
        files_to_test.append(("奇安信", qianxin_file))
    if moan_file.exists():
        files_to_test.append(("默安", moan_file))

    for file_type, file_path in files_to_test:
        print(f"\n测试 {file_type} 文件: {file_path.name}")
        parser = sast_parser_factory.get_parser(str(file_path))
        if parser:
            print(f"  选择的解析器: {parser.get_vendor_name()}")
            print(f"  解析器优先级: {parser.get_priority()}")
        else:
            print(f"  未找到合适的解析器")

    print("\n✅ 多厂商选择测试完成")


if __name__ == "__main__":
    success1 = test_qianxin_parser()
    test_multi_vendor_selection()

    if success1:
        print("\n🎉 所有测试通过!")
    else:
        print("\n💥 部分测试失败!")