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
    """Enhanced SRP scorer with contextual and architectural awareness"""

    def __init__(self) -> None:
        """Initialize the improved SRP scorer."""
        # Architectural patterns that justify multiple related components
        self.domain_patterns = {
            "analyzers": ["analyze", "detect", "check", "validate", "scan"],
            "processors": ["process", "transform", "convert", "handle"],
            "collectors": ["collect", "gather", "extract", "fetch"],
            "builders": ["build", "create", "construct", "generate"],
            "managers": ["manage", "coordinate", "orchestrate", "control"],
            "utils": ["format", "parse", "validate", "normalize"]
        }

    def calculate_srp_score(self, class_info: dict[str, Any], responsibilities: list[str]) -> float:
        """
        Calculate improved SRP score with contextual awareness

        Args:
            class_info: The class information
            responsibilities: The responsibilities

        Returns:
            The SRP score (0.0 - 1.0)
        """
        class_name = class_info.get("name", "Unknown")
        method_count = len(class_info["methods"])
        external_deps = len(set(class_info["external_calls"]))
        instance_creations = len(class_info["instance_creations"])

        # Determine class archetype for context-aware scoring
        class_type = self._determine_class_type(class_name, responsibilities)

        # Base score starts high
        score = 1.0

        # 1. IMPROVED: Contextual responsibility analysis
        if len(responsibilities) > 1:
            cohesion_bonus = self._calculate_cohesion_bonus(responsibilities, class_type)
            penalty = self._calculate_responsibility_penalty(len(responsibilities), class_type)
            score -= penalty - cohesion_bonus  # Bonus can reduce penalty

        # 2. IMPROVED: Adaptive method count thresholds
        method_threshold = self._get_adaptive_method_threshold(class_type)
        if method_count > method_threshold:
            # Softer penalty curve
            excess = method_count - method_threshold
            score -= min(excess * 0.015, 0.3)  # Cap at 0.3 penalty

        # 3. IMPROVED: Context-aware dependency analysis
        dep_threshold = self._get_adaptive_dependency_threshold(class_type)
        if external_deps > dep_threshold:
            excess = external_deps - dep_threshold
            score -= min(excess * 0.03, 0.25)  # Softer penalty

        # 4. UNCHANGED: Instance creation penalty (still valid)
        if instance_creations > 2:
            score -= min(instance_creations * 0.08, 0.2)  # Softer penalty

        # 5. NEW: Architectural bonus for well-designed classes
        architectural_bonus = self._calculate_architectural_bonus(class_name, class_type)
        score += architectural_bonus

        return max(0.0, min(1.0, score))

    def _determine_class_type(self, class_name: str, responsibilities: list[str]) -> str:
        """Determine the architectural type of the class"""
        name_lower = class_name.lower()

        # Check for architectural patterns in class name
        for pattern_type, keywords in self.domain_patterns.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return pattern_type

        # Check responsibilities for patterns
        all_resp = " ".join(responsibilities).lower()
        for pattern_type, keywords in self.domain_patterns.items():
            if any(keyword in all_resp for keyword in keywords):
                return pattern_type

        return "generic"

    def _calculate_cohesion_bonus(self, responsibilities: list[str], class_type: str) -> float:
        """Calculate bonus for cohesive responsibilities within same domain"""
        if len(responsibilities) <= 1:
            return 0.0

        # Check if responsibilities are related to the same domain
        domain_keywords = self.domain_patterns.get(class_type, [])
        related_count = 0

        for resp in responsibilities:
            resp_lower = resp.lower()
            if any(keyword in resp_lower for keyword in domain_keywords):
                related_count += 1

        # If most responsibilities are domain-related, give bonus
        cohesion_ratio = related_count / len(responsibilities)
        if cohesion_ratio >= 0.7:  # 70% related
            return min(0.15, cohesion_ratio * 0.2)  # Up to 0.15 bonus

        return 0.0

    def _calculate_responsibility_penalty(self, resp_count: int, class_type: str) -> float:
        """Calculate context-aware responsibility penalty"""
        if resp_count <= 1:
            return 0.0

        base_penalty = (resp_count - 1) * 0.15  # Reduced from 0.2

        # Architectural classes can handle more responsibilities
        if class_type in ["analyzers", "processors", "managers"]:
            if resp_count <= 4:  # Allow up to 4 related responsibilities
                base_penalty *= 0.5  # Half penalty

        return min(base_penalty, 0.5)  # Cap penalty

    def _get_adaptive_method_threshold(self, class_type: str) -> int:
        """Get adaptive method count threshold based on class type"""
        thresholds = {
            "analyzers": 20,      # Analyzers can have many methods
            "processors": 15,     # Processors need more methods
            "collectors": 12,     # Collectors moderate complexity
            "builders": 12,       # Builders moderate complexity
            "managers": 18,       # Managers coordinate many operations
            "utils": 8,           # Utils should stay simple
            "generic": 10         # Default threshold
        }
        return thresholds.get(class_type, 10)

    def _get_adaptive_dependency_threshold(self, class_type: str) -> int:
        """Get adaptive dependency threshold based on class type"""
        thresholds = {
            "analyzers": 10,      # Analyzers use many libraries
            "processors": 8,      # Processors need various tools
            "collectors": 6,      # Collectors moderate dependencies
            "builders": 7,        # Builders need components
            "managers": 8,        # Managers coordinate systems
            "utils": 4,           # Utils should be focused
            "generic": 5          # Default threshold
        }
        return thresholds.get(class_type, 5)

    def _calculate_architectural_bonus(self, class_name: str, class_type: str) -> float:
        """Calculate bonus for good architectural patterns"""
        bonus = 0.0
        name_lower = class_name.lower()

        # Bonus for clear naming patterns
        if any(pattern in name_lower for pattern in ["detector", "analyzer", "processor", "manager"]):
            bonus += 0.05

        # Bonus for domain-specific classes (not generic)
        if class_type != "generic":
            bonus += 0.03

        return min(bonus, 0.08)  # Cap architectural bonus

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
