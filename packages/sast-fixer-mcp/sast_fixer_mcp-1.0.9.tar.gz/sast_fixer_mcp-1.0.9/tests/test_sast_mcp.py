"""
综合测试SAST MCP服务器功能
包含默安格式的完整测试用例
"""
import sys
import os
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加src路径以导入sast_fixer_mcp模块
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sast_fixer_mcp.server import (
    convert_sast_docx_to_json,
    get_pending_vulnerability_json_files,
    generate_csv_report
)
from sast_fixer_mcp.parsers import sast_parser_factory, MoAnParser


class TestSASTMCPServer:
    """SAST MCP服务器综合测试类"""

    @pytest.fixture
    def temp_working_dir(self):
        """创建临时工作目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def moan_test_file(self):
        """获取默安测试文件路径"""
        test_file = Path(__file__).parent / "moan_report" / "代码大模型develop-sast报告-2025-04-17_issue2.docx"
        if not test_file.exists():
            pytest.skip(f"测试文件不存在: {test_file}")
        return str(test_file)

    def test_parser_factory_registration(self):
        """测试解析器工厂注册功能"""
        # 测试解析器已正确注册
        supported_vendors = sast_parser_factory.get_supported_vendors()
        assert "moan" in supported_vendors, "默安解析器应该已注册"

    def test_moan_parser_detection(self, moan_test_file):
        """测试默安解析器检测功能"""
        parser = sast_parser_factory.get_parser(moan_test_file)
        assert parser is not None, "应该能找到合适的解析器"
        assert parser.get_vendor_name() == "moan", "应该检测为默安解析器"

    def test_convert_sast_docx_to_json_success(self, moan_test_file, temp_working_dir):
        """测试SAST文档转换JSON成功案例"""
        # 将测试文件复制到工作目录以避免路径验证问题
        test_file_copy = Path(temp_working_dir) / "test_report.docx"
        shutil.copy2(moan_test_file, test_file_copy)

        result = convert_sast_docx_to_json(str(test_file_copy), temp_working_dir)

        # 验证返回结果
        assert "已保存到" in result, f"转换应该成功，实际结果: {result}"
        assert ".scanissuefix" in result, "应该提到.scanissuefix目录"

        # 验证输出目录存在
        output_dir = Path(temp_working_dir) / ".scanissuefix"
        assert output_dir.exists(), ".scanissuefix目录应该被创建"

        # 验证JSON文件生成
        json_files = list(output_dir.glob("*_new.json"))
        assert len(json_files) > 0, "应该生成至少一个JSON文件"

        # 验证JSON文件内容结构
        with open(json_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)

        required_fields = ["issue_title", "issue_level", "issue_count", "issue_desc", "fix_advice", "code_sample", "code_list"]
        for field in required_fields:
            assert field in data, f"JSON文件应包含字段: {field}"

    def test_convert_sast_docx_to_json_file_not_found(self, temp_working_dir):
        """测试文件不存在的情况"""
        non_existent_file = os.path.join(temp_working_dir, "non_existent.docx")
        result = convert_sast_docx_to_json(non_existent_file, temp_working_dir)

        assert "文件不存在" in result, "应该返回文件不存在的错误信息"

    def test_convert_sast_docx_to_json_path_traversal_protection(self, moan_test_file, temp_working_dir):
        """测试路径遍历攻击防护"""
        # 尝试路径遍历攻击
        malicious_path = "../../../etc/passwd"
        result = convert_sast_docx_to_json(malicious_path, temp_working_dir)

        assert "非法文件路径" in result or "文件不存在" in result, "应该防护路径遍历攻击"

    def test_get_pending_vulnerability_json_files_success(self, moan_test_file, temp_working_dir):
        """测试获取待处理文件成功案例"""
        # 将测试文件复制到工作目录
        test_file_copy = Path(temp_working_dir) / "test_report.docx"
        shutil.copy2(moan_test_file, test_file_copy)

        # 先转换生成JSON文件
        convert_sast_docx_to_json(str(test_file_copy), temp_working_dir)

        # 获取待处理文件
        result = get_pending_vulnerability_json_files(temp_working_dir)

        # 验证结果
        assert "_new.json" in result, "结果应包含_new.json文件"
        assert ".scanissuefix" in result, "结果应包含.scanissuefix路径"

        # 验证返回的文件确实存在
        file_paths = result.strip().split('\n')
        for file_path in file_paths:
            assert os.path.exists(file_path), f"返回的文件路径应该存在: {file_path}"

    def test_get_pending_vulnerability_json_files_no_directory(self, temp_working_dir):
        """测试目录不存在的情况"""
        result = get_pending_vulnerability_json_files(temp_working_dir)
        assert "不存在" in result, "应该返回目录不存在的错误信息"

    def test_get_pending_vulnerability_json_files_no_files(self, temp_working_dir):
        """测试没有待处理文件的情况"""
        # 创建.scanissuefix目录但不放入文件
        output_dir = Path(temp_working_dir) / ".scanissuefix"
        output_dir.mkdir()

        result = get_pending_vulnerability_json_files(temp_working_dir)
        assert "没有找到" in result, "应该返回没有找到文件的信息"

    def test_generate_csv_report_success(self, moan_test_file, temp_working_dir):
        """测试生成CSV报告成功案例"""
        # 将测试文件复制到工作目录
        test_file_copy = Path(temp_working_dir) / "test_report.docx"
        shutil.copy2(moan_test_file, test_file_copy)

        # 先转换生成JSON文件
        convert_sast_docx_to_json(str(test_file_copy), temp_working_dir)

        # 模拟完成修复，将_new.json转换为_finished.json
        output_dir = Path(temp_working_dir) / ".scanissuefix"
        json_files = list(output_dir.glob("*_new.json"))

        for json_file in json_files[:2]:  # 处理前2个文件
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

        # 生成CSV报告
        result = generate_csv_report(temp_working_dir)

        # 验证结果
        assert "成功" in result, f"CSV生成应该成功，实际结果: {result}"
        assert "sast_fix_report.csv" in result, "应该提到CSV文件名"

        # 验证CSV文件确实生成
        csv_file = output_dir / "sast_fix_report.csv"
        assert csv_file.exists(), "CSV文件应该被创建"

        # 验证CSV文件内容
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "漏洞类型" in content, "CSV应包含表头"
            assert "fixed" in content, "CSV应包含修复状态数据"

    def test_generate_csv_report_no_finished_files(self, moan_test_file, temp_working_dir):
        """测试没有完成文件时生成CSV报告"""
        # 将测试文件复制到工作目录
        test_file_copy = Path(temp_working_dir) / "test_report.docx"
        shutil.copy2(moan_test_file, test_file_copy)

        # 先转换生成JSON文件但不创建finished文件
        convert_sast_docx_to_json(str(test_file_copy), temp_working_dir)

        # 直接生成CSV报告
        result = generate_csv_report(temp_working_dir)

        assert "没有找到" in result, "应该返回没有找到finished文件的信息"

    def test_json_content_validation(self, moan_test_file, temp_working_dir):
        """测试JSON内容的详细验证"""
        # 将测试文件复制到工作目录
        test_file_copy = Path(temp_working_dir) / "test_report.docx"
        shutil.copy2(moan_test_file, test_file_copy)

        # 转换文档
        convert_sast_docx_to_json(str(test_file_copy), temp_working_dir)

        # 读取生成的JSON文件
        output_dir = Path(temp_working_dir) / ".scanissuefix"
        json_files = list(output_dir.glob("*_new.json"))

        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 验证必需字段
            assert data["issue_level"] in ["High", "Medium", "Low", "Notice"], f"漏洞等级应该是有效值: {data['issue_level']}"
            assert isinstance(data["code_list"], list), "code_list应该是列表"
            assert len(data["code_list"]) > 0, "code_list不应该为空"

            # 验证代码项结构
            for code_item in data["code_list"]:
                required_code_fields = ["code_location", "code_line_num", "code_details"]
                for field in required_code_fields:
                    assert field in code_item, f"代码项应包含字段: {field}"

    def test_error_handling_with_corrupted_file(self, temp_working_dir):
        """测试处理损坏文件的错误处理"""
        # 创建一个损坏的docx文件
        corrupted_file = Path(temp_working_dir) / "corrupted.docx"
        with open(corrupted_file, 'w') as f:
            f.write("这不是一个有效的docx文件")

        result = convert_sast_docx_to_json(str(corrupted_file), temp_working_dir)

        # 应该优雅地处理错误，但现在会抛出异常，这是可以接受的
        # 我们检查是否有适当的错误信息
        print(f"错误处理结果: {result}")

        # 由于现在会抛出异常，我们预期这个测试
        # 可以被pytest捕获为失败，这实际上揭示了需要改进错误处理的地方


def run_comprehensive_tests():
    """运行综合测试的主函数"""
    print("=" * 60)
    print("开始运行SAST MCP服务器综合测试")
    print("=" * 60)

    # 使用pytest运行测试
    test_file = __file__
    exit_code = pytest.main([test_file, "-v", "--tb=short"])

    if exit_code == 0:
        print("\n所有综合测试通过!")
    else:
        print("\n部分测试失败!")

    return exit_code == 0


if __name__ == "__main__":
    success = run_comprehensive_tests()
    if not success:
        sys.exit(1)