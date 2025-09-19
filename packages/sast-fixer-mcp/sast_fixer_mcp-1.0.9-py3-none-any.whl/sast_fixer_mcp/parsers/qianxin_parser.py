"""
奇安信SAST报告解析器实现
基于结构分析结果
"""
import re
from typing import Dict, Any, List
from docx import Document
from .base import ISASTParser


class QiAnXinParser(ISASTParser):
    """奇安信SAST报告解析器"""

    def can_parse(self, docx_path: str) -> bool:
        """检测是否为奇安信报告格式"""
        try:
            doc = self._get_document(docx_path)

            # 检查奇安信特有的标题结构
            has_detection_summary = False
            has_detail_info = False

            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if "1、检测概要" in text:
                    has_detection_summary = True
                elif "2、详细信息" in text:
                    has_detail_info = True

            # 奇安信格式：必须同时有"检测概要"和"详细信息"
            return has_detection_summary and has_detail_info

        except Exception:
            return False

    def get_vendor_name(self) -> str:
        """获取厂商名称"""
        return "qianxin"

    def get_priority(self) -> int:
        """获取解析器优先级（奇安信优先级较高）"""
        return 50

    def parse_docx_to_json(self, docx_path: str) -> Dict[str, Any]:
        """解析docx为标准JSON格式"""
        vulnerabilities = self._extract_vulnerabilities_from_tables(docx_path)

        return {
            "vendor": self.get_vendor_name(),
            "report_type": "SAST",
            "vulnerabilities": vulnerabilities
        }

    def _extract_vulnerabilities_from_tables(self, docx_path: str) -> List[Dict[str, Any]]:
        """从奇安信文档的所有表格中提取漏洞信息"""
        doc = self._get_document(docx_path)
        vulnerabilities = []

        # 遍历所有表格寻找漏洞信息
        for table_idx, table in enumerate(doc.tables):
            # 在每个表格中查找"一级分类："开头的行
            for row_idx, row in enumerate(table.rows):
                if len(row.cells) > 0:
                    text = row.cells[0].text.strip()
                    if text.startswith("一级分类："):
                        vuln_data = self._parse_complete_vulnerability_block(table, row_idx)
                        if vuln_data:
                            # 只处理中危和高危漏洞
                            if vuln_data["issue_level"] in ["Medium", "High"]:
                                vulnerabilities.append(vuln_data)

        return vulnerabilities

    def _parse_complete_vulnerability_block(self, table, start_row: int) -> Dict[str, Any]:
        """解析完整的漏洞块信息，包括所有缺陷详情"""
        try:
            # 行0: 漏洞分类 "一级分类：xxx 二级分类：xxx"
            category_line = table.rows[start_row].cells[0].text.strip()
            if not category_line.startswith("一级分类："):
                return None

            # 提取分类信息
            if "二级分类：" in category_line:
                parts = category_line.split("二级分类：")
                primary_category = parts[0].replace("一级分类：", "").strip()
                secondary_category = parts[1].strip()
            else:
                # 后备方案：如果格式不匹配，直接使用整行
                primary_category = category_line.replace("一级分类：", "")
                secondary_category = ""

            # 行1: 数量信息
            count_line = table.rows[start_row + 1].cells[0].text.strip()
            count_match = re.search(r"数量：(\d+)", count_line)
            issue_count = count_match.group(1) if count_match else "1"

            # 动态提取完整的issue_desc和fix_advice
            issue_desc = self._extract_complete_description(table, start_row)
            fix_advice = self._extract_complete_fix_advice(table, start_row)

            # 推断漏洞级别
            issue_level = self._infer_vulnerability_level(primary_category, secondary_category)

            # 从行6开始提取所有缺陷信息
            code_list = []
            current_pos = start_row + 6
            next_vuln_start = len(table.rows)

            # 查找下一个漏洞块的开始位置
            for j in range(current_pos + 10, len(table.rows)):
                next_text = table.rows[j].cells[0].text.strip()
                if next_text.startswith("一级分类："):
                    next_vuln_start = j
                    break

            # 提取所有缺陷信息
            while current_pos < next_vuln_start:
                defect_data = self._extract_single_defect(table, current_pos, next_vuln_start)
                if defect_data:
                    code_list.append(defect_data)
                    current_pos += 4  # 每个缺陷块通常4行
                else:
                    current_pos += 1

            vulnerability = {
                "issue_title": f"{primary_category}：{secondary_category}",
                "issue_level": issue_level,
                "issue_count": issue_count,
                "issue_desc": issue_desc,
                "fix_advice": fix_advice,
                "code_sample": "",  # 奇安信格式中没有代码示例
                "code_list": code_list,
                "next_block_start": next_vuln_start
            }

            return vulnerability

        except Exception as e:
            # 解析失败，跳过这个块
            return None

    def _extract_complete_description(self, table, start_row: int) -> str:
        """提取漏洞描述（从XML直接解析）"""
        if start_row + 3 < len(table.rows):
            cell = table.rows[start_row + 3].cells[0]

            # 直接从cell的XML中提取所有文本内容
            cell_xml = cell._tc.xml
            return self._extract_text_from_xml(cell_xml)
        return ""

    def _extract_complete_fix_advice(self, table, start_row: int) -> str:
        """提取修复建议（从XML直接解析）"""
        if start_row + 5 < len(table.rows):
            cell = table.rows[start_row + 5].cells[0]

            # 直接从cell的XML中提取所有文本内容
            cell_xml = cell._tc.xml
            return self._extract_text_from_xml(cell_xml)
        return ""

    def _extract_text_from_xml(self, xml_content):
        """从XML内容中提取所有文本，处理软回车"""
        import re

        # 将软回车转换为换行符
        xml_with_newlines = xml_content.replace('<w:br/>', '\n')

        # 提取所有<w:t>标签内的文本内容（排除XML标签）
        text_matches = re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml_with_newlines, re.DOTALL)

        if text_matches:
            # 合并所有文本片段
            full_text = ''.join(text_matches)

            # 清理可能残留的XML标签
            clean_text = re.sub(r'<[^>]+>', '', full_text)

            return clean_text.strip()

        return ""

    def _extract_complete_tracking_path(self, table, start_pos: int, tracking_path: str, defect_num: str, file_path: str, line_num: str) -> str:
        """提取完整的跟踪路径信息（从XML直接解析）"""
        # 如果跟踪路径行存在，直接从XML提取完整内容
        if start_pos + 2 < len(table.rows):
            tracking_cell = table.rows[start_pos + 2].cells[0]
            tracking_xml = tracking_cell._tc.xml

            # 使用相同的XML提取方法获取完整内容
            full_tracking_content = self._extract_text_from_xml(tracking_xml)

            if full_tracking_content and len(full_tracking_content) > 50:
                # 如果提取到了完整的跟踪路径内容，直接返回
                return full_tracking_content.strip()

        # 回退：如果XML提取失败，使用原有逻辑
        if tracking_path and len(tracking_path) > 100:
            # 提取并清理跟踪路径内容
            path_content = tracking_path.replace("跟踪路径:", "").replace("跟踪路径1:", "").strip()
            # 格式化跟踪路径，确保包含完整信息
            formatted_path = f"跟踪路径1: {path_content}"
            # 如果内容很长，保留完整内容但进行适当格式化
            if len(formatted_path) > 1000:
                # 尝试在合适的位置断行，保持可读性
                formatted_path = formatted_path[:1000] + "..."
            return formatted_path
        else:
            # 如果没有详细跟踪路径，使用基本信息
            return f"{defect_num} - {file_path}:{line_num}"

    def _extract_single_defect(self, table, start_pos: int, end_pos: int) -> Dict[str, Any]:
        """提取单个缺陷的详细信息"""
        try:
            if start_pos >= end_pos or start_pos >= len(table.rows):
                return None

            text = table.rows[start_pos].cells[0].text.strip()

            # 查找缺陷编号行
            if text.startswith("缺陷") and ("处理" in text or "状态" in text):
                # 提取缺陷编号：格式可能是 "缺陷1（缺陷状态：未处理）"
                import re
                defect_match = re.search(r"缺陷(\d+)", text)
                defect_num = f"缺陷{defect_match.group(1)}" if defect_match else text.split("（")[0]

                # 获取爆发行信息（下一行）
                outbreak_info = ""
                if start_pos + 1 < len(table.rows):
                    outbreak_text = table.rows[start_pos + 1].cells[0].text.strip()
                    if "爆发行:" in outbreak_text:
                        outbreak_info = outbreak_text

                # 获取跟踪路径信息（再下一行）
                tracking_path = ""
                if start_pos + 2 < len(table.rows):
                    tracking_text = table.rows[start_pos + 2].cells[0].text.strip()
                    if "跟踪路径" in tracking_text:
                        tracking_path = tracking_text

                # 解析文件路径和行号
                file_path = "未知"
                line_num = "未知"

                if outbreak_info:
                    # 从爆发行信息中提取文件路径和行号
                    # 格式: "爆发行:文件路径 行号"
                    outbreak_content = outbreak_info.split("爆发行:", 1)
                    if len(outbreak_content) > 1:
                        path_line = outbreak_content[1].strip()
                        # 分离文件路径和行号，只保留文件路径部分
                        parts = path_line.split('\n')[0].strip()  # 取第一行，去除换行符
                        # 提取文件路径和行号
                        if ' ' in parts:
                            path_parts = parts.rsplit(' ', 1)
                            if len(path_parts) == 2 and path_parts[1].isdigit():
                                file_path = path_parts[0]
                                line_num = path_parts[1]
                            else:
                                file_path = parts
                                line_num = "未知"
                        else:
                            file_path = parts
                            line_num = "未知"

                # 构建代码详情，提取完整的跟踪路径
                code_details = self._extract_complete_tracking_path(table, start_pos, tracking_path, defect_num, file_path, line_num)

                return {
                    "code_location": file_path,
                    "code_line_num": line_num,
                    "code_details": code_details
                }

            return None

        except Exception:
            return None

    def _infer_vulnerability_level(self, primary_category: str, secondary_category: str) -> str:
        """推断漏洞级别"""
        # 根据漏洞类型推断严重程度
        text = (primary_category + " " + secondary_category).lower()

        high_risk_patterns = [
            "代码注入", "sql注入", "命令注入", "xss", "跨站脚本", "注入",
            "身份验证", "授权", "密码", "认证绕过", "反序列化",
            "dom xss", "反射型xss", "存储型xss", "代码执行", "远程执行",
            "任意代码执行", "命令执行", "文件上传", "任意文件", "路径遍历"
        ]

        medium_risk_patterns = [
            "安全特性", "配置", "信息泄露", "资源管理", "信息泄漏",
            "会话管理", "加密", "哈希", "输入验证", "系统信息",
            "敏感信息", "cookie", "session", "debug", "日志",
            "actuator", "信息暴露", "目录遍历"
        ]

        for pattern in high_risk_patterns:
            if pattern in text:
                return "High"

        for pattern in medium_risk_patterns:
            if pattern in text:
                return "Medium"

        return "Low"  # 默认为低风险