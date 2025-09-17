"""
🔍 SRP Analyzer: Simple Facade

Simple facade for creating and coordinating all SRP analysis components.
Follows the simplicity principle of solid_scorer.py.
"""

# Python imports
from ast import parse
from pathlib import Path

# Local imports
from .core import (
    ClassInfoCollector,
    EmojiScoreCalculator,
    ImportCollector,
    ResponsibilityDetector,
    SimpleAttributeExtractor,
    SimpleCallExtractor,
    SimpleDependencyAnalyzer,
    SimpleInstanceDetector,
    SRPScorer,
)
from .protocols import DependencyInfo


class SimpleSRPAnalyzer:
    """Simple SRP Analyzer without IoC complexity"""

    def __init__(self) -> None:
        """Initialize the SRP analyzer."""
        # Create simple components without DI complexity
        self.import_collector = ImportCollector()
        self.class_collector = ClassInfoCollector()
        self.call_extractor = SimpleCallExtractor()
        self.instance_detector = SimpleInstanceDetector()
        self.attr_extractor = SimpleAttributeExtractor()
        self.responsibility_detector = ResponsibilityDetector()
        self.srp_scorer = SRPScorer()
        self.score_calculator = EmojiScoreCalculator()

    def analyze_file(self, file_path: Path, target_class: str | None = None) -> dict[str, DependencyInfo]:
        """
        Analyze Python file for SRP compliance - simple and straightforward

        Args:
            file_path: The path to the file to analyze
            target_class: The target class to analyze

        Returns:
            The SRP analysis results
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return {}

        try:
            tree = parse(source)
        except SyntaxError as e:
            print(f"❌ Syntax error in file {file_path}: {e}")
            return {}

        # Create analyzer with simple dependency injection
        analyzer = SimpleDependencyAnalyzer(
            self.import_collector,
            self.class_collector,
            self.call_extractor,
            self.instance_detector,
            self.attr_extractor,
        )

        analyzer.visit(tree)

        results = {}

        for class_name, class_info in analyzer.classes.items():
            if target_class and class_name != target_class:
                continue

            responsibilities = self.responsibility_detector.detect_responsibilities(class_info)
            srp_score = self.srp_scorer.calculate_srp_score(class_info, responsibilities)
            violations = self.srp_scorer.identify_violations(class_info, responsibilities)

            results[class_name] = DependencyInfo(
                class_name=class_name,
                imports=analyzer.imports,
                external_calls=list(set(class_info["external_calls"])),
                instance_creations=class_info["instance_creations"],
                method_count=len(class_info["methods"]),
                responsibilities=responsibilities,
                srp_score=srp_score,
                violations=violations,
            )

        return results

    def print_analysis(self, results: dict[str, DependencyInfo]) -> None:
        """
        Print analysis results with emoji visualization

        Args:
            results: The SRP analysis results
        """
        if not results:
            print("🤷 No classes found or analysis not possible")
            return

        for class_name, info in results.items():
            print(f"\n🔍 Analysis of class: {class_name}")
            print(f"{'=' * (20 + len(class_name))}")

            # SRP Score with emoji
            score_emoji = self.score_calculator.get_score_emoji(info.srp_score)
            print(f"{score_emoji} SRP Score: {info.srp_score:.2f}/1.00")

            # Basic statistics
            print("📊 Statistics:")
            print(f"   • Methods: {info.method_count}")
            print(f"   • External dependencies: {len(info.external_calls)}")
            print(f"   • Creates instances: {len(info.instance_creations)}")

            # Responsibilities
            if info.responsibilities:
                print(f"🎯 Found responsibilities ({len(info.responsibilities)}):")
                for resp in info.responsibilities:
                    print(f"   • {resp}")
            else:
                print("🎯 Responsibilities: not determined")

            # Violations
            if info.violations:
                print("⚠️  SRP Violations:")
                for violation in info.violations:
                    print(f"   • {violation}")
            else:
                print("✅ No SRP violations found")

            # External dependencies (top 10)
            if info.external_calls:
                print("🔗 External dependencies:")
                for call in info.external_calls[:10]:
                    print(f"   • {call}")
                if len(info.external_calls) > 10:
                    print(f"   ... and {len(info.external_calls) - 10} more")

            # Instance creations
            if info.instance_creations:
                print("🏭 Creates instances:")
                for creation in info.instance_creations:
                    print(f"   • {creation}")

            # Recommendations
            print("💡 Recommendations:")
            if info.srp_score < 0.6:
                print("   • Consider splitting class into multiple classes with single responsibility")
            if len(info.responsibilities) > 1:
                print("   • Extract each responsibility into separate class")
            if info.method_count > 10:
                print("   • Too many methods - class might be doing too much")
            if len(info.instance_creations) > 2:
                print("   • Use dependency injection instead of creating instances inside class")
            if info.srp_score >= 0.8:
                print("   • Class follows SRP well! 🎉")


# Convenience function for backward compatibility
def analyze_file(file_path: Path, target_class: str | None = None) -> dict[str, DependencyInfo]:
    """
    Analyze file using simple SRP analyzer

    Args:
        file_path: The path to the file to analyze
        target_class: The target class to analyze

    Returns:
        The SRP analysis results
    """
    analyzer = SimpleSRPAnalyzer()
    return analyzer.analyze_file(file_path, target_class)


def print_analysis(results: dict[str, DependencyInfo]) -> None:
    """
    Print analysis results

    Args:
        results: The SRP analysis results
    """
    analyzer = SimpleSRPAnalyzer()
    analyzer.print_analysis(results)
