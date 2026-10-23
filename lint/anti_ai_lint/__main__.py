# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Entry point for python -m anti_ai_lint."""

from .cli import main
import sys

if __name__ == "__main__":
    sys.exit(main())

