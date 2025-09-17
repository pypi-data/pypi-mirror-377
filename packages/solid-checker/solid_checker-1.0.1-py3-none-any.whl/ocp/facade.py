"""
🔍 OCP Analyzer: Simple Facade

Simple facade for creating and coordinating all OCP analysis components.
Follows the simplicity principle of solid_scorer.py.
"""

# Python imports
from ast import parse
from collections import defaultdict
from pathlib import Path

# Local imports
from .core import AbstractionDetector, OCPAnalyzer, OCPScorer, RigidityDetector, ViolationAnalyzer
from .protocols import OCPAnalysisResult


class SimpleOCPAnalyzer:
    """Simple OCP Analyzer without complex infrastructure"""

    def __init__(self) -> None:
        """Initialize the OCP analyzer."""
        # Create simple components without DI complexity
        self.abstraction_detector = AbstractionDetector()
        self.rigidity_detector = RigidityDetector()
        self.violation_analyzer = ViolationAnalyzer()
        self.scorer = OCPScorer()

    def analyze_file(self, file_path: Path) -> OCPAnalysisResult:
        """
        Analyze Python file for OCP compliance - simple and straightforward

        Args:
            file_path: The path to the file to analyze

        Returns:
            The OCP analysis result
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return OCPAnalysisResult(str(file_path), [], 0.0, [], [])

        try:
            tree = parse(source)
        except SyntaxError as e:
            print(f"❌ Syntax error in file {file_path}: {e}")
            return OCPAnalysisResult(str(file_path), [], 0.0, [], [])

        # Create analyzer with simple dependency injection
        analyzer = OCPAnalyzer(self.abstraction_detector, self.rigidity_detector)
        analyzer.visit(tree)

        # Get detected patterns
        if_elif_chains = self.rigidity_detector.detect_if_elif_chains()
        type_checks = self.rigidity_detector.detect_type_checks()
        switch_statements = self.rigidity_detector.detect_switch_statements()

        # Analyze violations
        violations = self.violation_analyzer.analyze_violations(if_elif_chains, type_checks, switch_statements)

        # Calculate score and identify patterns
        abstract_methods = self.abstraction_detector.detect_abstract_methods()
        protocols = self.abstraction_detector.detect_protocols()

        ocp_score = self.scorer.calculate_ocp_score(violations, len(abstract_methods), len(protocols))

        extensibility_points = self.scorer.identify_extensibility_points(abstract_methods, protocols)

        rigid_constructs = self.scorer.identify_rigid_constructs(violations)

        return OCPAnalysisResult(
            file_path=str(file_path),
            violations=violations,
            ocp_score=ocp_score,
            extensibility_points=extensibility_points,
            rigid_constructs=rigid_constructs,
        )

    def print_analysis(self, result: OCPAnalysisResult) -> None:
        """
        Print analysis results with clear visualization

        Args:
            result: The OCP analysis result
        """
        print(f"\n🔍 OCP Analysis: {Path(result.file_path).name}")
        print(f"{'=' * 50}")

        # OCP Score
        score_emoji = "🟢" if result.ocp_score >= 0.8 else "🟡" if result.ocp_score >= 0.6 else "🔴"
        print(f"{score_emoji} OCP Score: {result.ocp_score:.2f}/1.00")

        # Extensibility points
        if result.extensibility_points:
            print("\n✅ Found extensibility points:")
            for point in result.extensibility_points:
                print(f"   • {point}")
        else:
            print("\n⚠️  No extensibility points found")
            print("   💡 Consider adding abstract classes or protocols")

        # Rigid constructs
        if result.rigid_constructs:
            print("\n🔒 Rigid constructs:")
            for construct in result.rigid_constructs:
                print(f"   • {construct}")

        # Violations
        if result.violations:
            print(f"\n⚠️  OCP Violations ({len(result.violations)}):")

            violations_by_type = defaultdict(list)
            for violation in result.violations:
                violations_by_type[violation.type].append(violation)

            for violation_type, violations in violations_by_type.items():
                type_name = {
                    "if_elif_chain": "If-Elif chains",
                    "type_checking": "Type checking",
                    "switch_statement": "Switch constructs",
                }.get(violation_type, violation_type)

                print(f"\n   📍 {type_name}:")
                for violation in violations[:5]:  # Show first 5
                    print(f"      • {violation.class_name}.{violation.method_name}:{violation.line_number}")
                    print(f"        {violation.description}")
                    print(f"        💡 {violation.suggestion}")

                if len(violations) > 5:
                    print(f"      ... and {len(violations) - 5} more violations")
        else:
            print("\n✅ No OCP violations found! 🎉")

        # Recommendations
        print("\n💡 Recommendations:")
        if result.ocp_score < 0.6:
            print("   • Code requires significant refactoring for OCP compliance")
        if result.violations:
            print("   • Replace if-elif chains and type checking with polymorphism")
            print("   • Use Strategy, Command or State patterns")
        if not result.extensibility_points:
            print("   • Add abstract classes or protocols for extension points")
        if result.ocp_score >= 0.8:
            print("   • Code follows OCP principle well! 🎉")
            print("   • New functionality can be added through extension, not modification")


# Convenience functions for backward compatibility
def analyze_file(file_path: Path) -> OCPAnalysisResult:
    """
    Analyze file using simple OCP analyzer

    Args:
        file_path: The path to the file to analyze

    Returns:
        The OCP analysis result
    """
    analyzer = SimpleOCPAnalyzer()
    return analyzer.analyze_file(file_path)


def print_analysis(result: OCPAnalysisResult) -> None:
    """
    Print analysis results

    Args:
        result: The OCP analysis result
    """
    analyzer = SimpleOCPAnalyzer()
    analyzer.print_analysis(result)
