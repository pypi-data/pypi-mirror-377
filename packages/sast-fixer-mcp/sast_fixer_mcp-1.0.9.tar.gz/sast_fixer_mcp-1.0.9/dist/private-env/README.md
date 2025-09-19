# SAST FIXER MCP Server内网安装包

SAST FIXER MCP Server 是一个基于 Model Context Protocol (MCP) 的服务端程序，用于处理静态应用安全测试（SAST）报告。
主要功能包括：

* 解析 DOCX 格式的 SAST 报告
* 跟踪漏洞修复状态
* 导出修复完成的综合报告
* 可与展露 AI Programmer 无缝集成，实现自动化漏洞修复

---

## 安装说明（研发测试域）

由于研发测试域 **无法访问公网 PyPI**，安装需依赖本地提供的安装包。

目录结构示例：

```
private-env/
 ├── packages/                 # 存放依赖包（whl 文件）
 │    ├── sast_fixer_mcp-1.0.8-py3-none-any.whl
 │    ├── 其他依赖 *.whl
 ├── python-3.12.9-amd64.exe   # Python 安装包
 └── README.md                 # 安装说明
```

---

### 1. 安装 Python

#### 方法一：直接下载安装

如果尚未安装Python或版本不符合要求，建议安装最稳定的Python 3.12版本：

* **Windows**: [下载 Python 3.12 for Windows](https://mirrors.aliyun.com/python-release/windows/python-3.12.9-amd64.exe)
  * 静默安装命令：
  ```bash
  python-3.12.9-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
  ```

* **macOS**: [下载 Python 3.12 for macOS](https://mirrors.aliyun.com/python-release/macos/python-3.12.10-macos11.pkg)
  * 静默安装命令：
  ```bash
  sudo installer -pkg /path/to/python-3.12.10-macos11.pkg -target /
  ```

#### 方法二：统信UOS系统安装

1. 通过统信UOS的可信库或联系厂商获取对应版本的Python安装包
2. 如支持APT，可尝试使用以下命令安装Python和pip：

```bash
sudo apt-get install python3.12 python3-pip
```

3. 验证安装：

```bash
python3 --version
pip3 --version
```

#### 升级Python

如果当前Python版本不符合要求，请使用上述链接下载并安装推荐的Python 3.12版本。确保系统PATH指向新的Python安装。

安装完成后，验证：

```bash
python --version
```

输出示例：

```
Python 3.12.9
```

---

### 2. 安装依赖（离线）

进入 `env` 目录，执行以下命令：

#### 推荐方式：一次性安装

```bash
pip install --no-index --find-links=./packages sast-fixer-mcp
```

说明：

* `--no-index`：禁止联网访问 PyPI
* `--find-links=./packages`：指定本地 whl 包目录

#### 备用方式：批量安装所有 whl

```bash
pip install ./packages/*.whl
```

Windows PowerShell：

```powershell
pip install (Get-ChildItem ./packages/*.whl)
```

---

### 3. 验证安装

```bash
pip show sast-fixer-mcp
```

若能看到版本号和路径，说明安装成功。

---

## VS Code 配置

在 VS Code 中配置 MCP Server：

1. 打开 **用户设置 JSON**

   * 快捷键 `Ctrl + Shift + P` → 输入 `Preferences: Open User Settings (JSON)`
2. 或在项目中新建 `.vscode/mcp.json` 文件

### 配置示例

```json
{
  "mcpServers": {
    "sast-fixer-mcp": {
      "command": "python",
      "args": ["-m", "sast_fixer_mcp"],
      "alwaysAllow": [
        "convert_sast_docx_to_json",
        "get_pending_vulnerability_json_files",
        "generate_csv_report"
      ],
      "timeout": 1800,
      "disabled": false
    }
  }
}
```

### 注意事项

如果运行时报错：

* `No module named sast_fixer_mcp`
* `MCP error -32000: Connection closed`

请先确认 Python 路径：

```bash
where python   # Windows
```

例如：

```
C:\Users\xxx\AppData\Local\Programs\Python\Python312\python.exe
```

然后在配置文件中将 `"command": "python"` 改为完整路径。