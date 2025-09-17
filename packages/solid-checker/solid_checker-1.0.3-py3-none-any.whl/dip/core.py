"""
🔍 DIP Analyzer: Core Analysis Module

Main components for analyzing the Dependency Inversion Principle.
Simple, focused implementation without unnecessary complexity.
"""

# Python imports
from ast import AST, AnnAssign, Attribute, Call, ClassDef, FunctionDef, Import, ImportFrom, Name, NodeVisitor

# Local imports
from .protocols import (
    AbstractionDetectorProtocol,
    ClassAnalysis,
    DependencyClassifierProtocol,
    DependencyInfo,
    DIPViolation,
)


# ============================================================================
# ABSTRACTION DETECTION
# ============================================================================


class AbstractionDetector:
    """Detects abstractions in code - simple and focused"""

    def __init__(self) -> None:
        """Initialize the abstraction detector."""
        # Patterns for abstractions
        self.abstraction_patterns = {
            "abc_classes": ["ABC", "abstractmethod"],
            "protocols": ["Protocol", "runtime_checkable"],
            "typing": ["Union", "Optional", "Any", "TypeVar", "Generic"],
            "common_abstractions": ["Interface", "Handler", "Processor", "Service", "Repository", "Factory"],
        }

    def is_abstraction_name(self, name: str) -> bool:
        """
        Check if name indicates abstraction

        Args:
            name: The name to check

        Returns:
            True if name indicates abstraction, False otherwise
        """
        name_lower = name.lower()

        # Common abstraction suffixes
        abstraction_suffixes = ["interface", "protocol", "abstract", "base"]
        abstraction_prefixes = ["i", "abstract", "base"]

        for suffix in abstraction_suffixes:
            if name_lower.endswith(suffix):
                return True

        for prefix in abstraction_prefixes:
            if name_lower.startswith(prefix) and len(name) > len(prefix):
                return True

        # Check known abstraction patterns
        return any(name in pattern_list for pattern_list in self.abstraction_patterns.values())


# ============================================================================
# DEPENDENCY CLASSIFIER
# ============================================================================


class DependencyClassifier:
    """Classifies dependencies - simple strategy"""

    def __init__(self, abstraction_detector: AbstractionDetectorProtocol) -> None:
        """
        Initialize the dependency classifier.

        Args:
            abstraction_detector: The abstraction detector to use
        """
        self.abstraction_detector = abstraction_detector
        # Patterns for concrete classes (often violating DIP)
        self.concrete_patterns = [
            "Connection",
            "Session",
            "Client",
            "Manager",
            "Controller",
            "Database",
            "File",
            "Http",
            "Socket",
            "Thread",
            "Process",
        ]

    def classify_dependency(self, name: str) -> str:
        """
        Classify dependency as hard, soft or abstraction

        Args:
            name: The name of the dependency to classify

        Returns:
            The classification of the dependency
        """
        if self.abstraction_detector.is_abstraction_name(name):
            return "abstraction"

        # Check concrete class patterns
        name_lower = name.lower()
        for pattern in self.concrete_patterns:
            if pattern.lower() in name_lower:
                return "hard"

        # Default to soft dependency
        return "soft"


# ============================================================================
# MAIN DIP ANALYZER
# ============================================================================


class DIPAnalyzer(NodeVisitor):
    """Simple DIP analyzer - focused and straightforward"""

    def __init__(
        self, abstraction_detector: AbstractionDetectorProtocol, dependency_classifier: DependencyClassifierProtocol
    ) -> None:
        """
        Initialize the DIP analyzer.

        Args:
            abstraction_detector: The abstraction detector to use
            dependency_classifier: The dependency classifier to use
        """
        self.abstraction_detector = abstraction_detector
        self.dependency_classifier = dependency_classifier

        self.classes: dict[str, ClassAnalysis] = {}
        self.abstractions: set[str] = set()
        self.concrete_classes: set[str] = set()
        self.current_class: str | None = None
        self.current_method: str | None = None
        self.imports: dict[str, str] = {}  # alias -> full_name

    def visit_Import(self, node: Import) -> None:
        """
        Process imports

        Args:
            node: The import node to process
        """
        for alias in node.names:
            self.imports[alias.asname or alias.name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ImportFrom) -> None:
        """
        Process from...import statements

        Args:
            node: The import from node to process
        """
        if node.module:
            for alias in node.names:
                full_name = f"{node.module}.{alias.name}"
                self.imports[alias.asname or alias.name] = full_name
        self.generic_visit(node)

    def visit_ClassDef(self, node: ClassDef) -> None:
        """
        Analyze class definitions

        Args:
            node: The class definition node to analyze
        """
        self.current_class = node.name

        # Determine if class is abstraction
        is_abstraction = self._is_abstraction(node)
        if is_abstraction:
            self.abstractions.add(node.name)
        else:
            self.concrete_classes.add(node.name)

        # Initialize class analysis
        class_analysis = ClassAnalysis(
            name=node.name,
            hard_dependencies=[],
            soft_dependencies=[],
            abstractions_used=[],
            dependency_injections=[],
            creation_patterns=[],
            line_number=node.lineno,
        )

        # Analyze base classes
        for base in node.bases:
            base_name = self._extract_name(base)
            if base_name:
                if self.abstraction_detector.is_abstraction_name(base_name):
                    class_analysis.abstractions_used.append(
                        DependencyInfo(base_name, "abstraction", "inheritance", node.lineno)
                    )
                else:
                    class_analysis.hard_dependencies.append(
                        DependencyInfo(base_name, "hard", "inheritance", node.lineno)
                    )

        self.classes[node.name] = class_analysis
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: FunctionDef) -> None:
        """
        Analyze methods

        Args:
            node: The function definition node to analyze
        """
        if self.current_class:
            self.current_method = node.name

            # Special analysis for constructor
            if node.name == "__init__":
                self._analyze_constructor(node)

        self.generic_visit(node)
        self.current_method = None

    def visit_Call(self, node: Call) -> None:
        """
        Analyze function calls/instance creation

        Args:
            node: The call node to analyze
        """
        if self.current_class and self.current_method:
            call_name = self._extract_name(node.func)

            if call_name and self._is_instance_creation(call_name):
                context = "constructor" if self.current_method == "__init__" else "method"

                dependency_info = DependencyInfo(
                    name=call_name,
                    dependency_type=self.dependency_classifier.classify_dependency(call_name),
                    usage_context=context,
                    line_number=node.lineno,
                )

                class_analysis = self.classes[self.current_class]
                if dependency_info.dependency_type == "hard":
                    class_analysis.hard_dependencies.append(dependency_info)
                elif dependency_info.dependency_type == "abstraction":
                    class_analysis.abstractions_used.append(dependency_info)
                else:
                    class_analysis.soft_dependencies.append(dependency_info)

        self.generic_visit(node)

    def visit_AnnAssign(self, node: AnnAssign) -> None:
        """
        Analyze type annotations

        Args:
            node: The annotation assignment node to analyze
        """
        if self.current_class:
            type_name = self._extract_name(node.annotation)
            if type_name:
                class_analysis = self.classes[self.current_class]

                dependency_info = DependencyInfo(
                    name=type_name,
                    dependency_type=self.dependency_classifier.classify_dependency(type_name),
                    usage_context="field",
                    line_number=node.lineno,
                )

                if dependency_info.dependency_type == "abstraction":
                    class_analysis.abstractions_used.append(dependency_info)
                elif dependency_info.dependency_type == "hard":
                    class_analysis.hard_dependencies.append(dependency_info)

        self.generic_visit(node)

    def _is_abstraction(self, node: ClassDef) -> bool:
        """
        Check if class is abstraction

        Args:
            node: The class definition node to check
        """
        # Check base classes
        for base in node.bases:
            base_name = self._extract_name(base)
            if base_name in ["ABC", "Protocol"]:
                return True

        # Check for abstract methods
        for item in node.body:
            if isinstance(item, FunctionDef):
                for decorator in item.decorator_list:
                    if isinstance(decorator, Name) and decorator.id == "abstractmethod":
                        return True

        # Check name patterns
        return self.abstraction_detector.is_abstraction_name(node.name)

    def _extract_name(self, node: AST) -> str | None:
        """
        Extract name from AST node

        Args:
            node: The AST node to extract the name from

        Returns:
            The name extracted from the AST node
        """
        if isinstance(node, Name):
            return node.id
        elif isinstance(node, Attribute):
            value = self._extract_name(node.value)
            return f"{value}.{node.attr}" if value else node.attr
        return None

    def _is_instance_creation(self, name: str) -> bool:
        """
        Check if call creates instance

        Args:
            name: The name of the call to check

        Returns:
            True if call creates instance, False otherwise
        """
        if not name:
            return False

        # Simple heuristic: starts with uppercase
        if name[0].isupper():
            return True

        # Exclude common functions
        exclude_functions = {"print", "len", "str", "int", "float", "bool", "list", "dict", "set", "tuple"}
        return name not in exclude_functions

    def _analyze_constructor(self, node: FunctionDef) -> None:
        """
        Special constructor analysis

        Args:
            node: The function definition node to analyze
        """
        if not self.current_class:
            return

        class_analysis = self.classes[self.current_class]

        # Look for dependency injection patterns
        for arg in node.args.args[1:]:  # Skip self
            if arg.annotation:
                type_name = self._extract_name(arg.annotation)
                if type_name and self.abstraction_detector.is_abstraction_name(type_name):
                    class_analysis.dependency_injections.append(arg.arg)


# ============================================================================
# VIOLATION ANALYZER
# ============================================================================


class ViolationAnalyzer:
    """Analyzes DIP violations - simple and focused"""

    def analyze_violations(self, classes: dict[str, ClassAnalysis], abstractions: set[str]) -> list[DIPViolation]:
        """
        Analyze DIP violations

        Args:
            classes: The classes to analyze
            abstractions: The abstractions to skip

        Returns:
            The violations found
        """
        violations = []

        for class_name, class_analysis in classes.items():
            if class_name in abstractions:
                continue  # Skip abstractions

            violations.extend(self._check_hard_dependencies(class_analysis))
            violations.extend(self._check_constructor_violations(class_analysis))
            violations.extend(self._check_missing_abstractions(class_analysis))

        return violations

    def _check_hard_dependencies(self, class_analysis: ClassAnalysis) -> list[DIPViolation]:
        """
        Check hard dependencies

        Args:
            class_analysis: The class analysis to check

        Returns:
            The violations found
        """
        violations = []
        constructor_hard_deps = [dep for dep in class_analysis.hard_dependencies if dep.usage_context == "constructor"]

        if len(constructor_hard_deps) > 3:
            violations.append(
                DIPViolation(
                    class_name=class_analysis.name,
                    violation_type="too_many_hard_dependencies",
                    dependency_name=f"{len(constructor_hard_deps)} dependencies",
                    description=f"Class creates {len(constructor_hard_deps)} hard dependencies in constructor",
                    suggestion="Use dependency injection with interfaces instead of creating instances",
                    line_number=class_analysis.line_number,
                    severity="high",
                )
            )

        # Check each hard dependency
        for dep in constructor_hard_deps:
            violations.append(
                DIPViolation(
                    class_name=class_analysis.name,
                    violation_type="hard_dependency_in_constructor",
                    dependency_name=dep.name,
                    description=f"Hard dependency on {dep.name} created in constructor",
                    suggestion=f"Inject {dep.name} through constructor parameter or use factory",
                    line_number=dep.line_number,
                    severity="medium",
                )
            )

        return violations

    def _check_constructor_violations(self, class_analysis: ClassAnalysis) -> list[DIPViolation]:
        """
        Check constructor violations

        Args:
            class_analysis: The class analysis to check

        Returns:
            The violations found
        """
        violations = []
        hard_count = len([d for d in class_analysis.hard_dependencies if d.usage_context == "constructor"])
        injection_count = len(class_analysis.dependency_injections)

        if hard_count > 0 and injection_count == 0:
            violations.append(
                DIPViolation(
                    class_name=class_analysis.name,
                    violation_type="no_dependency_injection",
                    dependency_name="constructor",
                    description="Constructor creates dependencies instead of receiving them",
                    suggestion="Use constructor injection to receive dependencies as parameters",
                    line_number=class_analysis.line_number,
                    severity="high",
                )
            )

        return violations

    def _check_missing_abstractions(self, class_analysis: ClassAnalysis) -> list[DIPViolation]:
        """
        Check missing abstractions

        Args:
            class_analysis: The class analysis to check

        Returns:
            The violations found
        """
        violations = []
        total_deps = len(class_analysis.hard_dependencies) + len(class_analysis.soft_dependencies)
        abstraction_count = len(class_analysis.abstractions_used)

        if total_deps > 2 and abstraction_count == 0:
            violations.append(
                DIPViolation(
                    class_name=class_analysis.name,
                    violation_type="missing_abstractions",
                    dependency_name="dependencies",
                    description="Class depends on concrete implementations without abstractions",
                    suggestion="Define interfaces/protocols for dependencies",
                    line_number=class_analysis.line_number,
                    severity="medium",
                )
            )

        return violations


# ============================================================================
# DIP SCORER
# ============================================================================


class DIPScorer:
    """Simple DIP scoring - straightforward calculation"""

    def calculate_dip_score(
        self, classes: dict[str, ClassAnalysis], violations: list[DIPViolation], abstractions: set[str]
    ) -> float:
        """
        Calculate DIP score (0.0 - 1.0)

        Args:
            classes: The classes to analyze
            violations: The violations to analyze
            abstractions: The abstractions to skip

        Returns:
            The DIP score
        """
        if not classes:
            return 1.0

        score = 1.0

        # Penalties for violations
        for violation in violations:
            if violation.severity == "high":
                score -= 0.25
            elif violation.severity == "medium":
                score -= 0.15
            elif violation.severity == "low":
                score -= 0.05

        # Bonus for using abstractions
        total_classes = len([name for name, analysis in classes.items() if name not in abstractions])

        if total_classes > 0:
            classes_with_abstractions = sum(1 for analysis in classes.values() if analysis.abstractions_used)
            abstraction_ratio = classes_with_abstractions / total_classes
            bonus = abstraction_ratio * 0.1
            score += bonus

        # Bonus for dependency injection
        classes_with_di = sum(1 for analysis in classes.values() if analysis.dependency_injections)
        if classes_with_di > 0:
            di_bonus = min(0.1, classes_with_di * 0.02)
            score += di_bonus

        return max(0.0, min(1.0, score))

    def generate_recommendations(self, classes: dict[str, ClassAnalysis], violations: list[DIPViolation]) -> list[str]:
        """
        Generate recommendations

        Args:
            classes: The classes to analyze
            violations: The violations to analyze

        Returns:
            The recommendations
        """
        recommendations = []

        if not violations:
            recommendations.append("Great! Code follows DIP well - dependencies are properly abstracted")
            return recommendations

        violation_types = {v.violation_type for v in violations}

        if "hard_dependency_in_constructor" in violation_types:
            recommendations.append("Replace constructor instantiation with dependency injection")
            recommendations.append("Define interfaces/protocols for external dependencies")

        if "too_many_hard_dependencies" in violation_types:
            recommendations.append("Reduce number of dependencies or use facade/mediator pattern")

        if "no_dependency_injection" in violation_types:
            recommendations.append("Implement constructor injection pattern")

        if "missing_abstractions" in violation_types:
            recommendations.append("Create interfaces/protocols to depend on abstractions, not concretions")

        # Specific examples
        high_severity_violations = [v for v in violations if v.severity == "high"]
        if high_severity_violations:
            worst_class = high_severity_violations[0]
            recommendations.append(f"Priority: Fix {worst_class.class_name} - {worst_class.description}")

        return recommendations
