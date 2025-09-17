"""
🔍 LSP Checker: Simple Facade

Simple facade for creating and coordinating all LSP analysis components.
Follows the simplicity principle of solid_scorer.py.
"""

# Python imports
from ast import parse
from collections import defaultdict
from pathlib import Path

# Local imports
from .core import HierarchyAnalyzer, LSPAnalyzer, LSPScorer, MethodAnalyzer, ViolationChecker
from .protocols import LSPAnalysisResult


class SimpleLSPChecker:
    """Simple LSP Checker without complex infrastructure"""

    def __init__(self) -> None:
        """Initialize the LSP checker."""
        # Create simple components without DI complexity
        self.method_analyzer = MethodAnalyzer()
        self.hierarchy_analyzer = HierarchyAnalyzer()
        self.violation_checker = ViolationChecker()
        self.scorer = LSPScorer()

    def analyze_file(self, file_path: Path, target_hierarchy: str | None = None) -> LSPAnalysisResult:
        """
        Analyze Python file for LSP compliance - simple and straightforward

        Args:
            file_path: The path to the file to analyze
            target_hierarchy: The target hierarchy to analyze

        Returns:
            The LSP analysis result
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return LSPAnalysisResult(str(file_path), {}, {}, [], 0.0)

        try:
            tree = parse(source)
        except SyntaxError as e:
            print(f"❌ Syntax error in file {file_path}: {e}")
            return LSPAnalysisResult(str(file_path), {}, {}, [], 0.0)

        # Create analyzer with simple dependency injection
        analyzer = LSPAnalyzer(self.method_analyzer)
        analyzer.visit(tree)

        # Analyze hierarchies
        hierarchies = self.hierarchy_analyzer.analyze_hierarchies(analyzer.classes)

        # Filter by target hierarchy if specified
        if target_hierarchy:
            filtered_hierarchies = {k: v for k, v in hierarchies.items() if k == target_hierarchy}
        else:
            filtered_hierarchies = hierarchies

        # Check violations
        violations = self.violation_checker.check_lsp_violations(analyzer.classes, filtered_hierarchies)

        # Calculate score
        lsp_score = self.scorer.calculate_lsp_score(analyzer.classes, violations)

        return LSPAnalysisResult(
            file_path=str(file_path),
            classes=analyzer.classes,
            hierarchies=filtered_hierarchies,
            violations=violations,
            lsp_score=lsp_score,
        )

    def print_analysis(self, result: LSPAnalysisResult, target_hierarchy: str | None = None) -> None:
        """
        Print analysis results with clear visualization

        Args:
            result: The LSP analysis result
            target_hierarchy: The target hierarchy to analyze
        """
        print(f"\n🔍 LSP Analysis: {Path(result.file_path).name}")
        print(f"{'=' * 50}")

        # LSP Score
        score_emoji = "🟢" if result.lsp_score >= 0.8 else "🟡" if result.lsp_score >= 0.6 else "🔴"
        print(f"{score_emoji} LSP Score: {result.lsp_score:.2f}/1.00")

        # Statistics
        total_classes = len(result.classes)
        classes_with_inheritance = sum(1 for cls in result.classes.values() if cls.base_classes)

        print("\n📊 Statistics:")
        print(f"   • Total classes: {total_classes}")
        print(f"   • With inheritance: {classes_with_inheritance}")
        print(f"   • Inheritance hierarchies: {len(result.hierarchies)}")

        # Inheritance hierarchies
        if result.hierarchies:
            print("\n🏗️ Inheritance hierarchies:")
            for base_class, derived_classes in result.hierarchies.items():
                if target_hierarchy and base_class != target_hierarchy:
                    continue

                print(f"   📍 {base_class}")
                for derived in derived_classes:
                    print(f"      └── {derived}")

                    # Show methods if there are problems
                    class_violations = [v for v in result.violations if v.derived_class == derived]
                    if class_violations:
                        for violation in class_violations[:2]:  # First 2
                            print(f"          ⚠️  {violation.method_name}: {violation.type}")

        # Violations
        if result.violations:
            print(f"\n⚠️  LSP Violations ({len(result.violations)}):")

            violations_by_type = defaultdict(list)
            for violation in result.violations:
                violations_by_type[violation.type].append(violation)

            for violation_type, violations in violations_by_type.items():
                type_names = {
                    "contract_violation": "Contract violations",
                    "new_exceptions": "New exceptions",
                    "precondition_strengthening": "Precondition strengthening",
                    "postcondition_weakening": "Postcondition weakening",
                    "signature_incompatibility": "Signature incompatibility",
                }

                print(f"\n   📍 {type_names.get(violation_type, violation_type)}:")
                for violation in violations[:3]:  # Show first 3
                    print(f"      • {violation.derived_class}.{violation.method_name}")
                    print(f"        {violation.description}")
                    print(f"        💡 {violation.suggestion}")

                if len(violations) > 3:
                    print(f"      ... and {len(violations) - 3} more violations")
        else:
            print("\n✅ No LSP violations found! 🎉")

        # Recommendations
        print("\n💡 Recommendations:")
        if result.lsp_score < 0.6:
            print("   • Inheritance hierarchies require serious review")
            print("   • Consider using composition instead of inheritance")
        if result.violations:
            print("   • Ensure derived classes don't violate base class contracts")
            print("   • Don't throw NotImplementedError in overridden methods")
        if not result.hierarchies and total_classes > 1:
            print("   • Consider using inheritance for shared functionality")
        if result.lsp_score >= 0.8:
            print("   • Inheritance hierarchies correctly follow LSP principle! 🎉")


# Convenience functions for backward compatibility
def analyze_file(file_path: Path, target_hierarchy: str | None = None) -> LSPAnalysisResult:
    """
    Analyze file using simple LSP checker

    Args:
        file_path: The path to the file to analyze
        target_hierarchy: The target hierarchy to analyze

    Returns:
        The LSP analysis result
    """
    checker = SimpleLSPChecker()
    return checker.analyze_file(file_path, target_hierarchy)


def print_analysis(result: LSPAnalysisResult, target_hierarchy: str | None = None) -> None:
    """
    Print analysis results

    Args:
        result: The LSP analysis result
        target_hierarchy: The target hierarchy to analyze
    """
    checker = SimpleLSPChecker()
    checker.print_analysis(result, target_hierarchy)
