"""
🔍 LSP Checker: Protocols & Data Structures Module

All protocols, abstractions and data structures for LSP checker.
Follows the Interface Segregation Principle (ISP).
"""

# Python imports
from dataclasses import dataclass
from typing import Any, Protocol


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class MethodSignature:
    """Method signature information"""

    name: str
    args: list[str]
    returns: str | None
    decorators: list[str]
    is_abstract: bool
    raises_exceptions: list[str]


@dataclass
class ClassInfo:
    """Class information for LSP analysis"""

    name: str
    base_classes: list[str]
    methods: dict[str, MethodSignature]
    line_number: int
    is_abstract: bool


@dataclass
class LSPViolation:
    """LSP principle violation"""

    type: str
    base_class: str
    derived_class: str
    method_name: str
    description: str
    suggestion: str
    line_number: int


@dataclass
class LSPAnalysisResult:
    """Complete LSP analysis result"""

    file_path: str
    classes: dict[str, ClassInfo]
    hierarchies: dict[str, list[str]]
    violations: list[LSPViolation]
    lsp_score: float


# ============================================================================
# PROTOCOLS
# ============================================================================


class MethodAnalyzerProtocol(Protocol):
    """Protocol for method analysis"""

    def analyze_method(self, node: Any) -> MethodSignature:
        """
        Analyze method and return signature

        Args:
            node: The node to analyze

        Returns:
            The method signature
        """
        ...


class HierarchyAnalyzerProtocol(Protocol):
    """Protocol for inheritance hierarchy analysis"""

    def analyze_hierarchies(self, classes: dict[str, ClassInfo]) -> dict[str, list[str]]:
        """
        Analyze inheritance hierarchies

        Args:
            classes: The classes to analyze

        Returns:
            The inheritance hierarchies
        """
        ...


class ViolationCheckerProtocol(Protocol):
    """Protocol for LSP violation checking"""

    def check_lsp_violations(
        self, classes: dict[str, ClassInfo], hierarchies: dict[str, list[str]]
    ) -> list[LSPViolation]:
        """
        Check for LSP violations

        Args:
            classes: The classes to analyze
            hierarchies: The hierarchies to analyze

        Returns:
            The LSP violations
        """
        ...


class LSPScorerProtocol(Protocol):
    """Protocol for LSP scoring"""

    def calculate_lsp_score(self, classes: dict[str, ClassInfo], violations: list[LSPViolation]) -> float:
        """
        Calculate LSP compliance score

        Args:
            classes: The classes to analyze
            violations: The violations to analyze

        Returns:
            The LSP score
        """
        ...
