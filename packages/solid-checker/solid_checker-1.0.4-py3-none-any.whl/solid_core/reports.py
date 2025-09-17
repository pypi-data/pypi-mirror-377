"""
Report generation functions for SOLID analysis results.

This module contains functions for generating various types of reports
from SOLID analysis results, including console output and JSON format.
"""

import json
from pathlib import Path
from typing import Any

from .models import SOLIDAnalysisResult
from .scorer import SOLIDScorer


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
        "scores": {
            "srp_score": result.scores.srp_score,
            "ocp_score": result.scores.ocp_score,
            "lsp_score": result.scores.lsp_score,
            "isp_score": result.scores.isp_score,
            "dip_score": result.scores.dip_score,
            "overall_score": result.scores.overall_score,
        },
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


def analyze_solid_project(project_path: Path, use_smart_analysis: bool = True) -> dict[str, Any]:
    """Analyze entire project for SOLID compliance.

    Args:
        project_path: Path to project directory
        use_smart_analysis: Whether to use smart analysis features

    Returns:
        Project-wide analysis results
    """
    from .project_analysis import ProjectScanner, ProjectSOLIDAnalyzer

    # Scan project
    scanner = ProjectScanner(project_path)
    project_files, project_structure = scanner.scan_project()

    # Analyze project
    analyzer = ProjectSOLIDAnalyzer()
    results = analyzer.analyze_project(project_files, project_structure, use_smart_analysis)

    # Add smart analysis flag
    results['smart_analysis_enabled'] = use_smart_analysis

    return results


def print_project_report(results: dict[str, Any], detailed: bool = False, show_smart_info: bool = True) -> None:
    """Print comprehensive project-wide SOLID analysis report.

    Args:
        results: Analysis results from analyze_solid_project
        detailed: Whether to show detailed breakdown
        show_smart_info: Whether to show smart analysis information
    """
    overview = results['project_overview']
    scores = results['aggregated_scores']
    violations = results['structural_violations']
    recommendations = results['recommendations']

    print("\n" + "=" * 80)
    print("🏗️  PROJECT-WIDE SOLID ANALYSIS REPORT")
    print("=" * 80)

    # Project overview
    print(f"\n📁 Project: {overview['root_path']}")
    print(f"   📊 Files analyzed: {overview['analyzed_files']}/{overview['total_files']} Python files")
    print(f"   📏 Total lines: {overview['total_lines']:,}")
    print(f"   📦 Packages: {overview['packages']}")
    print(f"   🏗️  Structure quality: {'✅ Good' if overview['has_proper_structure'] else '⚠️  Needs improvement'}")
    print(f"   📁 Max depth: {overview['max_depth']} levels")

    # Overall scores (convert 0.0-1.0 range to 0.0-10.0 for display)
    print("\n🎯 OVERALL SOLID SCORES:")
    print(f"   📋 SRP (Single Responsibility): {scores['srp_score']*10:.1f}/10.0")
    print(f"   🔓 OCP (Open/Closed): {scores['ocp_score']*10:.1f}/10.0")
    print(f"   🔄 LSP (Liskov Substitution): {scores['lsp_score']*10:.1f}/10.0")
    print(f"   ✂️  ISP (Interface Segregation): {scores['isp_score']*10:.1f}/10.0")
    print(f"   🔌 DIP (Dependency Inversion): {scores['dip_score']*10:.1f}/10.0")
    print(f"   🏆 OVERALL: {scores['overall_score']*10:.1f}/10.0")

    # Grade assessment (scores are in 0.0-1.0 range)
    overall_score = scores['overall_score']
    if overall_score >= 0.8:  # 8.0/10.0
        grade = "🟢 EXCELLENT"
    elif overall_score >= 0.65:  # 6.5/10.0
        grade = "🟡 GOOD"
    elif overall_score >= 0.5:  # 5.0/10.0
        grade = "🟠 FAIR"
    else:
        grade = "🔴 NEEDS WORK"

    print(f"\n🎖️  Project Grade: {grade}")

    # Structural violations
    if violations:
        print(f"\n⚠️  STRUCTURAL VIOLATIONS ({len(violations)}):")
        for i, violation in enumerate(violations[:5], 1):  # Show top 5
            print(f"   {i}. [{violation['principle']}] {violation['description']}")
            if 'file' in violation:
                print(f"      File: {violation['file']}")
            elif 'files' in violation:
                print(f"      Files: {', '.join(violation['files'][:3])}...")

    # Recommendations
    if recommendations:
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations[:6], 1):  # Show top 6
            print(f"   {i}. {rec}")

    # Detailed file breakdown
    if detailed:
        print("\n📋 DETAILED FILE ANALYSIS:")
        file_results = results['file_results']

        # Sort files by overall score (worst first)
        sorted_files = sorted(
            file_results.items(),
            key=lambda x: x[1]['scores']['overall_score']
        )

        for i, (file_path, file_result) in enumerate(sorted_files[:10], 1):  # Top 10 worst
            file_scores = file_result['scores']
            print(f"\n   {i}. 📄 {file_path}")
            print(f"      Overall: {file_scores['overall_score']*10:.1f}, " +
                  f"SRP: {file_scores['srp_score']*10:.1f}, " +
                  f"OCP: {file_scores['ocp_score']*10:.1f}, " +
                  f"LSP: {file_scores['lsp_score']*10:.1f}, " +
                  f"ISP: {file_scores['isp_score']*10:.1f}, " +
                  f"DIP: {file_scores['dip_score']*10:.1f}")

    print("\n" + "=" * 80)


def print_project_json_report(results: dict[str, Any]) -> None:
    """Print project analysis results in JSON format.

    Args:
        results: Analysis results from analyze_solid_project
    """
    # Convert Path objects to strings for JSON serialization
    json_results = json.loads(json.dumps(results, default=str, indent=2))
    print(json.dumps(json_results, indent=2))
