"""
Project-wide SOLID analysis components.

This module provides functionality for analyzing entire Python projects,
scanning directory structures, and aggregating SOLID compliance across multiple files.
"""

from pathlib import Path
from typing import Any

# Import will be done locally to avoid circular dependency
from .models import ProjectFile, ProjectStructure, SOLIDScores


class ProjectScanner:
    """Scanner for recursive Python file discovery and project structure analysis"""

    def __init__(self, root_path: Path) -> None:
        """Initialize project scanner.

        Args:
            root_path: Root directory to scan
        """
        self.root_path = Path(root_path).resolve()
        self._ignore_patterns = {
            '__pycache__', '.git', '.venv', 'venv', '.env', 'env',
            'node_modules', '.pytest_cache', '.mypy_cache', '.ruff_cache',
            'build', 'dist', '*.egg-info'
        }

    def scan_project(self) -> tuple[list[ProjectFile], ProjectStructure]:
        """Scan project and return files and structure information.

        Returns:
            Tuple of (project_files, project_structure)
        """
        python_files = []
        packages = set()
        test_files = []
        main_files = []
        total_lines = 0
        max_depth = 0

        # Recursive scan
        for py_file in self._find_python_files():
            try:
                # Read file to count lines
                with open(py_file, encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())

                relative_path = py_file.relative_to(self.root_path)
                depth = len(relative_path.parts)
                max_depth = max(max_depth, depth)

                # Classify file type
                is_init = py_file.name == '__init__.py'
                is_test = self._is_test_file(py_file)
                is_main = self._is_main_file(py_file)

                project_file = ProjectFile(
                    path=py_file,
                    relative_path=relative_path,
                    size_lines=lines,
                    is_package_init=is_init,
                    is_test_file=is_test,
                    is_main_file=is_main
                )

                python_files.append(project_file)
                total_lines += lines

                # Track packages and special files
                if is_init:
                    packages.add(str(relative_path.parent))
                elif is_test:
                    test_files.append(str(relative_path))
                elif is_main:
                    main_files.append(str(relative_path))

            except Exception:
                # Skip files that can't be read
                continue

        # Analyze structure quality
        has_proper_structure = self._assess_structure_quality(python_files, packages)

        structure = ProjectStructure(
            root_path=self.root_path,
            total_files=len(python_files),
            total_lines=total_lines,
            packages=sorted(packages),
            modules=[str(f.relative_path) for f in python_files if not f.is_package_init],
            test_files=test_files,
            main_files=main_files,
            max_depth=max_depth,
            has_proper_structure=has_proper_structure
        )

        return python_files, structure

    def _find_python_files(self) -> list[Path]:
        """Find all Python files in the project, excluding ignored patterns."""
        python_files = []

        def should_ignore_path(file_path: Path) -> bool:
            """Check if file path should be ignored."""
            # Get relative path from project root
            try:
                rel_path = file_path.relative_to(self.root_path)
                path_str = str(rel_path)

                # Check if any part of the path matches ignore patterns
                return any(pattern in path_str for pattern in self._ignore_patterns)
            except ValueError:
                # If can't get relative path, skip file
                return True

        # Walk through directory tree
        for py_file in self.root_path.rglob('*.py'):
            # Skip if path should be ignored
            if should_ignore_path(py_file):
                continue

            python_files.append(py_file)

        return python_files

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        name = file_path.name.lower()
        parent = file_path.parent.name.lower()

        return (
            name.startswith('test_') or
            name.endswith('_test.py') or
            name == 'conftest.py' or
            'test' in parent
        )

    def _is_main_file(self, file_path: Path) -> bool:
        """Check if file is a main entry point."""
        name = file_path.name.lower()
        return name in ('main.py', '__main__.py', 'app.py', 'run.py')

    def _assess_structure_quality(self, files: list[ProjectFile], packages: set[str]) -> bool:
        """Assess if project has proper structure for SOLID principles."""
        if len(files) <= 5:
            return True  # Small projects are OK with any structure

        # Check for package organization
        has_packages = len(packages) > 0

        # Check for separation of concerns
        has_tests = any(f.is_test_file for f in files)
        has_main = any(f.is_main_file for f in files)

        # Check for reasonable file sizes (not too many giant files)
        large_files = [f for f in files if f.size_lines > 500]
        has_reasonable_sizes = len(large_files) / len(files) < 0.3

        return has_packages and has_tests and has_main and has_reasonable_sizes


class ProjectSOLIDAnalyzer:
    """Analyzer for project-wide SOLID compliance"""

    def __init__(self) -> None:
        """Initialize project-wide SOLID analyzer."""
        pass

    def analyze_project(self, project_files: list[ProjectFile], structure: ProjectStructure, use_smart_analysis: bool = True) -> dict[str, Any]:
        """Analyze entire project for SOLID compliance.

        Args:
            project_files: List of Python files in project
            structure: Project structure information
            use_smart_analysis: Whether to use smart contextual analysis

        Returns:
            Comprehensive project analysis results
        """
        file_results = {}
        aggregated_scores = []
        structural_violations = []

        # Analyze each file
        for project_file in project_files:
            if project_file.is_package_init or project_file.size_lines < 10:
                continue  # Skip tiny files and empty __init__.py

            # Skip self-analysis to prevent circular dependencies
            if project_file.path.name == 'solid_scorer.py':
                print(f"⚠️ Skipping self-analysis of {project_file.relative_path}")
                continue

            try:
                # Local import to avoid circular dependency
                from .analyzer import analyze_solid_comprehensive

                # Use global analyze_solid_comprehensive function with smart analysis
                result = analyze_solid_comprehensive(project_file.path, use_smart_analysis=use_smart_analysis)
                file_results[str(project_file.relative_path)] = result
                aggregated_scores.append(result.scores)
            except Exception as e:
                print(f"⚠️ Failed to analyze {project_file.relative_path}: {str(e)[:50]}...")
                # Skip files that can't be analyzed
                continue

        # Aggregate results
        project_scores = self._aggregate_scores(aggregated_scores)

        # Analyze structural violations
        structural_violations = self._analyze_structural_violations(structure, file_results)

        return {
            'project_overview': {
                'root_path': str(structure.root_path),
                'total_files': structure.total_files,
                'analyzed_files': len(file_results),
                'total_lines': structure.total_lines,
                'packages': len(structure.packages),
                'has_proper_structure': structure.has_proper_structure,
                'max_depth': structure.max_depth
            },
            'aggregated_scores': self._scores_to_dict(project_scores),
            'file_results': {path: self._result_to_dict(result) for path, result in file_results.items()},
            'structural_violations': structural_violations,
            'recommendations': self._generate_project_recommendations(structure, project_scores, structural_violations)
        }

    def _aggregate_scores(self, scores_list: list[SOLIDScores]) -> SOLIDScores:
        """Intelligent project-wide SOLID scores aggregation with weighted averaging."""
        if not scores_list:
            return SOLIDScores(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        n = len(scores_list)

        # Sort scores to prioritize better-scoring files
        sorted_scores = sorted(scores_list, key=lambda s: s.overall_score, reverse=True)

        # Use weighted averaging - better files get higher weight
        # Top 30% files: weight 1.5, Middle 40%: weight 1.0, Bottom 30%: weight 0.7
        def calculate_weighted_avg(score_attr: str) -> float:
            total_weighted_sum = 0.0
            total_weights = 0.0

            for i, scores in enumerate(sorted_scores):
                if i < n * 0.3:  # Top 30%
                    weight = 1.5
                elif i < n * 0.7:  # Middle 40%
                    weight = 1.0
                else:  # Bottom 30%
                    weight = 0.7

                total_weighted_sum += getattr(scores, score_attr) * weight
                total_weights += weight

            return total_weighted_sum / total_weights if total_weights > 0 else 0.0

        # Calculate project-wide scores with smart weighting
        aggregated_scores = SOLIDScores(
            srp_score=calculate_weighted_avg('srp_score'),
            ocp_score=calculate_weighted_avg('ocp_score'),
            lsp_score=calculate_weighted_avg('lsp_score'),
            isp_score=calculate_weighted_avg('isp_score'),
            dip_score=calculate_weighted_avg('dip_score'),
            overall_score=calculate_weighted_avg('overall_score')
        )

        # Apply project-level bonuses for good overall architecture
        architectural_bonus = self._calculate_project_architectural_bonus(scores_list)

        return SOLIDScores(
            srp_score=min(1.0, aggregated_scores.srp_score + architectural_bonus),
            ocp_score=min(1.0, aggregated_scores.ocp_score + architectural_bonus),
            lsp_score=min(1.0, aggregated_scores.lsp_score + architectural_bonus),
            isp_score=min(1.0, aggregated_scores.isp_score + architectural_bonus),
            dip_score=min(1.0, aggregated_scores.dip_score + architectural_bonus),
            overall_score=min(1.0, aggregated_scores.overall_score + architectural_bonus)
        )

    def _calculate_project_architectural_bonus(self, scores_list: list[SOLIDScores]) -> float:
        """Calculate project-level architectural bonus based on consistency."""
        if len(scores_list) < 3:
            return 0.0

        # Bonus for consistent good scores across many files
        good_scores_count = sum(1 for s in scores_list if s.overall_score >= 0.6)
        consistency_ratio = good_scores_count / len(scores_list)

        if consistency_ratio >= 0.8:  # 80%+ files have good scores
            return 0.05  # Small bonus for consistent architecture
        elif consistency_ratio >= 0.6:  # 60%+ files have good scores
            return 0.02  # Tiny bonus

        return 0.0

    def _scores_to_dict(self, scores: SOLIDScores) -> dict[str, float]:
        """Convert SOLIDScores to dictionary for JSON serialization."""
        return {
            'srp_score': scores.srp_score,
            'ocp_score': scores.ocp_score,
            'lsp_score': scores.lsp_score,
            'isp_score': scores.isp_score,
            'dip_score': scores.dip_score,
            'overall_score': scores.overall_score
        }

    def _result_to_dict(self, result: Any) -> dict[str, Any]:
        """Convert SOLIDAnalysisResult to dictionary for JSON serialization."""
        # Simplified conversion - would need proper implementation based on actual structure
        return {
            'scores': self._scores_to_dict(result.scores)
        }

    def _analyze_structural_violations(self, structure: ProjectStructure, file_results: dict[str, Any]) -> list[dict[str, Any]]:
        """Analyze structural violations of SOLID principles."""
        violations = []

        # SRP: Check for god modules (too many responsibilities)
        for file_path, result in file_results.items():
            if result.scores.srp_score < 0.5:
                violations.append({
                    'principle': 'SRP',
                    'type': 'god_module',
                    'file': file_path,
                    'score': result.scores.srp_score,
                    'description': 'Module has too many responsibilities - consider splitting'
                })

        # OCP: Check for modification-prone structures
        low_ocp_files = [fp for fp, r in file_results.items() if r.scores.ocp_score < 0.4]
        if len(low_ocp_files) > len(file_results) * 0.3:  # >30% of files
            violations.append({
                'principle': 'OCP',
                'type': 'modification_prone_architecture',
                'files': low_ocp_files[:5],  # Show first 5
                'description': 'Many modules are not properly closed for modification'
            })

        # DIP: Check for high coupling between packages
        if len(structure.packages) > 1:
            # This is simplified - could be enhanced with import analysis
            high_coupling_files = [fp for fp, r in file_results.items() if r.scores.dip_score < 0.5]
            if len(high_coupling_files) > len(file_results) * 0.4:
                violations.append({
                    'principle': 'DIP',
                    'type': 'high_coupling',
                    'description': 'High coupling detected between modules - consider dependency injection'
                })

        # ISP: Check for large interfaces (many methods)
        # This could be enhanced with AST analysis

        return violations

    def _generate_project_recommendations(
        self,
        structure: ProjectStructure,
        scores: SOLIDScores,
        violations: list[dict[str, Any]]
    ) -> list[str]:
        """Generate project-level recommendations."""
        recommendations = []

        # Structure recommendations
        if not structure.has_proper_structure:
            recommendations.append("📁 Consider organizing code into packages for better SRP compliance")

        if structure.max_depth > 4:
            recommendations.append("📁 Deep directory nesting detected - consider flattening structure")

        if not structure.test_files:
            recommendations.append("🧪 Add unit tests to support LSP compliance and safe refactoring")

        # Score-based recommendations
        if scores.srp_score < 0.6:
            recommendations.append("🔄 Many modules have multiple responsibilities - consider splitting large files")

        if scores.ocp_score < 0.6:
            recommendations.append("🔐 Improve extensibility using abstract base classes and polymorphism")

        if scores.dip_score < 0.6:
            recommendations.append("🔌 Reduce coupling with dependency injection and interface abstractions")

        # Violation-specific recommendations
        for violation in violations[:3]:  # Top 3 violations
            if violation['principle'] == 'SRP' and violation['type'] == 'god_module':
                recommendations.append(f"📋 Split {violation['file']} - it has too many responsibilities")

        return recommendations[:8]  # Limit to 8 recommendations
