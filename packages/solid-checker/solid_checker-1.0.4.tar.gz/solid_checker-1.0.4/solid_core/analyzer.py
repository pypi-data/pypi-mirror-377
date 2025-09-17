"""
Main SOLID analysis function.

This module contains the core analyze_solid_comprehensive function
that orchestrates the complete SOLID analysis workflow.
"""

from pathlib import Path

from dip import analyze_file as analyze_dip
from isp import analyze_file as analyze_isp
from lsp import analyze_file as analyze_lsp
from ocp import analyze_file as analyze_ocp
from srp import DependencyInfo
from srp import analyze_file as analyze_srp

from .models import ProjectComplexity, ProjectType, SOLIDAnalysisResult, SOLIDScores
from .scorer import SOLIDScorer


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
    srp_score = _calculate_module_srp_score(srp_result, file_path) if srp_result else 1.0

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


def _calculate_module_srp_score(srp_result: dict[str, DependencyInfo], file_path: Path) -> float:
    """
    Calculate intelligent module-level SRP score with architectural awareness

    Args:
        srp_result: Dictionary of class-level SRP analysis results
        file_path: Path to the analyzed file

    Returns:
        Module-level SRP score that considers architectural patterns
    """
    if not srp_result:
        return 1.0

    # Get basic statistics
    class_scores = [info.srp_score for info in srp_result.values()]
    class_names = list(srp_result.keys())
    num_classes = len(class_scores)
    avg_score = sum(class_scores) / num_classes

    # Determine module type and context
    module_name = file_path.stem.lower()
    module_context = _determine_module_context(module_name, class_names)

    # Base score starts with weighted average (good classes matter more)
    sorted_scores = sorted(class_scores, reverse=True)
    if len(sorted_scores) >= 3:
        # Weight: best 40%, middle 35%, worst 25%
        weighted_avg = (
            sum(sorted_scores[:len(sorted_scores)//2]) * 0.6 +
            sum(sorted_scores[len(sorted_scores)//2:]) * 0.4
        ) / len(sorted_scores)
    else:
        weighted_avg = avg_score

    base_score = weighted_avg

    # Apply modular cohesion bonus/penalty
    cohesion_adjustment = _calculate_module_cohesion(class_names, module_context)

    # Apply architectural pattern bonus
    architectural_bonus = _calculate_module_architectural_bonus(module_name, module_context, num_classes)

    # Apply size-based adjustment (prevent penalizing well-organized large modules)
    size_adjustment = _calculate_module_size_adjustment(num_classes, module_context, avg_score)

    final_score = base_score + cohesion_adjustment + architectural_bonus + size_adjustment

    return max(0.0, min(1.0, final_score))


def _determine_module_context(module_name: str, class_names: list[str]) -> str:
    """Determine the architectural context of the module"""

    # Check module name for architectural patterns
    architectural_modules = {
        "core": "core_module",      # Core implementation modules
        "facade": "facade_module",  # Facade pattern modules
        "protocols": "interface_module", # Protocol/interface modules
        "models": "data_module",    # Data model modules
        "utils": "utility_module",  # Utility modules
        "analyzer": "analysis_module", # Analysis modules
        "scorer": "scoring_module"  # Scoring modules
    }

    for pattern, context in architectural_modules.items():
        if pattern in module_name:
            return context

    # Check class names for domain patterns
    all_names = " ".join(class_names).lower()

    domain_patterns = {
        "analyzer": "analysis_module",
        "detector": "analysis_module",
        "processor": "processing_module",
        "manager": "coordination_module",
        "builder": "construction_module",
        "collector": "collection_module"
    }

    for pattern, context in domain_patterns.items():
        if pattern in all_names:
            return context

    return "generic_module"


def _calculate_module_cohesion(class_names: list[str], module_context: str) -> float:
    """Calculate cohesion bonus/penalty based on class name patterns"""

    if len(class_names) <= 2:
        return 0.0  # Small modules don't get cohesion bonus/penalty

    # Extract common patterns from class names
    name_words = []
    for name in class_names:
        # Split camelCase and extract meaningful parts
        import re
        words = re.findall(r'[A-Z][a-z]*', name)
        name_words.extend([w.lower() for w in words])

    # Count pattern frequency
    from collections import Counter
    word_counts = Counter(name_words)

    # Look for cohesive patterns
    cohesive_words = ["analyzer", "detector", "processor", "manager", "builder", "collector", "scorer"]
    cohesive_count = sum(word_counts.get(word, 0) for word in cohesive_words)

    # Calculate cohesion ratio
    total_meaningful_words = sum(count for word, count in word_counts.items() if len(word) > 3)
    if total_meaningful_words == 0:
        return 0.0

    cohesion_ratio = cohesive_count / total_meaningful_words

    # High cohesion gets bonus, low cohesion gets penalty
    if cohesion_ratio >= 0.6:  # 60%+ cohesive
        return min(0.15, cohesion_ratio * 0.25)  # Up to +0.15
    elif cohesion_ratio <= 0.2:  # 20% or less cohesive
        return max(-0.1, (cohesion_ratio - 0.3) * 0.5)  # Up to -0.1 penalty

    return 0.0


def _calculate_module_architectural_bonus(module_name: str, module_context: str, num_classes: int) -> float:
    """Calculate architectural pattern bonus"""

    bonus = 0.0

    # Core modules are expected to have multiple related classes
    if module_context == "core_module":
        if 3 <= num_classes <= 8:  # Sweet spot for core modules
            bonus += 0.1
        elif num_classes <= 2:
            bonus -= 0.05  # Too small for core module

    # Facade modules should be simpler
    elif module_context == "facade_module":
        if num_classes <= 3:
            bonus += 0.05
        else:
            bonus -= 0.05  # Facade too complex

    # Interface modules can have many protocols
    elif module_context == "interface_module":
        if num_classes >= 2:  # Multiple protocols is normal
            bonus += 0.05

    # Analysis modules are expected to be comprehensive
    elif module_context == "analysis_module":
        if 4 <= num_classes <= 10:  # Comprehensive analysis suite
            bonus += 0.08

    return min(bonus, 0.1)  # Cap bonus


def _calculate_module_size_adjustment(num_classes: int, module_context: str, avg_score: float) -> float:
    """Calculate size-based adjustment to prevent unfair penalties for large well-organized modules"""

    if num_classes <= 3:
        return 0.0  # No adjustment for small modules

    # If classes have generally good scores, don't penalize for size
    if avg_score >= 0.7:
        if num_classes <= 6:
            return 0.02  # Small bonus for well-organized medium modules
        elif num_classes <= 10:
            return 0.01  # Small bonus for well-organized large modules

    # If scores are poor, apply gentle penalty for size
    elif avg_score < 0.5:
        if num_classes >= 8:
            return -0.05  # Penalty for large poorly organized modules
        elif num_classes >= 5:
            return -0.02  # Small penalty for medium poorly organized modules

    return 0.0

