"""
🔍 SRP Analyzer: Refactored Modular Architecture

Modular architecture of SRP analyzer following SOLID principles.
Simple, focused, and easily testable.

Core components:
- protocols: All protocols and interfaces
- core: Main collectors, analyzers and scorers
- facade: Simple facade for component coordination

Usage example:
    from srp import analyze_file, print_analysis

    results = analyze_file(Path("my_code.py"))
    print_analysis(results)
"""

# Python imports
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
from .facade import SimpleSRPAnalyzer, analyze_file, print_analysis
from .protocols import AttributeExtractor, CallExtractor, DependencyInfo, InstanceDetector


# Main exports for ease of use
__all__ = [
    "AttributeExtractor",
    # Protocols (for those who want to customize)
    "CallExtractor",
    "ClassInfoCollector",
    # Data structures
    "DependencyInfo",
    "EmojiScoreCalculator",
    # Individual components (for unit testing)
    "ImportCollector",
    "InstanceDetector",
    "ResponsibilityDetector",
    "SRPScorer",
    "SimpleAttributeExtractor",
    "SimpleCallExtractor",
    "SimpleDependencyAnalyzer",
    "SimpleInstanceDetector",
    # Core components
    "SimpleSRPAnalyzer",
    # Main API
    "analyze_file",
    "print_analysis",
]
