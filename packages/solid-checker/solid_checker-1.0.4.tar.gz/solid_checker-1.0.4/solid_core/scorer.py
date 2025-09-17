"""
Core SOLID scorer class.

This module contains the main SOLIDScorer class that orchestrates
SOLID principle analysis with context-aware scoring and recommendations.
"""

from dip import DIPAnalysisResult
from isp import ISPAnalysisResult
from lsp import LSPAnalysisResult
from ocp import OCPAnalysisResult
from srp import DependencyInfo

from .models import ProjectComplexity, ProjectType, SOLIDScores
from .smart_analysis import AdaptiveWeightCalculator, ContextualRecommendationGenerator, ProjectComplexityAnalyzer


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

