#!/usr/bin/env python3
"""
🔍 SOLID Checker CLI - Smart SOLID Principles Analysis

Main entry point for the SOLID Checker tool with modular architecture.
This file contains only the CLI orchestrator, with all core functionality
organized into focused modules in the solid_core package.

Usage:
    solid-checker my_code.py                    # Single file analysis
    solid-checker .                             # Project-wide analysis
    solid-checker --report my_code.py           # Detailed analysis
    solid-checker --json my_code.py             # JSON output
    solid-checker --legacy my_code.py           # Classic analysis
"""

import argparse
import sys
from pathlib import Path

# Import all functionality from the modular solid_core package
from solid_core import (
    analyze_solid_comprehensive,
    analyze_solid_project,
    print_json_report,
    print_project_json_report,
    print_project_report,
    print_solid_report,
)


def main() -> None:
    """Main CLI entry point for SOLID Scorer with smart analysis capabilities"""
    parser = argparse.ArgumentParser(
        description="SOLID Checker - Smart comprehensive analysis of all SOLID principles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
    # Single file analysis
    solid-checker my_code.py
    solid-checker --report my_code.py
    solid-checker --json my_code.py > analysis.json

    # Project-wide analysis (NEW!)
    solid-checker .                    # analyze current directory
    solid-checker /path/to/project     # analyze project directory
    solid-checker --project .          # explicit project mode

    # Analysis modes
    solid-checker --legacy my_code.py  # classic scoring system
    solid-checker --smart my_code.py   # smart system (default)

Smart Analysis Features:
    • Automatic project type detection (Script, Utility, Library, Application)
    • Adaptive SOLID principle weighting based on project characteristics
    • Context-aware quality thresholds and recommendations
    • Project complexity analysis and intelligent scoring
    • Project-wide structural analysis (NEW!)
        """,
    )

    parser.add_argument("target", help="Python file or project directory to analyze")
    parser.add_argument("--project", action="store_true", help="Force project-wide analysis mode")
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

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"❌ Target {target_path} not found")
        sys.exit(1)

    # Determine analysis mode
    is_project_mode = args.project or target_path.is_dir()

    try:
        if is_project_mode:
            # Project-wide analysis
            if use_smart_analysis:
                print("🏗️  Starting smart project-wide SOLID analysis...")
            else:
                print("📊 Starting project-wide SOLID analysis...")

            results = analyze_solid_project(target_path, use_smart_analysis=use_smart_analysis)

            if args.json:
                print_project_json_report(results)
            else:
                print_project_report(results, detailed=args.report, show_smart_info=show_smart_info)
        else:
            # Single file analysis (existing behavior)
            if use_smart_analysis:
                print("🧠 Starting smart SOLID analysis...")
            else:
                print("📊 Starting classic SOLID analysis...")

            result = analyze_solid_comprehensive(target_path, use_smart_analysis=use_smart_analysis)

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
