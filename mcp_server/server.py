#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Standalone runner for anti-ai Model Context Protocol (MCP) server."""

import sys
from pathlib import Path

_lint_dir = str(Path(__file__).resolve().parent.parent / "lint")
if _lint_dir not in sys.path:
    sys.path.insert(0, _lint_dir)

from anti_ai_lint.mcp_server import main

if __name__ == "__main__":
    sys.exit(main())
