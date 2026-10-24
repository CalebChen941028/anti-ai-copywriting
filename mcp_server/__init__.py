# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""MCP server package for anti-ai-copywriting."""

from pathlib import Path
import sys

_lint_dir = str(Path(__file__).resolve().parent.parent / "lint")
if _lint_dir not in sys.path:
    sys.path.insert(0, _lint_dir)

from anti_ai_lint.mcp_server import main, run_mcp_server

__all__ = ["main", "run_mcp_server"]
