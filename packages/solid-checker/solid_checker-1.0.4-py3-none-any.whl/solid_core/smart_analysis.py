"""
Smart analysis components for context-aware SOLID principle evaluation.

This module contains classes that provide intelligent, context-aware analysis
based on project complexity and type characteristics.
"""

from pathlib import Path

from dip import DIPAnalysisResult
from isp import ISPAnalysisResult
from lsp import LSPAnalysisResult
from ocp import OCPAnalysisResult
from srp import DependencyInfo

from .models import ProjectComplexity, ProjectType, SOLIDScores


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

