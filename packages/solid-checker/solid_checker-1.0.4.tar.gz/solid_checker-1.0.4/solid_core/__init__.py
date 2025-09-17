"""
SOLID Core - Modular SOLID Analysis Framework

This package contains the core components for SOLID principle analysis,
organized into logical modules for better maintainability and testing.
"""

# Main analysis function - primary public API
from .analyzer import analyze_solid_comprehensive

# Data models
from .models import ProjectComplexity, ProjectFile, ProjectStructure, ProjectType, SOLIDAnalysisResult, SOLIDScores

# Project-wide analysis
from .project_analysis import ProjectScanner, ProjectSOLIDAnalyzer

# Report functions
from .reports import (
    analyze_solid_project,
    print_json_report,
    print_project_json_report,
    print_project_report,
    print_solid_report,
)

# Main scorer class
from .scorer import SOLIDScorer

# Smart analysis components
from .smart_analysis import (
    AdaptiveWeightCalculator,
    ContextualRecommendationGenerator,
    ProjectComplexityAnalyzer,
)


__all__ = [
    'AdaptiveWeightCalculator',
    'ContextualRecommendationGenerator',
    'ProjectComplexity',
    'ProjectComplexityAnalyzer',
    'ProjectFile',
    'ProjectSOLIDAnalyzer',
    'ProjectScanner',
    'ProjectStructure',
    'ProjectType',
    'SOLIDAnalysisResult',
    'SOLIDScorer',
    'SOLIDScores',
    'analyze_solid_comprehensive',
    'analyze_solid_project',
    'print_json_report',
    'print_project_json_report',
    'print_project_report',
    'print_solid_report',
]

