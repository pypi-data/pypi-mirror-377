# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a SAST (Static Application Security Testing) Fixer MCP Server that provides dedicated handling of SAST reports. It's designed as a Model Context Protocol (MCP) server for parsing DOCX vulnerability reports, tracking remediation status, and generating comprehensive fix reports.

## Architecture

The project follows a multi-vendor extensible architecture:

- **Core MCP Server** (`src/sast_fixer_mcp/server.py`): Main MCP server implementation with three primary tools
- **Multi-vendor Parser Support**: Designed to support different SAST vendor formats (currently Moan format, with extensibility for QiAnXin and others)
- **JSON Workflow**: DOCX → JSON → Remediation Tracking → CSV Reports

### Key Components

- `convert_sast_docx_to_json`: Converts SAST DOCX reports to structured JSON format
- `get_pending_vulnerability_json_files`: Retrieves pending vulnerability files (`_new.json`)
- `generate_csv_report`: Creates CSV reports from resolved vulnerabilities (`_finished.json`)

The system creates a `.scanissuefix` directory to track vulnerability lifecycle:
- `*_new.json`: Newly parsed vulnerabilities awaiting remediation
- `*_finished.json`: Completed vulnerability fixes with status tracking

## Development Commands

### Testing
```bash
# Run the main test for Moan parser
uv run python tests/test_moan_parser.py

# Run pytest for full test suite
uv run pytest
```

### Code Quality
```bash
# Linting
uv run ruff check

# Type checking
uv run pyright
```

### Development Setup
```bash
# Install dependencies
uv sync

# Run server locally for testing
uv run python -m sast_fixer_mcp --verbose --working-directory /path/to/test/project
```

### Build and Distribution
```bash
# Build package
uv build

# Upload to PyPI (requires proper credentials)
twine upload ./dist/*
```

### MCP Inspector for Debugging
```bash
# For uvx installations
npx @modelcontextprotocol/inspector uvx sast-fixer-mcp

# For local development
npx @modelcontextprotocol/inspector uv run sast-fixer-mcp
```

## Important Notes

- **Path Security**: The codebase includes path traversal protection in `server.py:206-219` to prevent directory traversal attacks
- **Working Directory**: All operations are scoped to the specified working directory for security
- **Extensible Design**: The `tests/parsers/` directory contains architecture design for supporting multiple SAST vendor formats
- **JSON Structure**: All parsers must output to a standardized JSON format for consistency across vendors

## Testing Data Structure

Test data is organized by vendor:
- `tests/moan_report/`: Moan format test files
- `tests/qianxin_report/`: QiAnXin format test files (future)
- `tests/parsers/`: Parser architecture and factory implementations

## Python Requirements

- Python 3.10+ required
- Uses `uv` for dependency management
- Key dependencies: mcp, python-docx, click, gitpython, pydantic