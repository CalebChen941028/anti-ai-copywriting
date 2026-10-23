"""Anti-AI Copywriting Linter (Zero-dependency rule & buzzword checker)."""

__version__ = "0.2.0"

from .detector import LintReport, LintViolation, analyze_text

__all__ = ["analyze_text", "LintReport", "LintViolation", "__version__"]
