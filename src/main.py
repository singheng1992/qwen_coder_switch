#!/usr/bin/env python3
"""
Qwen Coder API Key Manager Entry Point
"""
import sys
from pathlib import Path

# 添加项目根目录到 sys.path，以便能够解析 src 包
# 这允许直接运行 python src/main.py
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.cli import app

if __name__ == "__main__":
    app()