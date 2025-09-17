"""
🔍 ISP Analyzer: Core Analysis Module

Основные компоненты анализа принципа разделения интерфейсов.
Простая, фокусированная реализация без лишней сложности.
"""

# Python imports
from ast import Attribute, ClassDef, FunctionDef, Name, NodeVisitor
from collections import defaultdict

# Local imports
from .protocols import InterfaceDetectorProtocol, InterfaceInfo, ISPViolation, MethodGrouperProtocol


# ============================================================================
# INTERFACE DETECTION
# ============================================================================


class InterfaceDetector:
    """Detects interfaces and protocols - simple and focused"""

    def is_protocol(self, node: ClassDef) -> bool:
        """
        Check if class is Protocol

        Args:
            node: The class definition node to check

        Returns:
            True if class is Protocol, False otherwise
        """
        for base in node.bases:
            if isinstance(base, Name) and base.id == "Protocol":
                return True
            elif isinstance(base, Attribute):
                attr_name = self._extract_attribute_name(base)
                if "Protocol" in attr_name:
                    return True
        return False

    def is_abstract_class(self, node: ClassDef) -> bool:
        """
        Check if class is abstract

        Args:
            node: The class definition node to check

        Returns:
            True if class is abstract, False otherwise
        """
        # Check inheritance from ABC
        for base in node.bases:
            if isinstance(base, Name) and base.id == "ABC":
                return True

        # Check for abstract methods
        for item in node.body:
            if isinstance(item, FunctionDef):
                if self._is_abstract_method(item):
                    return True

        return False

    def _is_abstract_method(self, node: FunctionDef) -> bool:
        """
        Check if method is abstract

        Args:
            node: The function definition node to check

        Returns:
            True if method is abstract, False otherwise
        """
        for decorator in node.decorator_list:
            if isinstance(decorator, Name) and decorator.id == "abstractmethod":
                return True
        return False

    def _extract_attribute_name(self, node: Attribute) -> str:
        """
        Extract attribute name

        Args:
            node: The attribute node to extract the name from

        Returns:
            The name of the attribute
        """
        if isinstance(node.value, Name):
            return f"{node.value.id}.{node.attr}"
        else:
            return node.attr


# ============================================================================
# METHOD GROUPING
# ============================================================================


class MethodGrouper:
    """Groups methods by functionality - simple pattern matching"""

    def __init__(self) -> None:
        """Initialize the method grouper."""
        # Patterns for method grouping
        self.method_patterns = {
            "crud": ["create", "read", "update", "delete", "save", "load", "find", "get", "set"],
            "validation": ["validate", "check", "verify", "ensure", "is_valid", "has_valid"],
            "notification": ["notify", "send", "alert", "broadcast", "publish"],
            "authentication": ["login", "logout", "authenticate", "authorize", "is_authorized"],
            "serialization": ["serialize", "deserialize", "to_json", "from_json", "to_dict", "from_dict"],
            "lifecycle": ["start", "stop", "pause", "resume", "restart", "shutdown", "initialize"],
            "rendering": ["render", "draw", "paint", "display", "show", "hide"],
            "calculation": ["calculate", "compute", "process", "transform", "convert"],
            "io": ["read", "write", "open", "close", "flush", "seek"],
            "comparison": ["compare", "equals", "matches", "is_equal", "is_same"],
        }

    def group_methods(self, methods: list[str]) -> dict[str, list[str]]:
        """
        Group methods by functional areas

        Args:
            methods: The methods to group

        Returns:
            The grouped methods
        """
        groups = defaultdict(list)
        ungrouped = []

        for method in methods:
            method_lower = method.lower()
            grouped = False

            for group_name, patterns in self.method_patterns.items():
                for pattern in patterns:
                    if pattern in method_lower:
                        groups[group_name].append(method)
                        grouped = True
                        break
                if grouped:
                    break

            if not grouped:
                ungrouped.append(method)

        if ungrouped:
            groups["other"] = ungrouped

        return dict(groups)


# ============================================================================
# MAIN ISP ANALYZER
# ============================================================================


class ISPAnalyzer(NodeVisitor):
    """Simple ISP analyzer - focused and straightforward"""

    def __init__(self, interface_detector: InterfaceDetectorProtocol, method_grouper: MethodGrouperProtocol) -> None:
        """Initialize the ISP analyzer."""
        self.interface_detector = interface_detector
        self.method_grouper = method_grouper

        self.interfaces: dict[str, InterfaceInfo] = {}
        self.implementations: dict[str, list[str]] = defaultdict(list)  # class -> list of interfaces
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ClassDef) -> None:
        """
        Analyze class definitions

        Args:
            node: The class definition node to analyze
        """
        self.current_class = node.name

        # Check if it's interface/protocol
        is_protocol = self.interface_detector.is_protocol(node)
        is_abstract_class = self.interface_detector.is_abstract_class(node)

        if is_protocol or is_abstract_class:
            methods = []
            abstract_methods = []

            # Collect methods
            for item in node.body:
                if isinstance(item, FunctionDef):
                    methods.append(item.name)

                    # Check abstract methods
                    if self._is_abstract_method(item):
                        abstract_methods.append(item.name)

            # Group methods by functionality
            method_groups = self.method_grouper.group_methods(methods)

            self.interfaces[node.name] = InterfaceInfo(
                name=node.name,
                methods=methods,
                abstract_methods=abstract_methods,
                line_number=node.lineno,
                is_protocol=is_protocol,
                is_abstract_class=is_abstract_class,
                method_groups=method_groups,
            )
        else:
            # Regular class - check what it implements
            base_interfaces = []
            for base in node.bases:
                if isinstance(base, Name):
                    base_interfaces.append(base.id)
                elif isinstance(base, Attribute):
                    base_interfaces.append(self._extract_attribute_name(base))

            if base_interfaces:
                self.implementations[node.name] = base_interfaces

        self.generic_visit(node)
        self.current_class = None

    def _is_abstract_method(self, node: FunctionDef) -> bool:
        """
        Check if method is abstract

        Args:
            node: The function definition node to check

        Returns:
            True if method is abstract, False otherwise
        """
        for decorator in node.decorator_list:
            if isinstance(decorator, Name) and decorator.id == "abstractmethod":
                return True
        return False

    def _extract_attribute_name(self, node: Attribute) -> str:
        """
        Extract attribute name

        Args:
            node: The attribute node to extract the name from

        Returns:
            The name of the attribute
        """
        if isinstance(node.value, Name):
            return f"{node.value.id}.{node.attr}"
        else:
            return node.attr


# ============================================================================
# VIOLATION DETECTION
# ============================================================================


class ViolationDetector:
    """Detects ISP violations - simple and focused"""

    def analyze_violations(
        self, interfaces: dict[str, InterfaceInfo], implementations: dict[str, list[str]]
    ) -> list[ISPViolation]:
        """
        Analyze ISP violations

        Args:
            interfaces: The interfaces to analyze
            implementations: The implementations to analyze

        Returns:
            The violations found
        """
        violations = []

        for _interface_name, interface_info in interfaces.items():
            violations.extend(self._check_fat_interface(interface_info))
            violations.extend(self._check_low_cohesion(interface_info))
            violations.extend(self._check_unused_methods(interface_info, implementations))

        return violations

    def _check_fat_interface(self, interface_info: InterfaceInfo) -> list[ISPViolation]:
        """
        Check if interface is too 'fat'

        Args:
            interface_info: The interface to check

        Returns:
            The violations found
        """
        violations = []
        method_count = len(interface_info.methods)

        if method_count > 10:
            violations.append(
                ISPViolation(
                    interface_name=interface_info.name,
                    violation_type="fat_interface",
                    method_count=method_count,
                    unused_methods=[],
                    cohesion_groups=[],
                    description=f"Interface {interface_info.name} has {method_count} methods (too many)",
                    suggestion="Split interface into smaller, more focused interfaces",
                    line_number=interface_info.line_number,
                )
            )
        elif method_count > 7:
            violations.append(
                ISPViolation(
                    interface_name=interface_info.name,
                    violation_type="potentially_fat_interface",
                    method_count=method_count,
                    unused_methods=[],
                    cohesion_groups=[],
                    description=f"Interface {interface_info.name} has {method_count} methods (consider splitting)",
                    suggestion="Consider splitting into smaller interfaces for better cohesion",
                    line_number=interface_info.line_number,
                )
            )

        return violations

    def _check_low_cohesion(self, interface_info: InterfaceInfo) -> list[ISPViolation]:
        """
        Check method cohesion in interface

        Args:
            interface_info: The interface to check

        Returns:
            The violations found
        """
        violations = []
        groups = interface_info.method_groups

        # If methods are split into many different groups, this may indicate low cohesion
        if len(groups) > 3:
            group_names = list(groups.keys())
            cohesion_groups = [groups[name] for name in group_names if name != "other"]

            violations.append(
                ISPViolation(
                    interface_name=interface_info.name,
                    violation_type="low_cohesion",
                    method_count=len(interface_info.methods),
                    unused_methods=[],
                    cohesion_groups=cohesion_groups,
                    description=f"Interface {interface_info.name} has methods from {len(groups)} different functional areas",
                    suggestion=f"Consider splitting into separate interfaces: {', '.join(group_names[:3])}",
                    line_number=interface_info.line_number,
                )
            )

        return violations

    def _check_unused_methods(
        self, interface_info: InterfaceInfo, implementations: dict[str, list[str]]
    ) -> list[ISPViolation]:
        """
        Check for potentially unused methods

        Args:
            interface_info: The interface to check
            implementations: The implementations to check

        Returns:
            The violations found
        """
        violations = []

        # If interface has many methods but few implementations, maybe not all methods are needed
        implementations_count = len(
            [impl for impl, interfaces in implementations.items() if interface_info.name in interfaces]
        )

        if len(interface_info.methods) > 5 and implementations_count <= 1:
            violations.append(
                ISPViolation(
                    interface_name=interface_info.name,
                    violation_type="potentially_unused_methods",
                    method_count=len(interface_info.methods),
                    unused_methods=[],
                    cohesion_groups=[],
                    description=f"Interface {interface_info.name} has many methods but few implementations",
                    suggestion="Verify all methods are needed or consider splitting interface",
                    line_number=interface_info.line_number,
                )
            )

        return violations


# ============================================================================
# ISP SCORER
# ============================================================================


class ISPScorer:
    """Simple ISP scoring - straightforward calculation"""

    def calculate_isp_score(self, interfaces: dict[str, InterfaceInfo], violations: list[ISPViolation]) -> float:
        """
        Calculate ISP score (0.0 - 1.0)

        Args:
            interfaces: The interfaces to analyze
            violations: The violations to analyze

        Returns:
            The ISP score
        """
        if not interfaces:
            return 1.0  # No interfaces - no problems

        score = 1.0

        # Penalties for violations
        for violation in violations:
            if violation.violation_type == "fat_interface":
                score -= 0.30
            elif violation.violation_type == "potentially_fat_interface":
                score -= 0.15
            elif violation.violation_type == "low_cohesion":
                score -= 0.25
            elif violation.violation_type == "potentially_unused_methods":
                score -= 0.10

        # Bonus for well-designed interfaces
        small_interfaces = sum(1 for info in interfaces.values() if len(info.methods) <= 5)
        if small_interfaces > 0:
            bonus = min(0.1, small_interfaces * 0.02)
            score += bonus

        return max(0.0, min(1.0, score))

    def generate_suggestions(self, interfaces: dict[str, InterfaceInfo], violations: list[ISPViolation]) -> list[str]:
        """
        Generate improvement suggestions

        Args:
            interfaces: The interfaces to analyze
            violations: The violations to analyze

        Returns:
            The suggestions
        """
        suggestions = []

        if not interfaces:
            suggestions.append("Consider using interfaces/protocols to define contracts")
            return suggestions

        fat_interfaces = [v for v in violations if v.violation_type in ["fat_interface", "potentially_fat_interface"]]
        if fat_interfaces:
            suggestions.append("Split large interfaces into smaller, focused ones")
            for violation in fat_interfaces[:2]:
                interface_info = interfaces[violation.interface_name]
                groups = list(interface_info.method_groups.keys())
                if len(groups) > 1:
                    suggestions.append(f"  • {violation.interface_name}: separate {', '.join(groups[:2])} concerns")

        cohesion_issues = [v for v in violations if v.violation_type == "low_cohesion"]
        if cohesion_issues:
            suggestions.append("Group related methods into separate interfaces")

        if len(violations) == 0:
            suggestions.append("Great! Interfaces follow ISP well - they are focused and cohesive")

        return suggestions
