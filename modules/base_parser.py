"""
Abstract base parser with utility methods for data normalization
Provides: safe conversion to int/float (handles spaces, commas, special chars),
diagonal inches extraction (removes quote variants)
"""

import re
from abc import ABC


class Parser(ABC):
    def _safe_to_int(self, value: str | None) -> int | None:
        if value is None:
            return None
        try:
            normalized = re.sub(r"[\s\u00a0\u202f]", "", value)
            return int(normalized)
        except ValueError:
            return None

    def _safe_to_float(self, value: str | None) -> float | None:
        if value is None:
            return None
        try:
            normalized = re.sub(r"[\s\u00a0\u202f]", "", value)
            normalized = normalized.replace(",", ".")
            normalized = re.sub(r"[^\d.\-]", "", normalized)
            return float(normalized)
        except ValueError:
            return None

    def _get_diagonal_inches(self, text_value: str | None) -> float | None:
        if not text_value:
            return None
        normalized = (text_value.replace('"', "")
                      .replace("''", "")
                      .replace("″", "")
                      .replace("“", "")
                      .replace(",", ".")
                      .strip())
        try:
            return float(normalized)
        except ValueError:
            return None
