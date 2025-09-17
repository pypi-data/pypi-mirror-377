"""
🔍 ISP Analyzer: Simple Facade

Simple facade for creating and coordinating all ISP analysis components.
Follows the simplicity principle of solid_scorer.py.
"""

# Python imports
from ast import parse
from collections import defaultdict
from pathlib import Path

# Local imports
from .core import InterfaceDetector, ISPAnalyzer, ISPScorer, MethodGrouper, ViolationDetector
from .protocols import ISPAnalysisResult


class SimpleISPAnalyzer:
    """Simple ISP Analyzer without complex infrastructure"""

    def __init__(self) -> None:
        """Initialize the ISP analyzer."""
        # Create simple components without DI complexity
        self.interface_detector = InterfaceDetector()
        self.method_grouper = MethodGrouper()
        self.violation_detector = ViolationDetector()
        self.scorer = ISPScorer()

    def analyze_file(self, file_path: Path, target_interface: str | None = None) -> ISPAnalysisResult:
        """
        Analyze Python file for ISP compliance - simple and straightforward

        Args:
            file_path: The path to the file to analyze
            target_interface: The target interface to analyze

        Returns:
            The ISP analysis result
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return ISPAnalysisResult(str(file_path), {}, {}, [], 0.0, [])

        try:
            tree = parse(source)
        except SyntaxError as e:
            print(f"❌ Syntax error in file {file_path}: {e}")
            return ISPAnalysisResult(str(file_path), {}, {}, [], 0.0, [])

        # Create analyzer with simple dependency injection
        analyzer = ISPAnalyzer(self.interface_detector, self.method_grouper)
        analyzer.visit(tree)

        # Filter by target interface if specified
        if target_interface:
            filtered_interfaces = {k: v for k, v in analyzer.interfaces.items() if k == target_interface}
        else:
            filtered_interfaces = analyzer.interfaces

        # Analyze violations
        violations = self.violation_detector.analyze_violations(filtered_interfaces, analyzer.implementations)

        # Calculate score and suggestions
        isp_score = self.scorer.calculate_isp_score(filtered_interfaces, violations)
        suggestions = self.scorer.generate_suggestions(filtered_interfaces, violations)

        return ISPAnalysisResult(
            file_path=str(file_path),
            interfaces=filtered_interfaces,
            implementations=dict(analyzer.implementations),
            violations=violations,
            isp_score=isp_score,
            suggestions=suggestions,
        )

    def print_analysis(self, result: ISPAnalysisResult, target_interface: str | None = None) -> None:
        """
        Print analysis results with clear visualization

        Args:
            result: The ISP analysis result
            target_interface: The target interface to analyze
        """
        print(f"\n🔍 ISP Analysis: {Path(result.file_path).name}")
        print(f"{'=' * 50}")

        # ISP Score
        score_emoji = "🟢" if result.isp_score >= 0.8 else "🟡" if result.isp_score >= 0.6 else "🔴"
        print(f"{score_emoji} ISP Score: {result.isp_score:.2f}/1.00")

        # Statistics
        total_interfaces = len(result.interfaces)
        total_methods = sum(len(info.methods) for info in result.interfaces.values())

        print("\n📊 Statistics:")
        print(f"   • Interfaces/protocols: {total_interfaces}")
        print(f"   • Total methods in interfaces: {total_methods}")
        print(f"   • Implementation classes: {len(result.implementations)}")

        # Interfaces
        if result.interfaces:
            print("\n🔌 Found interfaces:")
            for name, info in result.interfaces.items():
                if target_interface and name != target_interface:
                    continue

                interface_type = (
                    "Protocol" if info.is_protocol else "Abstract Class" if info.is_abstract_class else "Interface"
                )
                emoji = "📝" if info.is_protocol else "🏗️" if info.is_abstract_class else "🔌"

                print(f"   {emoji} {name} ({interface_type})")
                print(f"      • Methods: {len(info.methods)}")

                if info.method_groups:
                    print("      • Functional groups:")
                    for group_name, methods in info.method_groups.items():
                        if group_name != "other":
                            print(
                                f"        - {group_name}: {', '.join(methods[:3])}{'...' if len(methods) > 3 else ''}"
                            )

                # Show violations for this interface
                interface_violations = [v for v in result.violations if v.interface_name == name]
                if interface_violations:
                    for violation in interface_violations[:2]:
                        print(f"      ⚠️  {violation.description}")
        else:
            print("\n⚠️  No interfaces/protocols found")
            print("   💡 Consider adding interfaces for better design")

        # Implementations
        if result.implementations:
            print("\n🏠 Interface implementations:")
            for class_name, interfaces in result.implementations.items():
                print(f"   • {class_name} implements: {', '.join(interfaces)}")

        # Violations
        if result.violations:
            print(f"\n⚠️  ISP Violations ({len(result.violations)}):")

            violations_by_type = defaultdict(list)
            for violation in result.violations:
                violations_by_type[violation.violation_type].append(violation)

            type_names = {
                "fat_interface": "Fat interfaces",
                "potentially_fat_interface": "Potentially fat interfaces",
                "low_cohesion": "Low cohesion",
                "potentially_unused_methods": "Possibly unused methods",
            }

            for violation_type, violations in violations_by_type.items():
                print(f"\n   📍 {type_names.get(violation_type, violation_type)}:")
                for violation in violations:
                    print(f"      • {violation.interface_name}: {violation.description}")
                    print(f"        💡 {violation.suggestion}")

                    if violation.cohesion_groups:
                        print(f"        📋 Method groups: {len(violation.cohesion_groups)}")
        else:
            print("\n✅ No ISP violations found! 🎉")

        # Suggestions
        if result.suggestions:
            print("\n💡 Recommendations:")
            for suggestion in result.suggestions:
                print(f"   {suggestion}")


# Convenience functions for backward compatibility
def analyze_file(file_path: Path, target_interface: str | None = None) -> ISPAnalysisResult:
    """
    Analyze file using simple ISP analyzer

    Args:
        file_path: The path to the file to analyze
        target_interface: The target interface to analyze

    Returns:
        The ISP analysis result
    """
    analyzer = SimpleISPAnalyzer()
    return analyzer.analyze_file(file_path, target_interface)


def print_analysis(result: ISPAnalysisResult, target_interface: str | None = None) -> None:
    """
    Print analysis results

    Args:
        result: The ISP analysis result
        target_interface: The target interface to analyze
    """
    analyzer = SimpleISPAnalyzer()
    analyzer.print_analysis(result, target_interface)
