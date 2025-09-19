# QiAnXin SAST 解析器测试指南

本文档说明如何测试 QiAnXin SAST 报告解析功能。

## 快速开始

### 1. 基本测试

运行完整的QiAnXin转换测试：

```bash
cd tests
uv run python test_qianxin_conversion.py
```

### 2. 简单使用示例

运行基本的转换示例：

```bash
uv run python examples/qianxin_simple_example.py
```

### 3. 直接调用API

在Python代码中直接使用：

```python
from sast_fixer_mcp.server import convert_sast_docx_to_json

# 转换QiAnXin SAST报告
result = convert_sast_docx_to_json(
    docx_file_path="path/to/qianxin_report.docx",
    working_directory="path/to/output/directory"
)

print(f"转换结果: {result}")
```

## 测试输出

### 预期结果

QiAnXin解析器能够：

- ✅ **多漏洞类型检测**: 从100+个表格中识别各种漏洞类型
- ✅ **风险级别过滤**: 只输出中危和高危漏洞
- ✅ **动态内容提取**: 自动适应不同的文档结构
- ✅ **标准JSON格式**: 与MoAn格式保持一致

### 输出统计（示例）

```
转换统计报告:
   高危漏洞: 94 种
   中危漏洞: 61 种
   总漏洞类型: 155 种
   总缺陷数量: 634 个
```

### JSON文件格式

生成的JSON文件包含：

```json
{
  "issue_title": "代码注入：SQL注入",
  "issue_level": "High",
  "issue_count": "21",
  "issue_desc": "完整的漏洞描述...",
  "fix_advice": "详细的修复建议...",
  "code_sample": "",
  "code_list": [
    {
      "code_location": "WebGoat-2025.3/src/main/java/...",
      "code_line_num": "142",
      "code_details": "跟踪路径1: 完整的调用链..."
    }
  ]
}
```

## 文件命名规则

输出文件按以下格式命名：

```
{序号}_{漏洞标题}_{风险级别}_漏洞数{数量}_{分片序号}_new.json
```

示例：
- `1_代码注入SQL注入_高危_漏洞数21_1_new.json`
- `12_安全特性Cookie未设置HTTPOnly属性_中危_漏洞数16_1_new.json`

## 支持的漏洞类型

QiAnXin解析器能识别包括但不限于：

### 高危漏洞
- SQL注入、代码注入
- XSS (DOM、反射型、存储型)
- 文件上传漏洞
- 路径遍历
- 代码执行
- 认证绕过

### 中危漏洞
- 信息泄露
- Cookie安全设置
- 会话管理
- 配置问题
- 系统信息暴露

## 故障排除

### 常见问题

1. **编码错误**: 确保系统支持UTF-8编码
2. **文件不存在**: 检查DOCX文件路径是否正确
3. **权限问题**: 确保有读取输入文件和写入输出目录的权限

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 然后运行转换
result = convert_sast_docx_to_json(docx_file, working_dir)
```

## 与MoAn对比

| 特性 | MoAn | QiAnXin |
|------|------|---------|
| 漏洞类型数量 | 3种 | 155种 |
| 文档结构 | 固定格式 | 动态适应 |
| 风险级别 | 手动配置 | 智能推断 |
| 输出格式 | 标准JSON | 标准JSON |

## 性能优化

对于大型文档：

1. 确保有足够的内存
2. 使用SSD存储以提高I/O性能
3. 考虑并行处理多个文档

## 扩展性

要添加新的漏洞类型识别：

1. 更新 `_infer_vulnerability_level()` 方法
2. 添加相应的风险模式匹配
3. 测试新类型的识别准确性