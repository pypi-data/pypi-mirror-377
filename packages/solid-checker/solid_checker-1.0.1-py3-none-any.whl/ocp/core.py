"""
🔍 OCP Analyzer: Core Analysis Module

Main components for analyzing the Open/Closed Principle.
Simple, focused implementation without unnecessary complexity.
"""

# Python imports
from ast import AST, Attribute, Call, ClassDef, Compare, Constant, FunctionDef, If, Match, Name, NodeVisitor
from collections import defaultdict

# Local imports
from .protocols import AbstractionDetectorProtocol, OCPViolation, RigidityDetectorProtocol


# ============================================================================
# ABSTRACTION DETECTION
# ============================================================================


class AbstractionDetector:
    """Detects abstractions in code - simple and focused"""

    def __init__(self) -> None:
        """Initialize the abstraction detector."""
        self.abstract_methods: set[str] = set()
        self.protocols: set[str] = set()

    def add_abstract_method(self, class_name: str, method_name: str) -> None:
        """
        Add abstract method

        Args:
            class_name: The name of the class
            method_name: The name of the method
        """
        self.abstract_methods.add(f"{class_name}.{method_name}")

    def add_protocol(self, class_name: str) -> None:
        """
        Add protocol

        Args:
            class_name: The name of the class
        """
        self.protocols.add(class_name)

    def detect_abstract_methods(self) -> set[str]:
        """
        Detect abstract methods

        Returns:
            The abstract methods
        """
        return self.abstract_methods

    def detect_protocols(self) -> set[str]:
        """
        Detect protocols

        Returns:
            The protocols
        """
        return self.protocols


# ============================================================================
# RIGIDITY DETECTION
# ============================================================================


class RigidityDetector:
    """Detects rigid constructs - simple pattern recognition"""

    def __init__(self) -> None:
        """Initialize the rigidity detector."""
        self.if_elif_chains: dict[str, list[tuple[int, str]]] = defaultdict(list)
        self.switch_statements: list[tuple[str, str, int]] = []
        self.type_checks: list[tuple[str, str, int]] = []

    def add_if_elif_chain(self, method_key: str, line_no: int, condition: str) -> None:
        """
        Add if-elif chain

        Args:
            method_key: The key of the method
            line_no: The line number
            condition: The condition
        """
        self.if_elif_chains[method_key].append((line_no, condition))

    def add_type_check(self, method_key: str, type_check: str, line_no: int) -> None:
        """
        Add type check

        Args:
            method_key: The key of the method
            type_check: The type check
            line_no: The line number
        """
        self.type_checks.append((method_key, type_check, line_no))

    def add_switch_statement(self, method_key: str, switch_desc: str, line_no: int) -> None:
        """
        Add switch statement

        Args:
            method_key: The key of the method
            switch_desc: The switch description
            line_no: The line number
        """
        self.switch_statements.append((method_key, switch_desc, line_no))

    def detect_if_elif_chains(self) -> dict[str, list[tuple[int, str]]]:
        """
        Detect if-elif chains

        Returns:
            The if-elif chains
        """
        return self.if_elif_chains

    def detect_type_checks(self) -> list[tuple[str, str, int]]:
        """
        Detect type checking

        Returns:
            The type checks
        """
        return self.type_checks

    def detect_switch_statements(self) -> list[tuple[str, str, int]]:
        """
        Detect switch statements

        Returns:
            The switch statements
        """
        return self.switch_statements


# ============================================================================
# MAIN OCP ANALYZER
# ============================================================================


class OCPAnalyzer(NodeVisitor):
    """Simple OCP analyzer - focused and straightforward"""

    def __init__(
        self, abstraction_detector: AbstractionDetectorProtocol, rigidity_detector: RigidityDetectorProtocol
    ) -> None:
        """
        Initialize the OCP analyzer.

        Args:
            abstraction_detector: The abstraction detector to use
            rigidity_detector: The rigidity detector to use
        """
        self.abstraction_detector = abstraction_detector
        self.rigidity_detector = rigidity_detector

        self.current_class: str | None = None
        self.current_method: str | None = None
        self.current_line: int = 0

    def visit_ClassDef(self, node: ClassDef) -> None:
        """
        Analyze class definitions

        Args:
            node: The class definition node to analyze
        """
        self.current_class = node.name

        # Check for abstractions and protocols
        for base in node.bases:
            if isinstance(base, Name):
                if base.id in ["ABC", "Protocol"]:
                    if base.id == "Protocol":
                        self.abstraction_detector.add_protocol(node.name)

        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: FunctionDef) -> None:
        """
        Analyze method definitions

        Args:
            node: The function definition node to analyze
        """
        self.current_method = node.name
        self.current_line = node.lineno

        # Check for abstract methods
        for decorator in node.decorator_list:
            if isinstance(decorator, Name) and decorator.id == "abstractmethod":
                if self.current_class:
                    self.abstraction_detector.add_abstract_method(self.current_class, node.name)

        # Analyze if-elif chains
        self._analyze_if_elif_chains(node)

        self.generic_visit(node)
        self.current_method = None

    def visit_If(self, node: If) -> None:
        """
        Analyze if-elif constructions

        Args:
            node: The if-elif node to analyze
        """
        if self.current_class and self.current_method:
            method_key = f"{self.current_class}.{self.current_method}"

            # Count branches
            current_node = node
            total_branches = 1  # Start with if

            while current_node.orelse and len(current_node.orelse) == 1:
                if isinstance(current_node.orelse[0], If):
                    total_branches += 1
                    current_node = current_node.orelse[0]
                else:
                    break

            # If many branches - potential OCP violation
            if total_branches >= 3:
                condition_desc = self._extract_condition_description(node.test)
                self.rigidity_detector.add_if_elif_chain(method_key, node.lineno, condition_desc)

        self.generic_visit(node)

    def visit_Call(self, node: Call) -> None:
        """
        Analyze function calls for type checking

        Args:
            node: The call node to analyze
        """
        if self.current_class and self.current_method:
            method_key = f"{self.current_class}.{self.current_method}"

            # Check isinstance() calls
            if isinstance(node.func, Name) and node.func.id == "isinstance":
                if len(node.args) >= 2:
                    obj_name = self._extract_expression_text(node.args[0])
                    type_name = self._extract_expression_text(node.args[1])
                    self.rigidity_detector.add_type_check(
                        method_key, f"isinstance({obj_name}, {type_name})", node.lineno
                    )

            # Check type() calls
            elif isinstance(node.func, Name) and node.func.id == "type":
                if node.args:
                    obj_name = self._extract_expression_text(node.args[0])
                    self.rigidity_detector.add_type_check(method_key, f"type({obj_name})", node.lineno)

        self.generic_visit(node)

    def visit_Match(self, node: Match) -> None:
        """
        Analyze match statements (Python 3.10+)

        Args:
            node: The match node to analyze
        """
        if self.current_class and self.current_method:
            method_key = f"{self.current_class}.{self.current_method}"
            subject = self._extract_expression_text(node.subject)
            case_count = len(node.cases)

            if case_count >= 3:  # Many cases may indicate OCP violation
                self.rigidity_detector.add_switch_statement(
                    method_key, f"match {subject} with {case_count} cases", node.lineno
                )

        self.generic_visit(node)

    def _analyze_if_elif_chains(self, node: FunctionDef) -> None:
        """
        Analyze if-elif chains in method

        Args:
            node: The function definition node to analyze
        """
        # Already handled in visit_If
        pass

    def _extract_condition_description(self, test_node: AST) -> str:
        """
        Extract condition description

        Args:
            test_node: The test node to extract the condition from

        Returns:
            The condition description
        """
        if isinstance(test_node, Compare):
            left = self._extract_expression_text(test_node.left)
            if test_node.ops and test_node.comparators:
                op = self._extract_operator_text(test_node.ops[0])
                right = self._extract_expression_text(test_node.comparators[0])
                return f"{left} {op} {right}"
        elif isinstance(test_node, Call):
            return self._extract_expression_text(test_node)
        elif isinstance(test_node, Name):
            return test_node.id

        return "complex_condition"

    def _extract_expression_text(self, node: AST) -> str:
        """
        Extract textual representation of expression

        Args:
            node: The expression node to extract the text from

        Returns:
            The textual representation of the expression
        """
        if isinstance(node, Name):
            return node.id
        elif isinstance(node, Attribute):
            value = self._extract_expression_text(node.value)
            return f"{value}.{node.attr}"
        elif isinstance(node, Constant):
            return repr(node.value)
        elif isinstance(node, Call):
            func = self._extract_expression_text(node.func)
            return f"{func}(...)"
        else:
            return "expr"

    def _extract_operator_text(self, op: AST) -> str:
        """
        Extract textual representation of operator

        Args:
            op: The operator node to extract the text from

        Returns:
            The textual representation of the operator
        """
        op_map = {
            "Eq": "==",
            "NotEq": "!=",
            "Lt": "<",
            "LtE": "<=",
            "Gt": ">",
            "GtE": ">=",
            "Is": "is",
            "IsNot": "is not",
            "In": "in",
            "NotIn": "not in",
        }
        return op_map.get(op.__class__.__name__, "op")


# ============================================================================
# VIOLATION ANALYZER
# ============================================================================


class ViolationAnalyzer:
    """Analyzes OCP violations - simple and focused"""

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
        violations = []

        # Analyze if-elif chains
        for method_key, conditions in if_elif_chains.items():
            if len(conditions) >= 1:  # If there are long chains
                class_name, method_name = method_key.split(".", 1)

                for line_no, condition in conditions:
                    # Check for typical OCP violation patterns
                    if any(keyword in condition.lower() for keyword in ["type", "kind", "category", "class"]):
                        violations.append(
                            OCPViolation(
                                type="if_elif_chain",
                                class_name=class_name,
                                method_name=method_name,
                                line_number=line_no,
                                description=f"Long if-elif chain based on type/category: {condition}",
                                suggestion="Consider using polymorphism or strategy pattern",
                            )
                        )

        # Analyze type checking
        for method_key, type_check, line_no in type_checks:
            class_name, method_name = method_key.split(".", 1)
            violations.append(
                OCPViolation(
                    type="type_checking",
                    class_name=class_name,
                    method_name=method_name,
                    line_number=line_no,
                    description=f"Explicit type checking: {type_check}",
                    suggestion="Use polymorphism instead of type checking",
                )
            )

        # Analyze switch statements
        for method_key, switch_desc, line_no in switch_statements:
            class_name, method_name = method_key.split(".", 1)
            violations.append(
                OCPViolation(
                    type="switch_statement",
                    class_name=class_name,
                    method_name=method_name,
                    line_number=line_no,
                    description=f"Large switch statement: {switch_desc}",
                    suggestion="Consider using polymorphism or command pattern",
                )
            )

        return violations


# ============================================================================
# OCP SCORER
# ============================================================================


class OCPScorer:
    """Simple OCP scoring - straightforward calculation"""

    def calculate_ocp_score(
        self, violations: list[OCPViolation], abstract_methods_count: int, protocols_count: int
    ) -> float:
        """
        Calculate OCP score (0.0 - 1.0)

        Args:
            violations: The violations to analyze
            abstract_methods_count: The number of abstract methods
            protocols_count: The number of protocols

        Returns:
            The OCP score
        """
        score = 1.0

        # Penalties for violations
        for violation in violations:
            if violation.type == "type_checking":
                score -= 0.15
            elif violation.type == "if_elif_chain":
                score -= 0.10
            elif violation.type == "switch_statement":
                score -= 0.20

        # Bonus for using abstractions
        abstraction_bonus = min(0.1, (abstract_methods_count + protocols_count) * 0.02)
        score += abstraction_bonus

        return max(0.0, min(1.0, score))

    def identify_extensibility_points(self, abstract_methods: set[str], protocols: set[str]) -> list[str]:
        """
        Identify extensibility points

        Args:
            abstract_methods: The abstract methods
            protocols: The protocols

        Returns:
            The extensibility points
        """
        points = []

        if abstract_methods:
            points.append(f"Abstract methods ({len(abstract_methods)}): {', '.join(list(abstract_methods)[:3])}")

        if protocols:
            points.append(f"Protocols ({len(protocols)}): {', '.join(protocols)}")

        return points

    def identify_rigid_constructs(self, violations: list[OCPViolation]) -> list[str]:
        """
        Identify rigid constructs

        Args:
            violations: The violations to analyze

        Returns:
            The rigid constructs
        """
        rigid = []

        type_checks = len([v for v in violations if v.type == "type_checking"])
        if type_checks > 0:
            rigid.append(f"Type checking ({type_checks} instances)")

        if_chains = len([v for v in violations if v.type == "if_elif_chain"])
        if if_chains > 0:
            rigid.append(f"If-elif chains ({if_chains} instances)")

        switches = len([v for v in violations if v.type == "switch_statement"])
        if switches > 0:
            rigid.append(f"Switch statements ({switches} instances)")

        return rigid
