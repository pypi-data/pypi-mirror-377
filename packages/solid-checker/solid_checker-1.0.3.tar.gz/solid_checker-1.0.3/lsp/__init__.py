"""
🔍 LSP Checker: Refactored Modular Architecture

Modular architecture of LSP checker following SOLID principles.
Simple, focused, and easily testable.

Core components:
- protocols: All protocols, data structures and interfaces
- core: Main analyzers, checkers and scorers
- facade: Simple facade for component coordination

Usage example:
    from lsp import analyze_file, print_analysis

    result = analyze_file(Path("my_code.py"))
    print_analysis(result)
"""

from .core import HierarchyAnalyzer, LSPAnalyzer, LSPScorer, MethodAnalyzer, ViolationChecker
from .facade import SimpleLSPChecker, analyze_file, print_analysis
from .protocols import (
    ClassInfo,
    HierarchyAnalyzerProtocol,
    LSPAnalysisResult,
    LSPScorerProtocol,
    LSPViolation,
    MethodAnalyzerProtocol,
    MethodSignature,
    ViolationCheckerProtocol,
)


# Main API exports for simplicity
__all__ = [
    "ClassInfo",
    "HierarchyAnalyzer",
    "HierarchyAnalyzerProtocol",
    "LSPAnalysisResult",
    "LSPAnalyzer",
    "LSPScorer",
    "LSPScorerProtocol",
    "LSPViolation",
    # Individual components (for unit testing)
    "MethodAnalyzer",
    # Protocols (for customization)
    "MethodAnalyzerProtocol",
    # Data structures
    "MethodSignature",
    # Core components
    "SimpleLSPChecker",
    "ViolationChecker",
    "ViolationCheckerProtocol",
    # Main API
    "analyze_file",
    "print_analysis",
]
