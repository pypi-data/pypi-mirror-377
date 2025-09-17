"""
🔍 DIP Analyzer: Simple Facade

Simple facade for creating and coordinating all DIP analysis components.
Follows the simplicity principle of solid_scorer.py.
"""

# Python imports
from ast import parse
from collections import defaultdict
from pathlib import Path

# Local imports
from .core import AbstractionDetector, DependencyClassifier, DIPAnalyzer, DIPScorer, ViolationAnalyzer
from .protocols import DIPAnalysisResult


class SimpleDIPAnalyzer:
    """Simple DIP Analyzer without complex infrastructure"""

    def __init__(self) -> None:
        """Initialize the DIP analyzer."""
        # Create simple components without DI complexity
        self.abstraction_detector = AbstractionDetector()
        self.dependency_classifier = DependencyClassifier(self.abstraction_detector)
        self.violation_analyzer = ViolationAnalyzer()
        self.scorer = DIPScorer()

    def analyze_file(self, file_path: Path, target_class: str | None = None) -> DIPAnalysisResult:
        """
        Analyze Python file for DIP compliance - simple and straightforward

        Args:
            file_path: The path to the file to analyze
            target_class: The target class to analyze

        Returns:
            The DIP analysis result
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return DIPAnalysisResult(str(file_path), {}, set(), set(), [], 0.0, [])

        try:
            tree = parse(source)
        except SyntaxError as e:
            print(f"❌ Syntax error in file {file_path}: {e}")
            return DIPAnalysisResult(str(file_path), {}, set(), set(), [], 0.0, [])

        # Create analyzer with simple dependency injection
        analyzer = DIPAnalyzer(self.abstraction_detector, self.dependency_classifier)
        analyzer.visit(tree)

        # Filter by target class if specified
        if target_class:
            filtered_classes = {k: v for k, v in analyzer.classes.items() if k == target_class}
        else:
            filtered_classes = analyzer.classes

        # Analyze violations
        violations = self.violation_analyzer.analyze_violations(filtered_classes, analyzer.abstractions)

        # Calculate score and recommendations
        dip_score = self.scorer.calculate_dip_score(filtered_classes, violations, analyzer.abstractions)
        recommendations = self.scorer.generate_recommendations(filtered_classes, violations)

        return DIPAnalysisResult(
            file_path=str(file_path),
            classes=filtered_classes,
            abstractions=analyzer.abstractions,
            concrete_classes=analyzer.concrete_classes,
            violations=violations,
            dip_score=dip_score,
            recommendations=recommendations,
        )

    def print_analysis(self, result: DIPAnalysisResult, target_class: str | None = None) -> None:
        """
        Print analysis results with clear visualization

        Args:
            result: The DIP analysis result
            target_class: The target class to analyze
        """
        print(f"\n🔍 DIP Analysis: {Path(result.file_path).name}")
        print(f"{'=' * 50}")

        # DIP Score
        score_emoji = "🟢" if result.dip_score >= 0.8 else "🟡" if result.dip_score >= 0.6 else "🔴"
        print(f"{score_emoji} DIP Score: {result.dip_score:.2f}/1.00")

        # Statistics
        print("\n📊 Statistics:")
        print(f"   • Total classes: {len(result.classes)}")
        print(f"   • Abstractions: {len(result.abstractions)}")
        print(f"   • Concrete classes: {len(result.concrete_classes)}")

        # Found abstractions
        if result.abstractions:
            print("\n🏗️ Found abstractions:")
            for abstraction in sorted(result.abstractions):
                print(f"   • {abstraction}")
        else:
            print("\n⚠️  No abstractions found")
            print("   💡 Consider adding interfaces/protocols")

        # Class analysis
        print("\n🏠 Class Analysis:")
        for class_name, class_analysis in result.classes.items():
            if target_class and class_name != target_class:
                continue

            if class_name in result.abstractions:
                continue  # Skip abstractions

            print(f"\n   📍 {class_name}:")

            # Dependencies
            hard_count = len(class_analysis.hard_dependencies)
            soft_count = len(class_analysis.soft_dependencies)
            abstraction_count = len(class_analysis.abstractions_used)

            print(f"      • Hard dependencies: {hard_count}")
            print(f"      • Soft dependencies: {soft_count}")
            print(f"      • Abstractions used: {abstraction_count}")

            if class_analysis.dependency_injections:
                print(f"      • Dependency injection: {', '.join(class_analysis.dependency_injections)}")

            # Show main hard dependencies
            constructor_hard = [d for d in class_analysis.hard_dependencies if d.usage_context == "constructor"]
            if constructor_hard:
                print(f"      ⚠️  Creates in constructor: {', '.join([d.name for d in constructor_hard[:3]])}")

            # Show used abstractions
            if class_analysis.abstractions_used:
                abstractions = [d.name for d in class_analysis.abstractions_used[:3]]
                print(f"      ✅ Uses abstractions: {', '.join(abstractions)}")

        # Violations
        if result.violations:
            print(f"\n⚠️  DIP Violations ({len(result.violations)}):")

            violations_by_severity = defaultdict(list)
            for violation in result.violations:
                violations_by_severity[violation.severity].append(violation)

            for severity in ["high", "medium", "low"]:
                violations = violations_by_severity.get(severity, [])
                if not violations:
                    continue

                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟠"}
                print(f"\n   {severity_emoji[severity]} {severity.upper()} priority:")

                for violation in violations:
                    print(f"      • {violation.class_name}: {violation.description}")
                    print(f"        💡 {violation.suggestion}")
        else:
            print("\n✅ No DIP violations found! 🎉")

        # Recommendations
        if result.recommendations:
            print("\n💡 Recommendations:")
            for recommendation in result.recommendations:
                print(f"   {recommendation}")


# Convenience functions for backward compatibility
def analyze_file(file_path: Path, target_class: str | None = None) -> DIPAnalysisResult:
    """
    Analyze file using simple DIP analyzer

    Args:
        file_path: The path to the file to analyze
        target_class: The target class to analyze

    Returns:
        The DIP analysis result
    """
    analyzer = SimpleDIPAnalyzer()
    return analyzer.analyze_file(file_path, target_class)


def print_analysis(result: DIPAnalysisResult, target_class: str | None = None) -> None:
    """
    Print analysis results

    Args:
        result: The DIP analysis result
        target_class: The target class to analyze
    """
    analyzer = SimpleDIPAnalyzer()
    analyzer.print_analysis(result, target_class)
