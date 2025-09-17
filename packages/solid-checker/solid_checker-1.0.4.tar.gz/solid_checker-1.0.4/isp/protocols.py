"""
🔍 ISP Analyzer: Protocols & Data Structures Module

All protocols, abstractions and data structures for ISP analyzer.
Follows the Interface Segregation Principle (ISP).
"""

# Python imports
from dataclasses import dataclass
from typing import Any, Protocol


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class InterfaceInfo:
    """Information about interface/protocol"""

    name: str
    methods: list[str]
    abstract_methods: list[str]
    line_number: int
    is_protocol: bool
    is_abstract_class: bool
    method_groups: dict[str, list[str]]  # Method grouping by functionality


@dataclass
class ISPViolation:
    """ISP principle violation"""

    interface_name: str
    violation_type: str
    method_count: int
    unused_methods: list[str]
    cohesion_groups: list[list[str]]
    description: str
    suggestion: str
    line_number: int


@dataclass
class ISPAnalysisResult:
    """Complete ISP analysis result"""

    file_path: str
    interfaces: dict[str, InterfaceInfo]
    implementations: dict[str, list[str]]
    violations: list[ISPViolation]
    isp_score: float
    suggestions: list[str]


# ============================================================================
# PROTOCOLS
# ============================================================================


class InterfaceDetectorProtocol(Protocol):
    """Protocol for interface detection"""

    def is_protocol(self, node: Any) -> bool:
        """
        Check if class is a Protocol

        Args:
            node: The class definition node to check

        Returns:
            True if class is a Protocol, False otherwise
        """
        ...

    def is_abstract_class(self, node: Any) -> bool:
        """
        Check if class is abstract

        Args:
            node: The class definition node to check

        Returns:
            True if class is abstract, False otherwise
        """
        ...


class MethodGrouperProtocol(Protocol):
    """Protocol for method grouping by functionality"""

    def group_methods(self, methods: list[str]) -> dict[str, list[str]]:
        """
        Group methods by functional areas

        Args:
            methods: The methods to group

        Returns:
            The grouped methods
        """
        ...


class ViolationDetectorProtocol(Protocol):
    """Protocol for ISP violation detection"""

    def check_fat_interface(self, interface_info: InterfaceInfo) -> ISPViolation | None:
        """
        Check for fat interface violations

        Args:
            interface_info: The interface to check

        Returns:
            The violation if found, None otherwise
        """
        ...

    def check_low_cohesion(self, interface_info: InterfaceInfo) -> ISPViolation | None:
        """
        Check for low cohesion violations

        Args:
            interface_info: The interface to check

        Returns:
            The violation if found, None otherwise
        """
        ...


class ISPScorerProtocol(Protocol):
    """Protocol for ISP scoring"""

    def calculate_isp_score(self, interfaces: dict[str, InterfaceInfo], violations: list[ISPViolation]) -> float:
        """
        Calculate ISP compliance score

        Args:
            interfaces: The interfaces to analyze
            violations: The violations to analyze

        Returns:
            The ISP score
        """
        ...

    def generate_suggestions(self, interfaces: dict[str, InterfaceInfo], violations: list[ISPViolation]) -> list[str]:
        """
        Generate improvement suggestions

        Args:
            interfaces: The interfaces to analyze
            violations: The violations to analyze

        Returns:
            The suggestions
        """
        ...
