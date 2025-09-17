#!/usr/bin/env python3
"""
🔍 SOLID Tools: Complete SOLID Analyzer with Smart Rating System

Comprehensive analyzer of all five SOLID principles with context-aware intelligence.
Combines SRP, OCP, LSP, ISP, and DIP analysis with adaptive scoring based on project complexity.

Features:
- Smart project type detection (Script, Utility, Application, Library)
- Adaptive SOLID principle weighting based on project context
- Context-aware recommendations and thresholds
- Complexity analysis and intelligent scoring

Usage:
    python solid_scorer.py path/to/your/file.py
    python solid_scorer.py --report path/to/your/file.py
    python solid_scorer.py --json path/to/your/file.py > report.json
    python solid_scorer.py --legacy path/to/your/file.py  # classic analysis
    python solid_scorer.py --no-smart-info path/to/your/file.py  # hide smart analysis information
"""

# Python imports
import argparse
import json
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any

# Local imports
from dip import DIPAnalysisResult
from dip import analyze_file as analyze_dip
from isp import ISPAnalysisResult
from isp import analyze_file as analyze_isp
from lsp import LSPAnalysisResult
from lsp import analyze_file as analyze_lsp
from ocp import OCPAnalysisResult
from ocp import analyze_file as analyze_ocp
from srp import DependencyInfo
from srp import analyze_file as analyze_srp


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


# ============================================================================
# SMART RATING SYSTEM: Contextual & Adaptive SOLID Analysis
# ============================================================================


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


class ProjectComplexityAnalyzer:
    """Analyzes project characteristics to determine appropriate SOLID standards"""

    def analyze_project(
        self,
        srp_analysis: dict[str, DependencyInfo],
        ocp_analysis: OCPAnalysisResult,
        lsp_analysis: LSPAnalysisResult,
        isp_analysis: ISPAnalysisResult,
        dip_analysis: DIPAnalysisResult,
        file_path: Path,
    ) -> ProjectComplexity:
        """
        Analyze project complexity and characteristics for smart SOLID assessment

        Args:
            srp_analysis: SRP analysis result
            ocp_analysis: OCP analysis result
            lsp_analysis: LSP analysis result
            isp_analysis: ISP analysis result
            dip_analysis: DIP analysis result
            file_path: Path to the file being analyzed

        Returns:
            ProjectComplexity object with analyzed metrics
        """

        # Calculate basic metrics
        lines_of_code = self._count_lines_of_code(file_path)
        class_count = len(srp_analysis)
        method_count = sum(len(info.responsibilities) for info in srp_analysis.values())
        inheritance_depth = self._calculate_inheritance_depth(lsp_analysis)
        external_deps = len(set().union(*[info.external_calls for info in srp_analysis.values()]))

        # Determine project type based on characteristics
        project_type = self._determine_project_type(lines_of_code, class_count, method_count)

        # Calculate normalized complexity score (0.0 - 1.0)
        complexity_score = self._calculate_complexity_score(
            lines_of_code, class_count, method_count, inheritance_depth, external_deps
        )

        return ProjectComplexity(
            lines_of_code=lines_of_code,
            class_count=class_count,
            method_count=method_count,
            inheritance_depth=inheritance_depth,
            external_dependencies=external_deps,
            project_type=project_type,
            complexity_score=complexity_score,
        )

    def _count_lines_of_code(self, file_path: Path) -> int:
        """
        Count non-empty, non-comment lines of actual code

        Args:
            file_path: Path to the file being analyzed

        Returns:
            Number of non-empty, non-comment lines of actual code
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            loc = 0
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith("#") and not stripped.startswith('"""'):
                    loc += 1
            return loc
        except Exception:
            return 0

    def _determine_project_type(self, lines: int, classes: int, methods: int) -> ProjectType:
        """
        Determine project type based on size and complexity metrics

        Args:
            lines: Number of lines of code
            classes: Number of classes
            methods: Number of methods

        Returns:
            ProjectType enum value based on metrics
        """
        if lines < 100 and classes <= 2:
            return ProjectType.SIMPLE_SCRIPT
        elif lines < 500 and classes <= 5:
            return ProjectType.UTILITY_MODULE
        elif lines < 1500 and classes <= 15:
            return ProjectType.SMALL_APPLICATION
        elif classes > 0 and any(
            ["test" in str(file_path).lower(), "lib" in str(file_path).lower(), "__init__" in str(file_path)]
            for file_path in [Path(".")]
        ):  # Heuristic for library detection
            return ProjectType.LIBRARY_FRAMEWORK
        else:
            return ProjectType.LARGE_APPLICATION

    def _calculate_inheritance_depth(self, lsp_analysis: LSPAnalysisResult) -> int:
        """
        Calculate maximum inheritance depth from LSP violations

        Args:
            lsp_analysis: LSP analysis result

        Returns:
            Maximum inheritance depth from LSP violations
        """
        # Simplified approach - count classes with inheritance-related issues
        return len([v for v in lsp_analysis.violations if "inheritance" in v.description.lower()])

    def _calculate_complexity_score(self, lines: int, classes: int, methods: int, inheritance: int, deps: int) -> float:
        """
        Calculate normalized complexity score (0.0 = simple, 1.0 = very complex)

        Args:
            lines: Number of lines of code
            classes: Number of classes
            methods: Number of methods
            inheritance: Maximum inheritance depth from LSP violations
            deps: Number of external dependencies

        Returns:
            Normalized complexity score (0.0 - 1.0)
        """
        # Normalize each metric to 0.0-1.0 range
        line_score = min(lines / 2000, 1.0)  # Max 2000 lines
        class_score = min(classes / 20, 1.0)  # Max 20 classes
        method_score = min(methods / 100, 1.0)  # Max 100 methods
        inheritance_score = min(inheritance / 5, 1.0)  # Max 5 inheritance levels
        deps_score = min(deps / 30, 1.0)  # Max 30 external dependencies

        # Weighted average of complexity factors
        complexity = (
            line_score * 0.3  # Lines of code weight
            + class_score * 0.25  # Class count weight
            + method_score * 0.2  # Method count weight
            + inheritance_score * 0.15  # Inheritance complexity weight
            + deps_score * 0.1  # External dependencies weight
        )

        return round(complexity, 2)


class AdaptiveWeightCalculator:
    """Calculates context-aware weights and thresholds for SOLID principles"""

    def calculate_adaptive_weights(self, complexity: ProjectComplexity) -> dict[str, float]:
        """
        Calculate SOLID principle weights based on project complexity and type

        Args:
            complexity: Project complexity object

        Returns:
            Dict of SOLID principle weights

        Different project types benefit from different emphasis on SOLID principles:
        - Scripts: Focus on simplicity (SRP) and loose coupling (DIP)
        - Utilities: Balanced approach with reusability focus
        - Libraries: Extensibility (OCP) and clean interfaces (ISP)
        - Large Apps: Maintainability (SRP) and extensibility (OCP)
        """

        base_weights = {
            "srp": 0.25,  # Single Responsibility Principle
            "ocp": 0.20,  # Open/Closed Principle
            "lsp": 0.20,  # Liskov Substitution Principle
            "isp": 0.15,  # Interface Segregation Principle
            "dip": 0.20,  # Dependency Inversion Principle
        }

        # Adapt weights based on project type characteristics
        if complexity.project_type == ProjectType.SIMPLE_SCRIPT:
            # Scripts: Prioritize simplicity over complex architecture patterns
            return {
                "srp": 0.4,  # Keep functions/classes focused and simple
                "ocp": 0.1,  # Avoid over-engineering with complex extension points
                "lsp": 0.1,  # Minimal inheritance hierarchy needed
                "isp": 0.1,  # Simple, straightforward interfaces
                "dip": 0.3,  # Avoid tight coupling but don't over-complicate
            }

        elif complexity.project_type == ProjectType.UTILITY_MODULE:
            # Utilities: Balance simplicity with reusability
            return {
                "srp": 0.3,  # Clear, focused utility functions
                "ocp": 0.2,  # Some extensibility for different use cases
                "lsp": 0.15,  # Moderate inheritance patterns
                "isp": 0.15,  # Clean interfaces for utility functions
                "dip": 0.2,  # Reasonable decoupling
            }

        elif complexity.project_type == ProjectType.LIBRARY_FRAMEWORK:
            # Libraries: Strict adherence to SOLID, focus on extensibility and interfaces
            return {
                "srp": 0.2,  # Good separation but not the top priority
                "ocp": 0.3,  # Critical: Must be extensible without modification
                "lsp": 0.2,  # Solid inheritance hierarchies for public APIs
                "isp": 0.25,  # Critical: Clean, segregated public interfaces
                "dip": 0.05,  # Less critical as libraries define abstractions
            }

        elif complexity.project_type == ProjectType.LARGE_APPLICATION:
            # Large applications: Strict SOLID compliance for maintainability
            return {
                "srp": 0.3,  # Critical for long-term maintainability
                "ocp": 0.25,  # Important for adding features without breaking existing code
                "lsp": 0.2,  # Solid inheritance patterns
                "isp": 0.15,  # Clean internal interfaces
                "dip": 0.1,  # Important for testing and modularity
            }

        else:  # SMALL_APPLICATION - use balanced approach
            return base_weights

    def calculate_adaptive_thresholds(self, complexity: ProjectComplexity) -> dict[str, float]:
        """
        Calculate context-aware quality thresholds for different project types

        Args:
            complexity: Project complexity object

        Returns:
            Dict with 'good' and 'acceptable' threshold values

        Different project types have different quality expectations:
        - Scripts: More lenient thresholds - don't demand over-engineering
        - Libraries: Stricter thresholds - higher quality standards
        - Large projects: Stricter thresholds - need better architecture
        - Small applications: Balanced approach
        """

        base_thresholds = {"good": 0.8, "acceptable": 0.6}

        if complexity.project_type == ProjectType.SIMPLE_SCRIPT:
            # More lenient thresholds for simple scripts - don't demand over-engineering
            return {"good": 0.6, "acceptable": 0.4}

        elif complexity.project_type == ProjectType.LIBRARY_FRAMEWORK:
            # Stricter thresholds for public APIs - higher quality standards
            return {"good": 0.9, "acceptable": 0.7}

        elif complexity.complexity_score > 0.8:
            # Stricter thresholds for very complex projects - need better architecture
            return {"good": 0.85, "acceptable": 0.65}

        return base_thresholds


class ContextualRecommendationGenerator:
    """Generates context-aware recommendations based on project complexity and type"""

    def generate_contextual_recommendations(
        self,
        scores: SOLIDScores,
        complexity: ProjectComplexity,
        thresholds: dict[str, float],
        srp_analysis: dict[str, DependencyInfo],
        ocp_analysis: OCPAnalysisResult,
        lsp_analysis: LSPAnalysisResult,
        isp_analysis: ISPAnalysisResult,
        dip_analysis: DIPAnalysisResult,
    ) -> list[str]:
        """
        Generate smart recommendations adapted to project context and complexity

        Args:
            scores: SOLID scores
            complexity: Project complexity object
            thresholds: Dict with 'good' and 'acceptable' threshold values
            srp_analysis: SRP analysis result
            ocp_analysis: OCP analysis result
            lsp_analysis: LSP analysis result
            isp_analysis: ISP analysis result
            dip_analysis: DIP analysis result

        Returns:
            List of recommendations

        Provides targeted advice based on:
        - Project type (Script, Utility, Library, Application)
        - Complexity score and characteristics
        - Context-appropriate quality thresholds
        - Specific SOLID principle violations
        """

        recommendations = []
        thresholds["good"]
        thresholds["acceptable"]

        # Add project context header
        recommendations.append(f"📋 Project Type: {complexity.project_type.value.replace('_', ' ').title()}")
        recommendations.append(f"📊 Complexity Score: {complexity.complexity_score:.2f}/1.00")

        # Generate context-specific SOLID recommendations
        if complexity.project_type == ProjectType.SIMPLE_SCRIPT:
            recommendations.extend(self._script_recommendations(scores, complexity, thresholds))

        elif complexity.project_type == ProjectType.UTILITY_MODULE:
            recommendations.extend(self._utility_recommendations(scores, complexity, thresholds))

        elif complexity.project_type == ProjectType.LIBRARY_FRAMEWORK:
            recommendations.extend(self._library_recommendations(scores, complexity, thresholds))

        elif complexity.project_type == ProjectType.LARGE_APPLICATION:
            recommendations.extend(self._application_recommendations(scores, complexity, thresholds))

        else:  # SMALL_APPLICATION
            recommendations.extend(self._standard_recommendations(scores, complexity, thresholds))

        # Add detailed violation analysis for deeper insights
        recommendations.extend(
            self._detailed_violation_analysis(
                scores, srp_analysis, ocp_analysis, lsp_analysis, isp_analysis, dip_analysis, complexity
            )
        )

        return recommendations

    def _script_recommendations(
        self, scores: SOLIDScores, complexity: ProjectComplexity, thresholds: dict[str, float]
    ) -> list[str]:
        """
        Generate recommendations specifically for simple scripts

        Args:
            scores: SOLID scores
            complexity: Project complexity object
            thresholds: Dict with 'good' and 'acceptable' threshold values

        Returns:
            List of recommendations
        """
        recs = []

        if scores.overall_score >= thresholds["good"]:
            recs.append("✅ Excellent! Your script follows good practices while staying simple")
            recs.append("💡 Insight: This level of organization is perfect for scripts")
        elif scores.overall_score >= thresholds["acceptable"]:
            recs.append("👍 Good balance of simplicity and structure for a script")
            if scores.srp_score < 0.6:
                recs.append("⚠️  Focus: Keep functions focused - single purpose is key for scripts")
        else:
            recs.append("🔧 Even simple scripts benefit from basic organization")
            recs.append("💡 Priority: Focus on Single Responsibility - one script, one main purpose")
            recs.append("⚠️  Warning: Avoid over-engineering - keep abstractions simple for basic tasks")

        return recs

    def _utility_recommendations(
        self, scores: SOLIDScores, complexity: ProjectComplexity, thresholds: dict[str, float]
    ) -> list[str]:
        """Generate recommendations for utility modules

        Args:
            scores: SOLID scores
            complexity: Project complexity object
            thresholds: Dict with 'good' and 'acceptable' threshold values

        Returns:
            List of recommendations
        """
        recs = []

        if scores.overall_score >= thresholds["good"]:
            recs.append("🌟 Excellent utility module structure!")
        else:
            recs.append("🔧 Utility modules benefit from clean, focused design")
            if scores.ocp_score < 0.7:
                recs.append("🔓 Consider: Make utilities extensible for different use cases")
            if scores.isp_score < 0.7:
                recs.append("🎯 Consider: Separate interfaces for different utility functions")

        return recs

    def _library_recommendations(
        self, scores: SOLIDScores, complexity: ProjectComplexity, thresholds: dict[str, float]
    ) -> list[str]:
        """
        Generate recommendations for libraries and frameworks

        Args:
            scores: SOLID scores
            complexity: Project complexity object
            thresholds: Dict with 'good' and 'acceptable' threshold values

        Returns:
            List of recommendations
        """
        recs = []

        if scores.overall_score >= thresholds["good"]:
            recs.append("🏆 Excellent library architecture!")
        else:
            recs.append("⚠️  Libraries require strict SOLID adherence for maintainability")
            if scores.ocp_score < 0.8:
                recs.append("🔓 CRITICAL: Libraries must be Open/Closed - extensible without modification")
            if scores.isp_score < 0.8:
                recs.append("🎯 CRITICAL: Clean, segregated interfaces are essential for public APIs")
            if scores.lsp_score < 0.8:
                recs.append("🔄 CRITICAL: Inheritance hierarchies must be solid for library consumers")

        return recs

    def _application_recommendations(
        self, scores: SOLIDScores, complexity: ProjectComplexity, thresholds: dict[str, float]
    ) -> list[str]:
        """
        Generate recommendations for large applications

        Args:
            scores: SOLID scores
            complexity: Project complexity object
            thresholds: Dict with 'good' and 'acceptable' threshold values

        Returns:
            List of recommendations
        """
        recs = []

        if scores.overall_score >= thresholds["good"]:
            recs.append("🌟 Well-architected application!")
        else:
            recs.append("🔧 Large applications require strong SOLID foundation")
            if scores.srp_score < 0.7:
                recs.append("📋 PRIORITY: Single Responsibility is crucial for long-term maintainability")
            if scores.dip_score < 0.7:
                recs.append("🔄 PRIORITY: Dependency Inversion enables testing and flexibility")

        return recs

    def _standard_recommendations(
        self, scores: SOLIDScores, complexity: ProjectComplexity, thresholds: dict[str, float]
    ) -> list[str]:
        """Generate standard recommendations for medium-sized applications

        Args:
            scores: SOLID scores
            complexity: Project complexity object
            thresholds: Dict with 'good' and 'acceptable' threshold values

        Returns:
            List of recommendations
        """
        return ["👍 Standard SOLID principles apply - balanced approach recommended"]

    def _detailed_violation_analysis(
        self,
        scores: SOLIDScores,
        srp_analysis: dict[str, DependencyInfo],
        ocp_analysis: OCPAnalysisResult,
        lsp_analysis: LSPAnalysisResult,
        isp_analysis: ISPAnalysisResult,
        dip_analysis: DIPAnalysisResult,
        complexity: ProjectComplexity,
    ) -> list[str]:
        """Provide detailed analysis of violations with project context

        Args:
            scores: SOLID scores
            srp_analysis: SRP analysis result
            ocp_analysis: OCP analysis result
            lsp_analysis: LSP analysis result
            isp_analysis: ISP analysis result
            dip_analysis: DIP analysis result
            complexity: Project complexity object

        Returns:
            List of detailed violation analysis

        Shows different levels of detail based on project type:
        - Complex projects: Show all significant violations
        - Simple scripts: Only show critical issues that matter for scripts
        """
        details = []

        # Show appropriate level of detail for the project type
        if complexity.project_type in [ProjectType.LIBRARY_FRAMEWORK, ProjectType.LARGE_APPLICATION]:
            # Show all significant violations for complex projects that need strict adherence
            if ocp_analysis.violations:
                details.append(f"🔓 OCP Issues: {len(ocp_analysis.violations)} extensibility violations found")
            if isp_analysis.violations:
                details.append(f"🎯 ISP Issues: {len(isp_analysis.violations)} interface segregation problems")

        elif complexity.project_type == ProjectType.SIMPLE_SCRIPT:
            # Only highlight truly problematic areas for scripts
            srp_issues = [name for name, info in srp_analysis.items() if info.srp_score < 0.4]
            if srp_issues:
                details.append(f"📋 Focus Areas: {', '.join(srp_issues[:2])} need better organization")

        return details


class SOLIDScorer:
    """Enhanced SOLID scorer with context-aware analysis and adaptive weighting"""

    def __init__(self) -> None:
        """Initialize the SOLID scorer."""
        self.complexity_analyzer = ProjectComplexityAnalyzer()
        self.weight_calculator = AdaptiveWeightCalculator()
        self.recommendation_generator = ContextualRecommendationGenerator()

    def calculate_overall_score(self, scores: SOLIDScores, weights: dict[str, float] | None = None) -> float:
        """
        Calculate overall SOLID score with optional adaptive weights

        Args:
            scores: Individual SOLID principle scores
            weights: Optional custom weights dict, defaults to equal weighting

        Returns:
            Weighted overall SOLID score (0.0 - 1.0)
        """
        if weights is None:
            # Use default equal weighting
            weights = {
                "srp": 0.25,  # Single Responsibility Principle
                "ocp": 0.20,  # Open/Closed Principle
                "lsp": 0.20,  # Liskov Substitution Principle
                "isp": 0.15,  # Interface Segregation Principle
                "dip": 0.20,  # Dependency Inversion Principle
            }

        # Calculate weighted average
        overall = (
            scores.srp_score * weights["srp"]
            + scores.ocp_score * weights["ocp"]
            + scores.lsp_score * weights["lsp"]
            + scores.isp_score * weights["isp"]
            + scores.dip_score * weights["dip"]
        )

        return round(overall, 2)

    def generate_smart_recommendations(
        self,
        scores: SOLIDScores,
        complexity: ProjectComplexity,
        srp_analysis: dict[str, DependencyInfo],
        ocp_analysis: OCPAnalysisResult,
        lsp_analysis: LSPAnalysisResult,
        isp_analysis: ISPAnalysisResult,
        dip_analysis: DIPAnalysisResult,
    ) -> list[str]:
        """
        Generate smart, context-aware recommendations based on project complexity

        Args:
            scores: SOLID scores
            complexity: Project complexity object
            srp_analysis: SRP analysis result
            ocp_analysis: OCP analysis result
            lsp_analysis: LSP analysis result
            isp_analysis: ISP analysis result
            dip_analysis: DIP analysis result

        Returns:
            List of recommendations
        """
        thresholds = self.weight_calculator.calculate_adaptive_thresholds(complexity)
        return self.recommendation_generator.generate_contextual_recommendations(
            scores, complexity, thresholds, srp_analysis, ocp_analysis, lsp_analysis, isp_analysis, dip_analysis
        )

    def generate_recommendations(
        self,
        scores: SOLIDScores,
        srp_analysis: dict[str, DependencyInfo],
        ocp_analysis: OCPAnalysisResult,
        lsp_analysis: LSPAnalysisResult,
        isp_analysis: ISPAnalysisResult,
        dip_analysis: DIPAnalysisResult,
    ) -> list[str]:
        """
        Legacy method - generates basic recommendations without context awareness

        Args:
            scores: SOLID scores
            srp_analysis: SRP analysis result
            ocp_analysis: OCP analysis result
            lsp_analysis: LSP analysis result
            isp_analysis: ISP analysis result
            dip_analysis: DIP analysis result

        Returns:
            List of recommendations
        """
        recommendations = []

        # Basic recommendations for backward compatibility
        if scores.overall_score >= 0.8:
            recommendations.append("🎉 Excellent work! Code follows SOLID principles well")
        elif scores.overall_score >= 0.6:
            recommendations.append("👍 Good foundation, but there are opportunities for improvement")
        else:
            recommendations.append("⚠️  Code requires significant refactoring for SOLID compliance")

        return recommendations

    def generate_contextual_summary(self, scores: SOLIDScores, complexity: ProjectComplexity) -> str:
        """
        Generate context-aware summary based on project complexity and type

        Provides tailored summaries that reflect appropriate expectations for different project types

        Args:
            scores: SOLID scores
            complexity: Project complexity object

        Returns:
            String summary of the project complexity and type
        """
        thresholds = self.weight_calculator.calculate_adaptive_thresholds(complexity)

        if scores.overall_score >= thresholds["good"]:
            if complexity.project_type == ProjectType.SIMPLE_SCRIPT:
                return f"Perfect script organization! 🎯 (Complexity: {complexity.complexity_score:.1f})"
            elif complexity.project_type == ProjectType.LIBRARY_FRAMEWORK:
                return f"Exceptional library architecture! 🏆 (Complexity: {complexity.complexity_score:.1f})"
            else:
                return f"Great SOLID architecture! 🌟 (Complexity: {complexity.complexity_score:.1f})"

        elif scores.overall_score >= thresholds["acceptable"]:
            if complexity.project_type == ProjectType.SIMPLE_SCRIPT:
                return f"Good script structure 👍 (Complexity: {complexity.complexity_score:.1f})"
            else:
                return f"Good foundation, some improvements needed 👍 (Complexity: {complexity.complexity_score:.1f})"

        else:
            if complexity.project_type == ProjectType.SIMPLE_SCRIPT:
                return f"Could use better organization 🔧 (Complexity: {complexity.complexity_score:.1f})"
            elif complexity.project_type == ProjectType.LIBRARY_FRAMEWORK:
                return f"Critical issues for library code! 🚨 (Complexity: {complexity.complexity_score:.1f})"
            else:
                return f"Significant refactoring needed ⚠️ (Complexity: {complexity.complexity_score:.1f})"

    def generate_summary(self, scores: SOLIDScores) -> str:
        """
        Generate basic summary without context (legacy method)

        Args:
            scores: SOLID scores

        Returns:
            String summary of the SOLID scores
        """
        if scores.overall_score >= 0.9:
            return "Exceptional SOLID compliance! 🏆"
        elif scores.overall_score >= 0.8:
            return "Great SOLID architecture! 🌟"
        elif scores.overall_score >= 0.7:
            return "Good SOLID foundation with room for improvement 👍"
        elif scores.overall_score >= 0.6:
            return "Moderate SOLID compliance, consider refactoring ⚠️"
        elif scores.overall_score >= 0.4:
            return "Poor SOLID compliance, significant refactoring needed 🔧"
        else:
            return "Critical SOLID violations, major restructuring required 🚨"


def analyze_solid_comprehensive(file_path: Path, use_smart_analysis: bool = True) -> SOLIDAnalysisResult:
    """
    Performs comprehensive analysis of all SOLID principles with contextual adaptation

    Args:
        file_path: Path to Python file to analyze
        use_smart_analysis: Whether to use smart contextual analysis (default: True)

    Returns:
        SOLIDAnalysisResult with scores, recommendations, and complexity analysis
    """
    print(f"🔍 SOLID Principles Analysis: {file_path.name}")

    # Run individual SOLID principle analyzers
    print("   📋 SRP Analysis...")
    srp_result = analyze_srp(file_path)
    srp_score = sum(info.srp_score for info in srp_result.values()) / len(srp_result) if srp_result else 1.0

    print("   🔓 OCP Analysis...")
    ocp_result = analyze_ocp(file_path)

    print("   🔄 LSP Analysis...")
    lsp_result = analyze_lsp(file_path)

    print("   🎯 ISP Analysis...")
    isp_result = analyze_isp(file_path)

    print("   🔄 DIP Analysis...")
    dip_result = analyze_dip(file_path)

    # Create enhanced SOLID scorer with smart capabilities
    scorer = SOLIDScorer()

    scores = SOLIDScores(
        srp_score=srp_score,
        ocp_score=ocp_result.ocp_score,
        lsp_score=lsp_result.lsp_score,
        isp_score=isp_result.isp_score,
        dip_score=dip_result.dip_score,
        overall_score=0.0,  # Will be calculated with adaptive or default weights
    )

    if use_smart_analysis:
        # 🧠 SMART ANALYSIS: Project complexity and context analysis
        print("   🧠 Project complexity analysis...")
        complexity = scorer.complexity_analyzer.analyze_project(
            srp_result, ocp_result, lsp_result, isp_result, dip_result, file_path
        )

        # Calculate adaptive weights based on project characteristics
        adaptive_weights = scorer.weight_calculator.calculate_adaptive_weights(complexity)

        # Calculate overall score with adaptive weights
        scores.overall_score = scorer.calculate_overall_score(scores, adaptive_weights)

        # Generate smart, contextual recommendations
        recommendations = scorer.generate_smart_recommendations(
            scores, complexity, srp_result, ocp_result, lsp_result, isp_result, dip_result
        )

        # Generate context-aware summary
        summary = scorer.generate_contextual_summary(scores, complexity)

        print(f"   📊 Project Type: {complexity.project_type.value.replace('_', ' ').title()}")
        print(f"   📈 Complexity: {complexity.complexity_score:.2f}/1.00")

    else:
        # Legacy analysis without smart features
        adaptive_weights = {"srp": 0.25, "ocp": 0.20, "lsp": 0.20, "isp": 0.15, "dip": 0.20}
        scores.overall_score = scorer.calculate_overall_score(scores)
        recommendations = scorer.generate_recommendations(
            scores, srp_result, ocp_result, lsp_result, isp_result, dip_result
        )
        summary = scorer.generate_summary(scores)
        complexity = ProjectComplexity(0, 0, 0, 0, 0, ProjectType.SIMPLE_SCRIPT, 0.0)

    return SOLIDAnalysisResult(
        file_path=str(file_path),
        scores=scores,
        srp_analysis=srp_result,
        ocp_analysis=ocp_result,
        lsp_analysis=lsp_result,
        isp_analysis=isp_result,
        dip_analysis=dip_result,
        recommendations=recommendations,
        summary=summary,
        project_complexity=complexity,
        adaptive_weights=adaptive_weights,
    )


def print_solid_report(result: SOLIDAnalysisResult, detailed: bool = False, show_smart_info: bool = True) -> None:
    """
    Print comprehensive SOLID analysis report with smart contextual information

    Args:
        result: Complete SOLID analysis result
        detailed: Whether to show detailed violation analysis
        show_smart_info: Whether to display smart analysis information
    """
    print(f"\n{'=' * 70}")
    print(f"🏆 SOLID Analysis Report: {Path(result.file_path).name}")
    print(f"{'=' * 70}")

    # Smart Analysis Information (if available)
    if show_smart_info and hasattr(result, "project_complexity"):
        complexity = result.project_complexity
        print("\n🧠 Smart Analysis:")
        print(f"   📋 Project Type: {complexity.project_type.value.replace('_', ' ').title()}")
        print(f"   📊 Complexity Score: {complexity.complexity_score:.2f}/1.00")
        print(f"   📈 Lines of Code: {complexity.lines_of_code}")
        print(f"   🏗️  Classes: {complexity.class_count}")

        if hasattr(result, "adaptive_weights"):
            print("\n⚖️  Adaptive Weights (for this project type):")
            weights = result.adaptive_weights
            print(f"   📋 SRP: {weights['srp']:.1%} | 🔓 OCP: {weights['ocp']:.1%} | 🔄 LSP: {weights['lsp']:.1%}")
            print(f"   🎯 ISP: {weights['isp']:.1%} | 🔄 DIP: {weights['dip']:.1%}")

    # Calculate context-aware thresholds for intelligent color coding
    if hasattr(result, "project_complexity"):
        scorer = SOLIDScorer()
        thresholds = scorer.weight_calculator.calculate_adaptive_thresholds(result.project_complexity)
        good_threshold = thresholds["good"]
        acceptable_threshold = thresholds["acceptable"]
    else:
        good_threshold = 0.8
        acceptable_threshold = 0.6

    print("\n📊 SOLID Scores (with context-aware thresholds):")
    print(
        f"   📋 SRP: {result.scores.srp_score:.2f}/1.00 {'🟢' if result.scores.srp_score >= good_threshold else '🟡' if result.scores.srp_score >= acceptable_threshold else '🔴'}"
    )
    print(
        f"   🔓 OCP: {result.scores.ocp_score:.2f}/1.00 {'🟢' if result.scores.ocp_score >= good_threshold else '🟡' if result.scores.ocp_score >= acceptable_threshold else '🔴'}"
    )
    print(
        f"   🔄 LSP: {result.scores.lsp_score:.2f}/1.00 {'🟢' if result.scores.lsp_score >= good_threshold else '🟡' if result.scores.lsp_score >= acceptable_threshold else '🔴'}"
    )
    print(
        f"   🎯 ISP: {result.scores.isp_score:.2f}/1.00 {'🟢' if result.scores.isp_score >= good_threshold else '🟡' if result.scores.isp_score >= acceptable_threshold else '🔴'}"
    )
    print(
        f"   🔄 DIP: {result.scores.dip_score:.2f}/1.00 {'🟢' if result.scores.dip_score >= good_threshold else '🟡' if result.scores.dip_score >= acceptable_threshold else '🔴'}"
    )

    print(f"\n🎯 Overall SOLID Score: {result.scores.overall_score:.2f}/1.00")
    print(f"📋 Summary: {result.summary}")

    # Quick statistics overview
    print("\n📈 Quick Stats:")
    print(f"   • Classes analyzed (SRP): {len(result.srp_analysis)}")
    print(f"   • OCP violations: {len(result.ocp_analysis.violations)}")
    print(f"   • LSP violations: {len(result.lsp_analysis.violations)}")
    print(f"   • ISP violations: {len(result.isp_analysis.violations)}")
    print(f"   • DIP violations: {len(result.dip_analysis.violations)}")

    # Smart contextual recommendations
    if result.recommendations:
        print("\n💡 Smart Recommendations:")
        for recommendation in result.recommendations:
            print(f"   {recommendation}")

    # Detailed violation analysis (optional)
    if detailed:
        print("\n🔍 Detailed Analysis:")

        # Most problematic SRP classes
        if result.srp_analysis:
            worst_srp = min(result.srp_analysis.items(), key=lambda x: x[1].srp_score)
            print(f"   📋 Worst SRP class: {worst_srp[0]} (score: {worst_srp[1].srp_score:.2f})")
            print(f"      Responsibilities: {', '.join(worst_srp[1].responsibilities)}")

        # Top OCP violations
        if result.ocp_analysis.violations:
            print(f"   🔓 Top OCP violation: {result.ocp_analysis.violations[0].description}")

        # Top LSP violations
        if result.lsp_analysis.violations:
            print(f"   🔄 Top LSP violation: {result.lsp_analysis.violations[0].description}")


def print_json_report(result: SOLIDAnalysisResult) -> None:
    """
    Output comprehensive SOLID analysis report in JSON format with smart analysis data

    Args:
        result: Complete SOLID analysis result to convert to JSON
    """
    # Convert dataclasses to dictionaries for JSON serialization
    json_result: dict[str, Any] = {
        "file_path": result.file_path,
        "scores": asdict(result.scores),
        "summary": result.summary,
        "recommendations": result.recommendations,
        "violations": {
            "srp_count": sum(len(info.violations) for info in result.srp_analysis.values()),
            "ocp_count": len(result.ocp_analysis.violations),
            "lsp_count": len(result.lsp_analysis.violations),
            "isp_count": len(result.isp_analysis.violations),
            "dip_count": len(result.dip_analysis.violations),
        },
    }

    # Add smart analysis information if available
    if hasattr(result, "project_complexity"):
        complexity = result.project_complexity
        json_result["smart_analysis"] = {
            "project_type": complexity.project_type.value,
            "complexity_score": complexity.complexity_score,
            "lines_of_code": complexity.lines_of_code,
            "class_count": complexity.class_count,
            "method_count": complexity.method_count,
            "inheritance_depth": complexity.inheritance_depth,
            "external_dependencies": complexity.external_dependencies,
        }

        # Include adaptive weights for transparency
        if hasattr(result, "adaptive_weights"):
            json_result["smart_analysis"]["adaptive_weights"] = result.adaptive_weights

    print(json.dumps(json_result, indent=2, ensure_ascii=False))


def main() -> None:
    """Main CLI entry point for SOLID Scorer with smart analysis capabilities"""
    parser = argparse.ArgumentParser(
        description="SOLID Scorer - Smart comprehensive analysis of all SOLID principles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
    python __main__.py my_code.py
    python __main__.py --report my_code.py
    python __main__.py --json my_code.py > analysis.json
    python __main__.py --legacy my_code.py  # classic scoring system
    python __main__.py --smart my_code.py   # smart system (default)
    
    # Alternative: run as module
    python -m solid-checker my_code.py

Smart Analysis Features:
    • Automatic project type detection (Script, Utility, Library, Application)
    • Adaptive SOLID principle weighting based on project characteristics
    • Context-aware quality thresholds and recommendations
    • Project complexity analysis and intelligent scoring
        """,
    )

    parser.add_argument("file", help="Python file to analyze")
    parser.add_argument("--report", action="store_true", help="Show detailed analysis report")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--smart", action="store_true", default=True, help="Use smart contextual analysis (default)")
    parser.add_argument("--legacy", action="store_true", help="Use legacy analysis system (no adaptation)")
    parser.add_argument("--no-smart-info", action="store_true", help="Hide smart analysis information in report")

    args = parser.parse_args()

    # Handle mutually exclusive analysis options
    use_smart_analysis = args.smart and not args.legacy
    show_smart_info = not args.no_smart_info

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ File {file_path} not found")
        sys.exit(1)

    try:
        if use_smart_analysis:
            print("🧠 Starting smart SOLID analysis...")
        else:
            print("📊 Starting classic SOLID analysis...")

        result = analyze_solid_comprehensive(file_path, use_smart_analysis=use_smart_analysis)

        if args.json:
            print_json_report(result)
        else:
            print_solid_report(result, detailed=args.report, show_smart_info=show_smart_info)

    except Exception as e:
        print(f"❌ Analysis error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
