import sys
import os
import json
from pathlib import Path

# 添加src路径以导入sast_fixer_mcp模块
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sast_fixer_mcp.server import convert_sast_docx_to_json, get_pending_vulnerability_json_files, generate_csv_report


def test_moan_sast_report():
    """测试默安SAST报告的解析功能"""
    print("=" * 60)
    print("开始测试默安SAST报告解析功能")
    print("=" * 60)

    # 测试文件路径
    test_dir = Path(__file__).parent.parent / "test_data" / "moan"
    docx_file = test_dir / "默安-sast报告-acepilot-server.docx"

    if not docx_file.exists():
        print(f"错误: 测试文件不存在: {docx_file}")
        return False

    print(f"测试目录: {test_dir}")
    print(f"测试文件: {docx_file.name}")

    try:
        # 测试1: 转换docx到json
        print("\n测试1: convert_sast_docx_to_json")
        result1 = convert_sast_docx_to_json(str(docx_file), str(test_dir))
        print(f"转换结果: {result1}")

        # 检查生成的JSON文件
        scanissuefix_dir = test_dir / ".scanissuefix"
        if scanissuefix_dir.exists():
            json_files = list(scanissuefix_dir.glob("*_new.json"))
            print(f"生成的JSON文件数量: {len(json_files)}")
            for i, json_file in enumerate(json_files[:3], 1):  # 只显示前3个
                print(f"   {i}. {json_file.name}")

        # 测试2: 获取待处理文件
        print("\n测试2: get_pending_vulnerability_json_files")
        result2 = get_pending_vulnerability_json_files(str(test_dir))
        print(f"待处理文件:\n{result2}")

        # 测试3: 模拟完成状态并生成CSV报告
        print("\n测试3: 模拟漏洞修复完成并生成CSV报告")

        # 将_new.json文件复制为_finished.json用于测试
        if scanissuefix_dir.exists():
            json_files = list(scanissuefix_dir.glob("*_new.json"))
            for json_file in json_files[:2]:  # 只处理前2个文件用于测试
                # 读取JSON内容
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 添加修复状态信息
                for code_item in data.get("code_list", []):
                    code_item["status"] = "fixed"
                    code_item["false_positive_probability"] = "低"
                    code_item["false_positive_reason"] = "测试修复"

                # 保存为_finished.json
                finished_file = json_file.parent / json_file.name.replace("_new.json", "_finished.json")
                with open(finished_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"   创建测试完成文件: {finished_file.name}")

        # 生成CSV报告
        result3 = generate_csv_report(str(test_dir))
        print(f"CSV报告生成结果: {result3}")

        # 检查CSV文件内容
        csv_file = scanissuefix_dir / "sast_fix_report.csv"
        if csv_file.exists():
            with open(csv_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            print(f"CSV报告行数: {len(lines)}")
            print(f"表头: {lines[0].strip() if lines else '无内容'}")

        print("\n默安SAST报告测试完成")
        return True

    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def analyze_json_structure():
    """分析生成的JSON结构"""
    print("\n分析JSON结构")
    test_dir = Path(__file__).parent.parent / "test_data" / "moan" / ".scanissuefix"

    if not test_dir.exists():
        print("错误: .scanissuefix目录不存在")
        return

    json_files = list(test_dir.glob("*_new.json"))
    if not json_files:
        print("错误: 没有找到JSON文件")
        return

    # 分析第一个JSON文件的结构
    sample_file = json_files[0]
    print(f"分析文件: {sample_file.name}")

    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("JSON结构分析:")
    print(f"   - 顶层键: {list(data.keys())}")
    print(f"   - 漏洞标题: {data.get('issue_title', 'N/A')}")
    print(f"   - 漏洞等级: {data.get('issue_level', 'N/A')}")
    print(f"   - 代码条目数: {len(data.get('code_list', []))}")

    if data.get('code_list'):
        code_item = data['code_list'][0]
        print(f"   - 代码项键: {list(code_item.keys())}")


if __name__ == "__main__":
    success = test_moan_sast_report()
    analyze_json_structure()

    if success:
        print("\n所有测试通过！")
    else:
        print("\n测试失败！")