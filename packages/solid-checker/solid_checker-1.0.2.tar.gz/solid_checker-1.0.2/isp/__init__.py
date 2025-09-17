"""
🔍 ISP Analyzer: Refactored Modular Architecture

Modular architecture of ISP analyzer following SOLID principles.
Simple, focused, and easily testable.

Core components:
- protocols: All protocols, data structures and interfaces
- core: Main analyzers, detectors and scorers
- facade: Simple facade for component coordination

Usage example:
    from isp import analyze_file, print_analysis

    result = analyze_file(Path("my_code.py"))
    print_analysis(result)
"""

# Local imports
from .core import InterfaceDetector, ISPAnalyzer, ISPScorer, MethodGrouper, ViolationDetector
from .facade import SimpleISPAnalyzer, analyze_file, print_analysis
from .protocols import (
    InterfaceDetectorProtocol,
    InterfaceInfo,
    ISPAnalysisResult,
    ISPScorerProtocol,
    ISPViolation,
    MethodGrouperProtocol,
    ViolationDetectorProtocol,
)


# Main API exports for simplicity
__all__ = [
    "ISPAnalysisResult",
    "ISPAnalyzer",
    "ISPScorer",
    "ISPScorerProtocol",
    "ISPViolation",
    # Individual components (for unit testing)
    "InterfaceDetector",
    # Protocols (for customization)
    "InterfaceDetectorProtocol",
    # Data structures
    "InterfaceInfo",
    "MethodGrouper",
    "MethodGrouperProtocol",
    # Core components
    "SimpleISPAnalyzer",
    "ViolationDetector",
    "ViolationDetectorProtocol",
    # Main API
    "analyze_file",
    "print_analysis",
]
