"""
🔍 OCP Analyzer: Protocols & Data Structures Module

All protocols, abstractions and data structures for OCP analyzer.
Follows the Interface Segregation Principle (ISP).
"""

# Python imports
from dataclasses import dataclass
from typing import Protocol


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class OCPViolation:
    """OCP principle violation"""

    type: str
    class_name: str
    method_name: str
    line_number: int
    description: str
    suggestion: str


@dataclass
class OCPAnalysisResult:
    """Complete OCP analysis result"""

    file_path: str
    violations: list[OCPViolation]
    ocp_score: float
    extensibility_points: list[str]
    rigid_constructs: list[str]


# ============================================================================
# PROTOCOLS
# ============================================================================


class AbstractionDetectorProtocol(Protocol):
    """Protocol for detecting abstractions in code"""

    def detect_abstract_methods(self) -> set[str]:
        """
        Detect abstract methods

        Returns:
            The abstract methods
        """
        ...

    def detect_protocols(self) -> set[str]:
        """
        Detect protocols

        Returns:
            The protocols
        """
        ...

    def add_abstract_method(self, class_name: str, method_name: str) -> None:
        """
        Add abstract method

        Args:
            class_name: The name of the class
            method_name: The name of the method
        """
        ...

    def add_protocol(self, class_name: str) -> None:
        """
        Add protocol

        Args:
            class_name: The name of the class
        """
        ...


class RigidityDetectorProtocol(Protocol):
    """Protocol for detecting rigid constructs"""

    def detect_if_elif_chains(self) -> dict[str, list[tuple[int, str]]]:
        """
        Detect if-elif chains

        Returns:
            The if-elif chains
        """
        ...

    def detect_type_checks(self) -> list[tuple[str, str, int]]:
        """
        Detect type checking

        Returns:
            The type checks
        """
        ...

    def detect_switch_statements(self) -> list[tuple[str, str, int]]:
        """
        Detect switch statements

        Returns:
            The switch statements
        """
        ...

    def add_if_elif_chain(self, method_key: str, line_no: int, condition: str) -> None:
        """
        Add if-elif chain

        Args:
            method_key: The key of the method
            line_no: The line number
            condition: The condition
        """
        ...

    def add_type_check(self, method_key: str, type_check: str, line_no: int) -> None:
        """
        Add type check

        Args:
            method_key: The key of the method
            type_check: The type check
            line_no: The line number
        """
        ...

    def add_switch_statement(self, method_key: str, switch_desc: str, line_no: int) -> None:
        """
        Add switch statement

        Args:
            method_key: The key of the method
            switch_desc: The switch description
            line_no: The line number
        """
        ...


class ViolationAnalyzerProtocol(Protocol):
    """Protocol for OCP violation analysis"""

    def analyze_violations(
        self,
        if_elif_chains: dict[str, list[tuple[int, str]]],
        type_checks: list[tuple[str, str, int]],
        switch_statements: list[tuple[str, str, int]],
    ) -> list[OCPViolation]:
        """
        Analyze OCP violations

        Args:
            if_elif_chains: The if-elif chains to analyze
            type_checks: The type checks to analyze
            switch_statements: The switch statements to analyze

        Returns:
            The violations found
        """
        ...


class OCPScorerProtocol(Protocol):
    """Protocol for OCP scoring"""

    def calculate_ocp_score(
        self, violations: list[OCPViolation], abstract_methods_count: int, protocols_count: int
    ) -> float:
        """
        Calculate OCP compliance score

        Args:
            violations: list[OCPViolation],
            abstract_methods_count: int,
            protocols_count: int

        Returns:
            The OCP score
        """
        ...

    def identify_extensibility_points(self, abstract_methods: set[str], protocols: set[str]) -> list[str]:
        """
        Identify extensibility points

        Args:
            abstract_methods: The abstract methods
            protocols: The protocols

        Returns:
            The extensibility points
        """
        ...

    def identify_rigid_constructs(self, violations: list[OCPViolation]) -> list[str]:
        """
        Identify rigid constructs

        Args:
            violations: The violations to analyze

        Returns:
            The rigid constructs
        """
        ...
