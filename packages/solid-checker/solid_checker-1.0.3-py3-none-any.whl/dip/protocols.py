"""
🔍 DIP Analyzer: Protocols & Data Structures Module

All protocols, abstractions and data structures for DIP analyzer.
Follows the Interface Segregation Principle (ISP).
"""

# Python imports
from dataclasses import dataclass
from typing import Protocol


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class DependencyInfo:
    """Information about class dependency"""

    name: str
    dependency_type: str  # 'hard', 'soft', 'abstraction'
    usage_context: str  # 'constructor', 'method', 'field'
    line_number: int


@dataclass
class ClassAnalysis:
    """Class analysis from DIP perspective"""

    name: str
    hard_dependencies: list[DependencyInfo]
    soft_dependencies: list[DependencyInfo]
    abstractions_used: list[DependencyInfo]
    dependency_injections: list[str]
    creation_patterns: list[str]
    line_number: int


@dataclass
class DIPViolation:
    """DIP principle violation"""

    class_name: str
    violation_type: str
    dependency_name: str
    description: str
    suggestion: str
    line_number: int
    severity: str  # 'high', 'medium', 'low'


@dataclass
class DIPAnalysisResult:
    """Complete DIP analysis result"""

    file_path: str
    classes: dict[str, ClassAnalysis]
    abstractions: set[str]
    concrete_classes: set[str]
    violations: list[DIPViolation]
    dip_score: float
    recommendations: list[str]


# ============================================================================
# PROTOCOLS
# ============================================================================


class AbstractionDetectorProtocol(Protocol):
    """Protocol for abstraction detection"""

    def is_abstraction_name(self, name: str) -> bool:
        """
        Check if name indicates abstraction

        Args:
            name: The name to check

        Returns:
            True if name indicates abstraction, False otherwise
        """
        ...


class DependencyClassifierProtocol(Protocol):
    """Protocol for dependency classification"""

    def classify_dependency(self, name: str) -> str:
        """
        Classify dependency as hard, soft or abstraction

        Args:
            name: The name of the dependency to classify

        Returns:
            The classification of the dependency
        """
        ...


class ViolationAnalyzerProtocol(Protocol):
    """Protocol for DIP violation analysis"""

    def analyze_violations(self, classes: dict[str, ClassAnalysis], abstractions: set[str]) -> list[DIPViolation]:
        """
        Analyze and find DIP violations

        Args:
            classes: The classes to analyze
            abstractions: The abstractions to skip

        Returns:
            The violations found
        """
        ...


class DIPScorerProtocol(Protocol):
    """Protocol for DIP scoring"""

    def calculate_dip_score(
        self, classes: dict[str, ClassAnalysis], violations: list[DIPViolation], abstractions: set[str]
    ) -> float:
        """
        Calculate DIP compliance score

        Args:
            classes: The classes to analyze
            violations: The violations to analyze
            abstractions: The abstractions to skip

        Returns:
            The DIP score
        """
        ...

    def generate_recommendations(self, classes: dict[str, ClassAnalysis], violations: list[DIPViolation]) -> list[str]:
        """
        Generate improvement recommendations

        Args:
            classes: The classes to analyze
            violations: The violations to analyze

        Returns:
            The recommendations
        """
        ...
