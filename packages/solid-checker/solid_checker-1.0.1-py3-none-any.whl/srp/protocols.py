"""
🔍 SRP Analyzer: Protocols Module

All protocols and abstractions for SRP analyzer.
Follows the Interface Segregation Principle (ISP).
"""

# Python imports
from ast import AST, Attribute, Call, ClassDef, Import, ImportFrom
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol


# ============================================================================
# CORE ANALYSIS PROTOCOLS
# ============================================================================


class CallExtractor(Protocol):
    """Protocol for extracting call information"""

    def extract(self, node: Call) -> str:
        """
        Extract call information from AST node

        Args:
            node: The call node to extract information from

        Returns:
            The call information
        """
        ...


class InstanceDetector(Protocol):
    """Protocol for detecting instance creation"""

    def is_instance_creation(self, node: Call) -> bool:
        """
        Detect if call creates an instance

        Args:
            node: The call node to check

        Returns:
            True if the call creates an instance, False otherwise
        """
        ...


class AttributeExtractor(Protocol):
    """Protocol for extracting attribute information"""

    def extract(self, node: Attribute) -> str:
        """
        Extract attribute information from AST node

        Args:
            node: The attribute node to extract information from

        Returns:
            The attribute information
        """
        ...


class ImportCollectorProtocol(Protocol):
    """Protocol for import collection"""

    @property
    def imports(self) -> set[str]:
        """
        Get collected imports

        Returns:
            The collected imports
        """
        ...

    def collect_import(self, node: Import) -> None:
        """
        Collect import statement

        Args:
            node: The import node to collect information from
        """
        ...

    def collect_import_from(self, node: ImportFrom) -> None:
        """
        Collect from...import statement

        Args:
            node: The import from node to collect information from
        """
        ...


class ClassCollectorProtocol(Protocol):
    """Protocol for class information collection"""

    @property
    def classes(self) -> dict[str, dict[str, Any]]:
        """
        Get collected classes

        Returns:
            The collected classes
        """
        ...

    def collect_class_def(self, node: ClassDef) -> None:
        """
        Collect class definition

        Args:
            node: The class definition node to collect information from
        """
        ...

    def add_external_call(self, class_name: str, call_info: str) -> None:
        """
        Add external call

        Args:
            class_name: The name of the class
            call_info: The information about the call
        """
        ...

    def add_instance_creation(self, class_name: str, call_info: str) -> None:
        """
        Add instance creation

        Args:
            class_name: The name of the class
            call_info: The information about the call
        """
        ...


class ResponsibilityDetectorProtocol(Protocol):
    """Protocol for responsibility detection"""

    def detect_responsibilities(self, class_info: dict[str, Any]) -> list[str]:
        """
        Detect class responsibilities

        Args:
            class_info: The class information

        Returns:
            The responsibilities
        """
        ...


class SRPScorerProtocol(Protocol):
    """Protocol for SRP scoring"""

    def calculate_srp_score(self, class_info: dict[str, Any], responsibilities: list[str]) -> float:
        """
        Calculate SRP score

        Args:
            class_info: The class information
            responsibilities: The responsibilities

        Returns:
            The SRP score
        """
        ...

    def identify_violations(self, class_info: dict[str, Any], responsibilities: list[str]) -> list[str]:
        """
        Identify SRP violations

        Args:
            class_info: The class information
            responsibilities: The responsibilities

        Returns:
            The violations
        """
        ...


class ScoreCalculator(Protocol):
    """Protocol for score calculation strategies"""

    def get_score_emoji(self, score: float) -> str:
        """
        Get emoji for score visualization

        Args:
            score: The score

        Returns:
            The score emoji
        """
        ...


# ============================================================================
# HANDLER PROTOCOLS
# ============================================================================


class HandlerRegistry(Protocol):
    """Protocol for AST node handler registries"""

    def register(self, node_type: type[AST], handler: Callable[[AST], str]) -> None:
        """
        Register a handler for specific AST node type

        Args:
            node_type: The type of the AST node
            handler: The handler to register
        """
        ...

    def handle(self, node: AST) -> str:
        """
        Handle node using registered handler

        Args:
            node: The node to handle

        Returns:
            The handled node
        """
        ...


class HandlerMapper(Protocol):
    """Protocol for handler mapping abstraction"""

    def get_handler(self, handler_name: str) -> Callable[[AST], str]:
        """
        Get handler by name

        Args:
            handler_name: The name of the handler

        Returns:
            The handler
        """
        ...


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class DependencyInfo:
    """Information about class dependencies and SRP compliance"""

    class_name: str
    imports: set[str]
    external_calls: list[str]
    instance_creations: list[str]
    method_count: int
    responsibilities: list[str]
    srp_score: float
    violations: list[str]
