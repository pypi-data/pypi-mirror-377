"""
Data models for SOLID analysis results and project information.

This module contains all dataclasses and enums used throughout the SOLID analysis framework.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Import required types from SOLID modules
from dip import DIPAnalysisResult
from isp import ISPAnalysisResult
from lsp import LSPAnalysisResult
from ocp import OCPAnalysisResult
from srp import DependencyInfo


@dataclass
class SOLIDScores:
    """SOLID principle scores for all five principles"""

    srp_score: float  # Single Responsibility Principle
    ocp_score: float  # Open/Closed Principle
    lsp_score: float  # Liskov Substitution Principle
    isp_score: float  # Interface Segregation Principle
    dip_score: float  # Dependency Inversion Principle
    overall_score: float  # Weighted overall score


@dataclass
class SOLIDAnalysisResult:
    """Complete SOLID analysis result with contextual information"""

    file_path: str
    scores: SOLIDScores
    srp_analysis: dict[str, DependencyInfo]
    ocp_analysis: OCPAnalysisResult
    lsp_analysis: LSPAnalysisResult
    isp_analysis: ISPAnalysisResult
    dip_analysis: DIPAnalysisResult
    recommendations: list[str]
    summary: str
    project_complexity: "ProjectComplexity"  # Smart analysis project complexity
    adaptive_weights: dict[str, float]  # Adaptive weights for transparency


class ProjectType(Enum):
    """Types of Python projects for contextual analysis"""

    SIMPLE_SCRIPT = "simple_script"  # < 100 lines, 1-2 classes
    UTILITY_MODULE = "utility_module"  # 100-500 lines, few classes
    SMALL_APPLICATION = "small_app"  # 500-1500 lines, moderate complexity
    LARGE_APPLICATION = "large_app"  # 1500+ lines, many classes
    LIBRARY_FRAMEWORK = "library"  # Public APIs, reusable components


@dataclass
class ProjectComplexity:
    """Project complexity analysis result"""

    lines_of_code: int
    class_count: int
    method_count: int
    inheritance_depth: int
    external_dependencies: int
    project_type: ProjectType
    complexity_score: float  # 0.0 (simple) to 1.0 (very complex)


@dataclass
class ProjectFile:
    """Information about a Python file in the project"""

    path: Path
    relative_path: Path
    size_lines: int
    is_package_init: bool = False
    is_test_file: bool = False
    is_main_file: bool = False


@dataclass
class ProjectStructure:
    """Analysis of project directory structure"""

    root_path: Path
    total_files: int
    total_lines: int
    packages: list[str]
    modules: list[str]
    test_files: list[str]
    main_files: list[str]
    max_depth: int
    has_proper_structure: bool

