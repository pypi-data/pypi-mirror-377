# 🔍 SOLID Checker - Smart SOLID Analysis Tool

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive, intelligent Python tool for analyzing code compliance with SOLID principles, featuring **adaptive contextual analysis** that adjusts evaluation criteria based on project type and complexity.

## 🌟 Key Features

### 🧠 Smart Contextual Analysis
- **Automatic Project Type Detection**: Identifies whether your code is a simple script, utility module, library, or large application
- **Adaptive Scoring**: Adjusts SOLID principle weights based on project characteristics
- **Context-Aware Thresholds**: Different quality expectations for different project types
- **Intelligent Recommendations**: Tailored advice that prevents over-engineering simple code while demanding excellence from libraries

### 📊 Comprehensive SOLID Analysis
- **SRP (Single Responsibility Principle)**: Analyzes class responsibilities and method focus
- **OCP (Open/Closed Principle)**: Detects extensibility violations and type checking patterns
- **LSP (Liskov Substitution Principle)**: Validates inheritance hierarchies and contracts
- **ISP (Interface Segregation Principle)**: Identifies interface bloat and segregation issues
- **DIP (Dependency Inversion Principle)**: Finds tight coupling and dependency issues

### 🎯 Advanced Scoring System
- **Weighted Scoring**: Different emphasis on principles based on project needs
- **Complexity Analysis**: Evaluates project size, class count, and architectural complexity
- **Color-Coded Results**: Visual indicators with adaptive thresholds
- **Detailed Violation Reports**: Specific issues with actionable insights

### 📈 Multiple Output Formats
- **Interactive Reports**: Rich console output with emoji indicators and detailed breakdowns
- **JSON Export**: Machine-readable format for CI/CD integration and further analysis
- **Detailed Analysis**: In-depth violation analysis with specific recommendations

## 🚀 Quick Start

### Installation

```bash
# Basic installation (recommended for end users)
pip install solid-checker

# Installation with development tools (for contributors)
pip install solid-checker[dev]
```

**Note:** The `[dev]` option includes additional tools like `ruff` (linting/formatting) and `mypy` (type checking) that are useful for development but not required for using the tool.

### Basic Usage

```bash
# Smart analysis (default) - automatically adapts to your project type
python solid-checker your_file.py

# Detailed report with violation breakdown
python solid-checker --report your_file.py

# JSON output for integration with other tools
python solid-checker --json your_file.py > analysis.json

# Legacy analysis (classic SOLID scoring without adaptation)
python solid-checker --legacy your_file.py
```

## 🧠 Smart Analysis in Action

The tool automatically adapts its analysis based on your project characteristics:

### Simple Scripts (< 100 lines, 1-2 classes)
```
🧠 Smart Analysis:
   📋 Project Type: Simple Script
   📊 Complexity Score: 0.0/1.00
   
⚖️ Adaptive Weights:
   📋 SRP: 40.0% | 🔓 OCP: 10.0% | 🔄 LSP: 10.0%
   🎯 ISP: 10.0% | 🔄 DIP: 30.0%
```
**Focus**: Simplicity and single purpose. Lenient thresholds to avoid over-engineering.

### Libraries/Frameworks
```
🧠 Smart Analysis:
   📋 Project Type: Library Framework
   📊 Complexity Score: 0.7/1.00
   
⚖️ Adaptive Weights:
   📋 SRP: 20.0% | 🔓 OCP: 30.0% | 🔄 LSP: 20.0%
   🎯 ISP: 25.0% | 🔄 DIP: 5.0%
```
**Focus**: Extensibility (OCP) and clean interfaces (ISP). Strict thresholds for public APIs.

### Large Applications
```
🧠 Smart Analysis:
   📋 Project Type: Large Application
   📊 Complexity Score: 0.8/1.00
   
⚖️ Adaptive Weights:
   📋 SRP: 30.0% | 🔓 OCP: 25.0% | 🔄 LSP: 20.0%
   🎯 ISP: 15.0% | 🔄 DIP: 10.0%
```
**Focus**: Maintainability (SRP) and extensibility (OCP). Strict compliance for long-term success.

## 📋 CLI Options

| Option | Description |
|--------|-------------|
| `file` | Python file to analyze |
| `--report` | Show detailed violation analysis |
| `--json` | Output results in JSON format |
| `--verbose` | Enable verbose error output |
| `--smart` | Use smart contextual analysis (default) |
| `--legacy` | Use classic analysis without adaptation |
| `--no-smart-info` | Hide smart analysis information in report |

## 📊 Understanding the Output

### Smart Analysis Section
```
🧠 Smart Analysis:
   📋 Project Type: Small App
   📊 Complexity Score: 0.30/1.00
   📈 Lines of Code: 589
   🏗️ Classes: 8

⚖️ Adaptive Weights (for this project type):
   📋 SRP: 25.0% | 🔓 OCP: 20.0% | 🔄 LSP: 20.0%
   🎯 ISP: 15.0% | 🔄 DIP: 20.0%
```

### SOLID Scores
```
📊 SOLID Scores (with context-aware thresholds):
   📋 SRP: 0.62/1.00 🟡
   🔓 OCP: 0.50/1.00 🔴
   🔄 LSP: 1.00/1.00 🟢
   🎯 ISP: 1.00/1.00 🟢
   🔄 DIP: 0.57/1.00 🔴
```

**Color Indicators**:
- 🟢 **Green**: Excellent compliance (above "good" threshold)
- 🟡 **Yellow**: Acceptable compliance (above "acceptable" threshold)  
- 🔴 **Red**: Needs improvement (below "acceptable" threshold)

*Note: Thresholds adapt based on project type*

## 🎯 Project Types & Adaptive Behavior

### 1. Simple Script
- **Characteristics**: < 100 lines, 1-2 classes
- **Focus**: Single purpose, avoid over-engineering
- **Thresholds**: Lenient (Good: 0.6, Acceptable: 0.4)
- **Weight Emphasis**: SRP (40%), DIP (30%)

### 2. Utility Module  
- **Characteristics**: 100-500 lines, few classes
- **Focus**: Balance simplicity with reusability
- **Thresholds**: Standard (Good: 0.8, Acceptable: 0.6)
- **Weight Emphasis**: Balanced approach

### 3. Small Application
- **Characteristics**: 500-1500 lines, moderate complexity
- **Focus**: Standard SOLID compliance
- **Thresholds**: Standard (Good: 0.8, Acceptable: 0.6)
- **Weight Emphasis**: Equal weighting

### 4. Large Application
- **Characteristics**: 1500+ lines, many classes
- **Focus**: Maintainability and structure
- **Thresholds**: Standard (Good: 0.8, Acceptable: 0.6)
- **Weight Emphasis**: SRP (30%), OCP (25%)

### 5. Library/Framework
- **Characteristics**: Public APIs, reusable components
- **Focus**: Extensibility and interface design
- **Thresholds**: Strict (Good: 0.9, Acceptable: 0.7)
- **Weight Emphasis**: OCP (30%), ISP (25%)

## 🛠️ Architecture

The tool follows a clean, modular architecture adhering to SOLID principles:

```
solid-checker/
├── __main__.py               # Main entry point
├── solid_scorer.py           # Main smart analysis engine
├── srp/                      # Single Responsibility Principle analyzer
│   ├── __init__.py
│   ├── core.py              # Core SRP analysis logic
│   ├── facade.py            # Simple API facade
│   └── protocols.py         # Type protocols and interfaces
├── ocp/                      # Open/Closed Principle analyzer
├── lsp/                      # Liskov Substitution Principle analyzer  
├── isp/                      # Interface Segregation Principle analyzer
├── dip/                      # Dependency Inversion Principle analyzer
└── README.md                # This documentation
```

### Key Components

#### ProjectComplexityAnalyzer
Analyzes project characteristics to determine appropriate SOLID standards:
- Lines of code counting
- Class and method analysis
- Inheritance depth calculation
- External dependency tracking

#### AdaptiveWeightCalculator
Calculates context-aware weights and thresholds:
- Project type-based weight adjustment
- Quality threshold adaptation
- Complex project stricter requirements

#### ContextualRecommendationGenerator
Generates smart, targeted recommendations:
- Project type-specific advice
- Context-appropriate violation analysis
- Prevents over-engineering warnings

#### SOLIDScorer
Enhanced scorer with adaptive capabilities:
- Smart recommendation generation
- Contextual summary creation
- Weighted scoring with project awareness

## 📈 Example Analyses

### Simple Python Script
```python
#!/usr/bin/env python3
def main():
    name = input("Enter your name: ")
    print(f"Hello, {name}!")

if __name__ == "__main__":
    main()
```

**Analysis Result**:
```
🧠 Smart Analysis:
   📋 Project Type: Simple Script
   📊 Complexity Score: 0.0/1.00

🎯 Overall SOLID Score: 1.00/1.00
📋 Summary: Perfect script organization! 🎯

💡 Smart Recommendations:
   ✅ Excellent! Your script follows good practices while staying simple
   💡 Insight: This level of organization is perfect for scripts
```

## 🔧 Integration & CI/CD

### JSON Output for Automation
```bash
python __main__.py --json my_code.py
```

Sample JSON output:
```json
{
  "file_path": "my_code.py",
  "scores": {
    "srp_score": 0.85,
    "ocp_score": 0.75,
    "lsp_score": 1.0,
    "isp_score": 0.9,
    "dip_score": 0.65,
    "overall_score": 0.83
  },
  "summary": "Great SOLID architecture! 🌟",
  "smart_analysis": {
    "project_type": "small_app",
    "complexity_score": 0.4,
    "lines_of_code": 350,
    "class_count": 5,
    "adaptive_weights": {
      "srp": 0.25,
      "ocp": 0.2,
      "lsp": 0.2,
      "isp": 0.15,
      "dip": 0.2
    }
  }
}
```

### GitHub Actions Integration
```yaml
name: SOLID Analysis
on: [push, pull_request]
jobs:
  solid-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.13
    - name: Run SOLID Analysis
      run: |
        python __main__.py --json src/main.py > solid_report.json
        # Add custom logic to parse results and set exit codes
```

## 🎓 Educational Value

This tool serves as both a practical analysis instrument and an educational resource:

1. **Learn SOLID Principles**: Understand how each principle applies in real code
2. **Contextual Understanding**: See how requirements change based on project type
3. **Practical Application**: Get actionable advice rather than abstract theory
4. **Progressive Improvement**: Track improvements over time with consistent metrics

## 🏆 Why This Tool is Different

Unlike traditional static analysis tools that apply rigid rules uniformly, SOLID Checker understands that **context matters**:

- **No More Over-Engineering Warnings** for simple scripts that don't need complex architecture
- **Stricter Standards** for libraries and frameworks where quality is paramount  
- **Balanced Approach** for typical applications with practical recommendations
- **Educational Feedback** that helps developers understand *why* certain principles matter more in different contexts

**Result**: More practical, actionable, and contextually appropriate SOLID analysis that helps you write better code without unnecessary complexity.

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- **New Project Type Detection**: Additional heuristics for specialized domains
- **Language Support**: Extend analysis to other programming languages  
- **Custom Rules**: User-defined weighting and threshold configurations
- **IDE Integration**: Plugins for popular development environments
- **Continuous Monitoring**: Integration with code quality dashboards

## 📜 License

MIT License - feel free to use, modify, and distribute.

---

*Built with ❤️ for developers who care about code quality and practical software architecture.*
