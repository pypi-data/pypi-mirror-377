"""
🔍 LSP Checker: Core Analysis Module

Main components for analyzing the Liskov Substitution Principle.
Simple, focused implementation without unnecessary complexity.
"""

# Python imports
from ast import AST, Attribute, Call, ClassDef, Constant, FunctionDef, Name, NodeVisitor, Raise, walk
from collections import defaultdict

# Local imports
from .protocols import ClassInfo, LSPViolation, MethodAnalyzerProtocol, MethodSignature


# ============================================================================
# METHOD ANALYSIS
# ============================================================================


class MethodAnalyzer:
    """Analyzes method signatures - simple and focused"""

    def analyze_method(self, node: FunctionDef) -> MethodSignature:
        """
        Analyze method and return signature

        Args:
            node: The function definition node to analyze

        Returns:
            The method signature
        """
        # Extract arguments
        args = [arg.arg for arg in node.args.args]

        # Extract return type
        returns = None
        if node.returns:
            returns = self._extract_type_annotation(node.returns)

        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, Name):
                decorators.append(decorator.id)

        # Check if abstract
        is_abstract = "abstractmethod" in decorators

        # Analyze raised exceptions
        raises_exceptions = self._find_raised_exceptions(node)

        return MethodSignature(
            name=node.name,
            args=args,
            returns=returns,
            decorators=decorators,
            is_abstract=is_abstract,
            raises_exceptions=raises_exceptions,
        )

    def _extract_type_annotation(self, node: AST) -> str:
        """
        Extract type annotation

        Args:
            node: The AST node to extract the type annotation from

        Returns:
            The type annotation
        """
        if isinstance(node, Name):
            return node.id
        elif isinstance(node, Constant):
            return str(node.value)
        elif isinstance(node, Attribute):
            return self._extract_attribute_name(node)
        else:
            return "Any"

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

    def _find_raised_exceptions(self, node: FunctionDef) -> list[str]:
        """
        Find exceptions raised in method

        Args:
            node: The function definition node to find the exceptions in

        Returns:
            The exceptions raised
        """
        exceptions = []

        for child in walk(node):
            if isinstance(child, Raise):
                if child.exc:
                    if isinstance(child.exc, Call):
                        if isinstance(child.exc.func, Name):
                            exceptions.append(child.exc.func.id)
                    elif isinstance(child.exc, Name):
                        exceptions.append(child.exc.id)

        return exceptions


# ============================================================================
# HIERARCHY ANALYSIS
# ============================================================================


class HierarchyAnalyzer:
    """Analyzes inheritance hierarchies - simple and straightforward"""

    def analyze_hierarchies(self, classes: dict[str, ClassInfo]) -> dict[str, list[str]]:
        """
        Analyze inheritance hierarchies

        Args:
            classes: The classes to analyze

        Returns:
            The inheritance hierarchies
        """
        hierarchies = defaultdict(list)

        for class_name, class_info in classes.items():
            for base_class in class_info.base_classes:
                if base_class in classes:
                    hierarchies[base_class].append(class_name)

        return dict(hierarchies)


# ============================================================================
# MAIN LSP ANALYZER
# ============================================================================


class LSPAnalyzer(NodeVisitor):
    """Simple LSP analyzer - focused and straightforward"""

    def __init__(self, method_analyzer: MethodAnalyzerProtocol) -> None:
        """
        Initialize the LSP analyzer.

        Args:
            method_analyzer: The method analyzer to use
        """
        self.method_analyzer = method_analyzer
        self.classes: dict[str, ClassInfo] = {}
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ClassDef) -> None:
        """
        Analyze class definitions

        Args:
            node: The class definition node to analyze
        """
        self.current_class = node.name

        # Extract base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, Name):
                base_classes.append(base.id)
            elif isinstance(base, Attribute):
                base_classes.append(self._extract_attribute_name(base))

        # Check if abstract
        is_abstract = self._is_abstract_class(node)

        # Analyze methods
        methods = {}
        for item in node.body:
            if isinstance(item, FunctionDef):
                method_sig = self.method_analyzer.analyze_method(item)
                methods[item.name] = method_sig

        self.classes[node.name] = ClassInfo(
            name=node.name, base_classes=base_classes, methods=methods, line_number=node.lineno, is_abstract=is_abstract
        )

        self.generic_visit(node)
        self.current_class = None

    def _is_abstract_class(self, node: ClassDef) -> bool:
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
                for decorator in item.decorator_list:
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
# VIOLATION CHECKER
# ============================================================================


class ViolationChecker:
    """Checks LSP violations - simple and focused"""

    def check_lsp_violations(
        self, classes: dict[str, ClassInfo], hierarchies: dict[str, list[str]]
    ) -> list[LSPViolation]:
        """
        Check LSP violations

        Args:
            classes: The classes to analyze
            hierarchies: The hierarchies to analyze

        Returns:
            The LSP violations
        """
        violations = []

        for base_class, derived_classes in hierarchies.items():
            base_info = classes.get(base_class)
            if not base_info:
                continue

            for derived_class in derived_classes:
                derived_info = classes.get(derived_class)
                if not derived_info:
                    continue

                violations.extend(self._check_method_compatibility(base_info, derived_info))

        return violations

    def _check_method_compatibility(self, base_info: ClassInfo, derived_info: ClassInfo) -> list[LSPViolation]:
        """
        Check method compatibility between base and derived classes

        Args:
            base_info: The base class information
            derived_info: The derived class information

        Returns:
            The LSP violations
        """
        violations = []

        for method_name, base_method in base_info.methods.items():
            derived_method = derived_info.methods.get(method_name)

            if not derived_method:
                # Method not overridden - this is normal
                continue

            # Check 1: Contract violation through exceptions
            violation = self._check_contract_violation(base_method, derived_method, base_info.name, derived_info.name)
            if violation:
                violations.append(violation)

            # Check 2: Precondition strengthening
            violation = self._check_precondition_strengthening(
                base_method, derived_method, base_info.name, derived_info.name
            )
            if violation:
                violations.append(violation)

            # Check 3: Postcondition weakening
            violation = self._check_postcondition_weakening(
                base_method, derived_method, base_info.name, derived_info.name
            )
            if violation:
                violations.append(violation)

            # Check 4: Signature compatibility
            violation = self._check_signature_compatibility(
                base_method, derived_method, base_info.name, derived_info.name
            )
            if violation:
                violations.append(violation)

        return violations

    def _check_contract_violation(
        self, base_method: MethodSignature, derived_method: MethodSignature, base_class: str, derived_class: str
    ) -> LSPViolation | None:
        """
        Check contract violation through exceptions

        Args:
            base_method: The base method information
            derived_method: The derived method information
            base_class: The base class name
            derived_class: The derived class name

        Returns:
            The LSP violation if found, None otherwise
        """
        # If base method doesn't raise NotImplementedError, but derived does
        if (
            "NotImplementedError" in derived_method.raises_exceptions
            and "NotImplementedError" not in base_method.raises_exceptions
        ):
            return LSPViolation(
                type="contract_violation",
                base_class=base_class,
                derived_class=derived_class,
                method_name=base_method.name,
                description=f"Method {base_method.name} raises NotImplementedError in derived class",
                suggestion="Implement the method properly or reconsider inheritance hierarchy",
                line_number=0,  # We don't have line info here
            )

        # If derived method raises new exceptions
        base_exceptions = set(base_method.raises_exceptions)
        derived_exceptions = set(derived_method.raises_exceptions)
        new_exceptions = derived_exceptions - base_exceptions

        # Exclude standard exceptions that may be added
        standard_exceptions = {"ValueError", "TypeError", "AttributeError"}
        problematic_new = new_exceptions - standard_exceptions

        if problematic_new:
            return LSPViolation(
                type="new_exceptions",
                base_class=base_class,
                derived_class=derived_class,
                method_name=base_method.name,
                description=f"Method introduces new exceptions: {', '.join(problematic_new)}",
                suggestion="Ensure derived method doesn't throw exceptions not expected by base class contract",
                line_number=0,
            )

        return None

    def _check_precondition_strengthening(
        self, base_method: MethodSignature, derived_method: MethodSignature, base_class: str, derived_class: str
    ) -> LSPViolation | None:
        """
        Check precondition strengthening

        Args:
            base_method: The base method information
            derived_method: The derived method information
            base_class: The base class name
            derived_class: The derived class name

        Returns:
            The LSP violation if found, None otherwise
        """
        # If derived method has more required arguments
        base_args = len([arg for arg in base_method.args if arg != "self"])
        derived_args = len([arg for arg in derived_method.args if arg != "self"])

        if derived_args > base_args:
            return LSPViolation(
                type="precondition_strengthening",
                base_class=base_class,
                derived_class=derived_class,
                method_name=base_method.name,
                description=f"Method has more required parameters ({derived_args} vs {base_args})",
                suggestion="Don't add required parameters in derived class methods",
                line_number=0,
            )

        return None

    def _check_postcondition_weakening(
        self, base_method: MethodSignature, derived_method: MethodSignature, base_class: str, derived_class: str
    ) -> LSPViolation | None:
        """
        Check postcondition weakening

        Args:
            base_method: The base method information
            derived_method: The derived method information
            base_class: The base class name
            derived_class: The derived class name

        Returns:
            The LSP violation if found, None otherwise
        """
        # If base method returns specific type, but derived returns more general
        if base_method.returns and derived_method.returns and base_method.returns != derived_method.returns:
            # Simple heuristic - if base returns specific type, but derived Any/None
            if derived_method.returns in ["Any", "None"] and base_method.returns not in ["Any", "None"]:
                return LSPViolation(
                    type="postcondition_weakening",
                    base_class=base_class,
                    derived_class=derived_class,
                    method_name=base_method.name,
                    description=f"Return type weakened from {base_method.returns} to {derived_method.returns}",
                    suggestion="Ensure derived method returns at least as specific type as base method",
                    line_number=0,
                )

        return None

    def _check_signature_compatibility(
        self, base_method: MethodSignature, derived_method: MethodSignature, base_class: str, derived_class: str
    ) -> LSPViolation | None:
        """
        Check signature compatibility

        Args:
            base_method: The base method information
            derived_method: The derived method information
            base_class: The base class name
            derived_class: The derived class name

        Returns:
            The LSP violation if found, None otherwise
        """
        # Check significant changes in signature
        base_arg_names = [arg for arg in base_method.args if arg != "self"]
        derived_arg_names = [arg for arg in derived_method.args if arg != "self"]

        # If argument names changed (except adding new ones at the end)
        min_args = min(len(base_arg_names), len(derived_arg_names))
        for i in range(min_args):
            if base_arg_names[i] != derived_arg_names[i]:
                return LSPViolation(
                    type="signature_incompatibility",
                    base_class=base_class,
                    derived_class=derived_class,
                    method_name=base_method.name,
                    description=f"Method signature changed: parameter '{base_arg_names[i]}' renamed to '{derived_arg_names[i]}'",
                    suggestion="Keep method signatures compatible with base class",
                    line_number=0,
                )

        return None


# ============================================================================
# LSP SCORER
# ============================================================================


class LSPScorer:
    """Simple LSP scoring - straightforward calculation"""

    def calculate_lsp_score(self, classes: dict[str, ClassInfo], violations: list[LSPViolation]) -> float:
        """
        Calculate LSP score

        Args:
            classes: The classes to analyze
            violations: The violations to analyze

        Returns:
            The LSP score
        """
        if not classes:
            return 1.0

        # Count classes with inheritance
        classes_with_inheritance = sum(1 for cls in classes.values() if cls.base_classes)

        if classes_with_inheritance == 0:
            return 1.0  # No inheritance - no LSP problems

        score = 1.0

        # Penalties for violations
        for violation in violations:
            if violation.type == "contract_violation":
                score -= 0.25  # Serious violation
            elif violation.type == "new_exceptions":
                score -= 0.15
            elif violation.type == "precondition_strengthening" or violation.type == "postcondition_weakening":
                score -= 0.20
            elif violation.type == "signature_incompatibility":
                score -= 0.10

        return max(0.0, min(1.0, score))
