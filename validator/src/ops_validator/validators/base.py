"""BaseValidator: error/warning collection and reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationIssue:
    rule_id: str
    field_path: str
    message: str
    is_warning: bool = False

    def __str__(self) -> str:
        level = "WARNING" if self.is_warning else "ERROR"
        return f"[{level}] [{self.rule_id}] {self.field_path}: {self.message}"


class BaseValidator:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.errors: list[ValidationIssue] = []
        self.warnings: list[ValidationIssue] = []

    def _error(self, rule_id: str, field_path: str, message: str) -> None:
        self.errors.append(ValidationIssue(rule_id, field_path, message))

    def _warning(self, rule_id: str, field_path: str, message: str) -> None:
        self.warnings.append(ValidationIssue(rule_id, field_path, message, is_warning=True))

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def validate(self) -> bool:
        """Run validation. Returns True if no errors (warnings allowed)."""
        raise NotImplementedError

    def report(self) -> str:
        """Return a human-readable validation summary."""
        lines = [f"Validation report: {self.path}"]
        lines.append(f"  Errors:   {len(self.errors)}")
        lines.append(f"  Warnings: {len(self.warnings)}")
        if self.errors:
            lines.append("\nERRORS:")
            for e in self.errors:
                lines.append(f"  {e}")
        if self.warnings:
            lines.append("\nWARNINGS:")
            for w in self.warnings:
                lines.append(f"  {w}")
        if self.is_valid:
            lines.append("\nPASSED")
        else:
            lines.append("\nFAILED")
        return "\n".join(lines)
