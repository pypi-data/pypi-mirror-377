"""
🔍 DIP Analyzer: Refactored Modular Architecture

Modular architecture of DIP analyzer following SOLID principles.
Simple, focused, and easily testable.

Core components:
- protocols: All protocols, data structures and interfaces
- core: Main analyzers, detectors and scorers
- facade: Simple facade for component coordination

Usage example:
    from dip import analyze_file, print_analysis

    result = analyze_file(Path("my_code.py"))
    print_analysis(result)
"""

# Local imports
from .core import AbstractionDetector, DependencyClassifier, DIPAnalyzer, DIPScorer, ViolationAnalyzer
from .facade import SimpleDIPAnalyzer, analyze_file, print_analysis
from .protocols import (
    AbstractionDetectorProtocol,
    ClassAnalysis,
    DependencyClassifierProtocol,
    DependencyInfo,
    DIPAnalysisResult,
    DIPScorerProtocol,
    DIPViolation,
    ViolationAnalyzerProtocol,
)


# Main API exports for simplicity
__all__ = [
    # Individual components (for unit testing)
    "AbstractionDetector",
    # Protocols (for customization)
    "AbstractionDetectorProtocol",
    "ClassAnalysis",
    "DIPAnalysisResult",
    "DIPAnalyzer",
    "DIPScorer",
    "DIPScorerProtocol",
    "DIPViolation",
    "DependencyClassifier",
    "DependencyClassifierProtocol",
    # Data structures
    "DependencyInfo",
    # Core components
    "SimpleDIPAnalyzer",
    "ViolationAnalyzer",
    "ViolationAnalyzerProtocol",
    # Main API
    "analyze_file",
    "print_analysis",
]
