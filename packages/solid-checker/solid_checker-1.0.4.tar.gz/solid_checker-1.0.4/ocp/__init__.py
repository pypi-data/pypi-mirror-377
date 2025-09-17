"""
🔍 OCP Analyzer: Refactored Modular Architecture

Modular architecture of OCP analyzer following SOLID principles.
Simple, focused, and easily testable.

Core components:
- protocols: All protocols, data structures and interfaces
- core: Main analyzers, detectors and scorers
- facade: Simple facade for component coordination

Usage example:
    from ocp import analyze_file, print_analysis

    result = analyze_file(Path("my_code.py"))
    print_analysis(result)
"""

# Local imports
from .core import AbstractionDetector, OCPAnalyzer, OCPScorer, RigidityDetector, ViolationAnalyzer
from .facade import SimpleOCPAnalyzer, analyze_file, print_analysis
from .protocols import (
    AbstractionDetectorProtocol,
    OCPAnalysisResult,
    OCPScorerProtocol,
    OCPViolation,
    RigidityDetectorProtocol,
    ViolationAnalyzerProtocol,
)


# Main API exports for simplicity
__all__ = [
    # Individual components (for unit testing)
    "AbstractionDetector",
    # Protocols (for customization)
    "AbstractionDetectorProtocol",
    "OCPAnalysisResult",
    "OCPAnalyzer",
    "OCPScorer",
    "OCPScorerProtocol",
    # Data structures
    "OCPViolation",
    "RigidityDetector",
    "RigidityDetectorProtocol",
    # Core components
    "SimpleOCPAnalyzer",
    "ViolationAnalyzer",
    "ViolationAnalyzerProtocol",
    # Main API
    "analyze_file",
    "print_analysis",
]
