"""
🔍 SRP Analyzer: Core Analysis Module

Main collectors, analyzers and scorer for SRP analysis.
Simple, focused implementation without complex IoC infrastructure.
"""

# Python imports
from ast import Attribute, Call, ClassDef, FunctionDef, Import, ImportFrom, NodeVisitor
from typing import Any, ClassVar

# Local imports
from .protocols import (
    AttributeExtractor,
    CallExtractor,
    ClassCollectorProtocol,
    ImportCollectorProtocol,
    InstanceDetector,
)


# ============================================================================
# SIMPLE EXTRACTORS (without Registry Pattern for simplicity)
# ============================================================================


class SimpleCallExtractor:
    """Simple call extractor without registry complexity"""

    def extract(self, node: Call) -> str:
        """
        Extract call information from Call node

        Args:
            node: The call node to extract information from

        Returns:
            The call information
        """
        if hasattr(node.func, "id"):
            return str(node.func.id)
        elif hasattr(node.func, "attr"):
            if hasattr(node.func, "value") and hasattr(node.func.value, "id"):
                return f"{node.func.value.id}.{node.func.attr}"
            return f"unknown.{node.func.attr}"
        return "unknown_call"


class SimpleInstanceDetector:
    """Simple instance detector without complex patterns"""

    def is_instance_creation(self, node: Call) -> bool:
        """
        Detect if call creates an instance (CamelCase heuristic)

        Args:
            node: The call node to check

        Returns:
            True if the call creates an instance, False otherwise
        """
        if hasattr(node.func, "id"):
            return node.func.id[0].isupper() if node.func.id else False
        return False


class SimpleAttributeExtractor:
    """Simple attribute extractor"""

    def extract(self, node: Attribute) -> str:
        """
        Extract attribute information

        Args:
            node: The attribute node to extract information from

        Returns:
            The attribute information
        """
        if hasattr(node.value, "id"):
            return f"{node.value.id}.{node.attr}"
        return f"unknown.{node.attr}"


# ============================================================================
# CORE COLLECTORS
# ============================================================================


class ImportCollector:
    """Collects import information (Single Responsibility)"""

    def __init__(self) -> None:
        """Initialize the import collector."""
        self._imports: set[str] = set()

    @property
    def imports(self) -> set[str]:
        """
        Get the imports

        Returns:
            The imports
        """
        return self._imports

    def collect_import(self, node: Import) -> None:
        """
        Collect import statement

        Args:
            node: The import node to collect information from
        """
        for alias in node.names:
            self._imports.add(alias.name)

    def collect_import_from(self, node: ImportFrom) -> None:
        """
        Collect from...import statement

        Args:
            node: The import from node to collect information from
        """
        if node.module:
            for alias in node.names:
                self._imports.add(f"{node.module}.{alias.name}")


class ClassInfoCollector:
    """Collects class information (Single Responsibility)"""

    def __init__(self) -> None:
        """Initialize the class info collector."""
        self._classes: dict[str, dict[str, Any]] = {}

    @property
    def classes(self) -> dict[str, dict[str, Any]]:
        """
        Get the classes

        Returns:
            The classes
        """
        return self._classes

    def collect_class_def(self, node: ClassDef) -> None:
        """
        Collect class definition information

        Args:
            node: The class definition node to collect information from
        """
        # Simple extraction without complex polymorphism
        decorators = [d.id for d in node.decorator_list if hasattr(d, "id")]
        base_classes = [base.id for base in node.bases if hasattr(base, "id")]

        # Calculate lines
        lines = 0
        if hasattr(node, "end_lineno") and node.end_lineno and node.lineno:
            lines = node.end_lineno - node.lineno + 1

        self._classes[node.name] = {
            "methods": [],
            "external_calls": [],
            "instance_creations": [],
            "attributes": [],
            "decorators": decorators,
            "base_classes": base_classes,
            "lines": lines,
        }

        # Collect methods
        for item in node.body:
            if isinstance(item, FunctionDef):
                self._classes[node.name]["methods"].append(item.name)

    def add_external_call(self, class_name: str, call_info: str) -> None:
        """
        Add external call to class

        Args:
            class_name: The name of the class
            call_info: The information about the call
        """
        if class_name in self._classes:
            self._classes[class_name]["external_calls"].append(call_info)

    def add_instance_creation(self, class_name: str, call_info: str) -> None:
        """
        Add instance creation to class

        Args:
            class_name: The name of the class
            call_info: The information about the call
        """
        if class_name in self._classes:
            self._classes[class_name]["instance_creations"].append(call_info)


# ============================================================================
# MAIN ANALYZER (simple version without IoC)
# ============================================================================


class SimpleDependencyAnalyzer(NodeVisitor):
    """Simple dependency analyzer without IoC complexity"""

    def __init__(
        self,
        import_collector: ImportCollectorProtocol,
        class_collector: ClassCollectorProtocol,
        call_extractor: CallExtractor,
        instance_detector: InstanceDetector,
        attr_extractor: AttributeExtractor,
    ) -> None:
        """
        Initialize the dependency analyzer.

        Args:
            import_collector: The import collector to use
            class_collector: The class collector to use
            call_extractor: The call extractor to use
            instance_detector: The instance detector to use
            attr_extractor: The attribute extractor to use
        """
        self.import_collector = import_collector
        self.class_collector = class_collector
        self.call_extractor = call_extractor
        self.instance_detector = instance_detector
        self.attr_extractor = attr_extractor

        self.current_class: str | None = None
        self.current_method: str | None = None

    @property
    def classes(self) -> dict[str, dict[str, Any]]:
        """
        Get the classes

        Returns:
            The classes
        """
        return self.class_collector.classes

    @property
    def imports(self) -> set[str]:
        """
        Get the imports

        Returns:
            The imports
        """
        return self.import_collector.imports

    def visit_Import(self, node: Import) -> None:
        """
        Visit import node

        Args:
            node: The import node to visit
        """
        self.import_collector.collect_import(node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ImportFrom) -> None:
        """
        Visit import from node

        Args:
            node: The import from node to visit
        """
        self.import_collector.collect_import_from(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ClassDef) -> None:
        """
        Visit class definition node

        Args:
            node: The class definition node to visit
        """
        self.current_class = node.name
        self.class_collector.collect_class_def(node)
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: FunctionDef) -> None:
        """
        Visit function definition node

        Args:
            node: The function definition node to visit
        """
        if self.current_class:
            self.current_method = node.name
        self.generic_visit(node)
        self.current_method = None

    def visit_Call(self, node: Call) -> None:
        """
        Visit call node

        Args:
            node: The call node to visit
        """
        if self.current_class and self.current_method:
            call_info = self.call_extractor.extract(node)
            if call_info:
                self.class_collector.add_external_call(self.current_class, call_info)

                if self.instance_detector.is_instance_creation(node):
                    self.class_collector.add_instance_creation(self.current_class, call_info)

        self.generic_visit(node)

    def visit_Attribute(self, node: Attribute) -> None:
        """
        Visit attribute node

        Args:
            node: The attribute node to visit
        """
        if self.current_class and self.current_method:
            attr_info = self.attr_extractor.extract(node)
            if attr_info and attr_info not in self.classes[self.current_class]["external_calls"]:
                self.class_collector.add_external_call(self.current_class, attr_info)

        self.generic_visit(node)


# ============================================================================
# RESPONSIBILITY DETECTOR & SRP SCORER
# ============================================================================


class ResponsibilityDetector:
    """Detects class responsibilities - simple and focused"""

    RESPONSIBILITY_PATTERNS: ClassVar[dict[str, list[str]]] = {
        "database": ["db", "database", "sql", "query", "connection", "cursor", "execute"],
        "network": ["http", "request", "response", "api", "client", "server", "socket"],
        "file_io": ["file", "read", "write", "open", "save", "load", "path"],
        "validation": ["validate", "check", "verify", "ensure", "assert"],
        "logging": ["log", "logger", "debug", "info", "warning", "error"],
        "email": ["email", "mail", "smtp", "send_email", "notification"],
        "authentication": ["auth", "login", "logout", "password", "token", "session"],
        "business_logic": ["calculate", "compute", "process", "transform", "analyze"],
        "ui": ["render", "display", "show", "hide", "ui", "interface", "view"],
        "configuration": ["config", "settings", "options", "preferences"],
        "caching": ["cache", "cached", "memoize", "store", "retrieve"],
        "serialization": ["json", "xml", "serialize", "deserialize", "parse"],
    }

    def detect_responsibilities(self, class_info: dict[str, Any]) -> list[str]:
        """
        Detect class responsibilities

        Args:
            class_info: The class information

        Returns:
            The responsibilities
        """
        responsibilities = set()

        # Analyze methods, calls, and instances
        all_text = " ".join(class_info["methods"]).lower()
        all_text += " " + " ".join(class_info["external_calls"]).lower()
        all_text += " " + " ".join(class_info["instance_creations"]).lower()

        # Find patterns
        for responsibility, patterns in self.RESPONSIBILITY_PATTERNS.items():
            for pattern in patterns:
                if pattern in all_text:
                    responsibilities.add(responsibility)
                    break

        return list(responsibilities)


class SRPScorer:
    """Scores SRP compliance - simple and straightforward"""

    def calculate_srp_score(self, class_info: dict[str, Any], responsibilities: list[str]) -> float:
        """
        Calculate SRP score (0.0 - 1.0, where 1.0 is excellent)

        Args:
            class_info: The class information
            responsibilities: The responsibilities

        Returns:
            The SRP score
        """
        score = 1.0

        # Penalty for multiple responsibilities
        if len(responsibilities) > 1:
            score -= (len(responsibilities) - 1) * 0.2

        # Penalty for too many methods
        method_count = len(class_info["methods"])
        if method_count > 10:
            score -= (method_count - 10) * 0.02

        # Penalty for too many external dependencies
        external_deps = len(set(class_info["external_calls"]))
        if external_deps > 5:
            score -= (external_deps - 5) * 0.05

        # Penalty for instance creation (DIP violation)
        instance_creations = len(class_info["instance_creations"])
        if instance_creations > 2:
            score -= instance_creations * 0.1

        return max(0.0, min(1.0, score))

    def identify_violations(self, class_info: dict[str, Any], responsibilities: list[str]) -> list[str]:
        """
        Identify specific SRP violations

        Args:
            class_info: The class information
            responsibilities: The responsibilities

        Returns:
            The violations
        """
        violations = []

        if len(responsibilities) > 1:
            violations.append(f"Multiple responsibilities: {', '.join(responsibilities)}")

        method_count = len(class_info["methods"])
        if method_count > 15:
            violations.append(f"Too many methods: {method_count} (consider splitting)")

        if len(class_info["instance_creations"]) > 3:
            violations.append("Creates too many instances (possible DIP violation)")

        external_deps = len(set(class_info["external_calls"]))
        if external_deps > 10:
            violations.append(f"Too many external dependencies: {external_deps}")

        return violations


# ============================================================================
# SCORE CALCULATOR
# ============================================================================


class EmojiScoreCalculator:
    """Calculates emoji representation for scores"""

    def get_score_emoji(self, score: float) -> str:
        """
        Get the score emoji

        Args:
            score: The score

        Returns:
            The score emoji
        """
        if score >= 0.8:
            return "🟢"
        elif score >= 0.6:
            return "🟡"
        else:
            return "🔴"
