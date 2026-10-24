# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Anti-AI Copywriting Linter (Zero-dependency rule & buzzword checker)."""

__version__ = "0.5.0"

from .detector import LintReport, LintViolation, analyze_text

__all__ = ["analyze_text", "LintReport", "LintViolation", "__version__"]
