# Levox - Production-Grade PII/GDPR Detection CLI

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Levox is a high-performance, enterprise-grade CLI application for detecting Personally Identifiable Information (PII) and ensuring GDPR compliance in codebases. Built with a multi-tier detection architecture, it provides fast, accurate scanning with minimal false positives.

## 🚀 Features

- **7-Stage Detection Pipeline**: Regex → AST Analysis → Context Analysis → Dataflow → CFG Analysis → ML Filtering → GDPR Compliance
- **Multi-Language Support**: Python, JavaScript, and extensible parser architecture
- **Performance Optimized**: <10s incremental scans, <30s full repository scans
- **Enterprise Licensing**: Standard, Premium, and Enterprise tiers with feature gates
- **Low False Positives**: Target <10% false positive rate
- **Memory Efficient**: Memory-mapped file operations for large codebases
- **Comprehensive Logging**: Structured logging with performance metrics

## 🏗️ Architecture

```
levox/
├── levox/
│   ├── cli.py                 # Main CLI entry point
│   ├── core/
│   │   ├── engine.py          # Detection engine orchestrator
│   │   ├── config.py          # Configuration management
│   │   └── exceptions.py      # Custom exceptions
│   ├── detection/
│   │   ├── regex_engine.py    # Stage 1: Optimized regex detection
│   │   ├── ast_analyzer.py    # Stage 2: AST-based context analysis
│   │   ├── context_analyzer.py # Stage 3: Semantic context analysis
│   │   ├── dataflow.py        # Stage 4: Taint/dataflow analysis
│   │   ├── cfg_analyzer.py    # Stage 5: Control Flow Graph analysis
│   │   └── ml_filter.py       # Stage 6: ML-based false positive reduction
│   ├── parsers/
│   │   ├── base.py           # Base parser interface
│   │   ├── python_parser.py  # Python AST parser
│   │   ├── javascript_parser.py # JS parser
│   │   └── multi_lang.py     # Multi-language coordinator
│   ├── utils/
│   │   ├── file_handler.py   # Memory-mapped file operations
│   │   ├── validators.py     # Luhn, format validators
│   │   └── performance.py    # Performance monitoring
│   └── models/
│       ├── detection_result.py # Result data models
│       └── confidence.py       # Confidence scoring
```

## 📦 Installation

### From Source

```bash
git clone https://github.com/levox/levox.git
cd levox
pip install -e .
```

### From PyPI

```bash
pip install levox
```

### From PyPI (Development Version)

```bash
pip install --upgrade levox
```

## 🚀 Quick Start

### Basic Usage

```bash
# Scan current directory
levox scan

# Scan specific directory
levox scan /path/to/codebase

# Scan with CFG analysis (Premium+)
levox scan --cfg

# Generate detailed report
levox scan --output report.json --format json

# Configure detection rules
levox configure --rules custom-rules.yaml
```

### Advanced CFG Analysis

```bash
# Enable deep scanning with CFG analysis
levox scan --cfg --cfg-confidence 0.7

# Alternative flag name
levox scan --deep-scan

# Full enterprise scan with all stages
levox scan --license-tier enterprise --cfg --format json
```

### CLI Commands

- `levox scan` - Scan codebase for PII/GDPR violations
- `levox configure` - Configure detection rules and settings
- `levox report` - Generate and view reports
- `levox feedback` - Provide feedback to improve detection

## ⚙️ Configuration

### Detection Pipeline Stages

**STAGE 1: Regex Detection (Basic)**
- Fast pattern matching for basic PII patterns
- Optimized regex engine with minimal false positives

**STAGE 2: AST Analysis (Premium+)**
- Abstract syntax tree parsing for code structure
- Multi-language support with Tree-sitter

**STAGE 3: Context Analysis (Premium+)**
- Semantic analysis of variable/function names
- Context-aware false positive reduction

**STAGE 4: Dataflow Analysis (Enterprise)**
- Tracks data movement through code
- Taint analysis for sensitive data flows

**STAGE 5: CFG Analysis (Premium+)**
- Control Flow Graph analysis for complex PII flows
- Detects conditional exposure, loop accumulation, transformation chains

**STAGE 6: ML Filtering (Enterprise)**
- Machine learning false positive reduction
- Confidence scoring and validation

**STAGE 7: GDPR Compliance (Premium+)**
- Regulatory compliance checking
- Audit logging and reporting

### License Tiers

- **Standard**: Basic regex detection, limited language support
- **Premium**: AST analysis, context analysis, CFG analysis, GDPR compliance
- **Enterprise**: Full 7-stage pipeline including dataflow and ML filtering

### Detection Rules

Create custom detection rules in `configs/rules.yaml`:

```yaml
patterns:
  credit_card:
    regex: '\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    confidence: 0.8
    risk_level: high
    
  email:
    regex: '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    confidence: 0.9
    risk_level: medium
```

## 🔍 Detection Pipeline

### Level 1: Regex Engine
- High-performance pattern matching
- Optimized for common PII formats
- Fast initial screening

### Level 2: AST Analysis
- Context-aware detection
- Variable name analysis
- Comment and string extraction

### Level 3: Dataflow Analysis
- Taint tracking
- Variable propagation
- Cross-function analysis

### Level 4: ML Filtering
- False positive reduction
- Context classification
- Confidence scoring

## 📊 Performance

- **Incremental Scans**: <10 seconds for modified files
- **Full Repository**: <30 seconds for 10,000 files
- **Memory Usage**: <500MB for large codebases
- **False Positive Rate**: Target <10%

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=levox

# Run specific test suite
pytest tests/test_detection/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.levox.ai](https://docs.levox.ai)
- **Issues**: [GitHub Issues](https://github.com/levox/levox/issues)
- **Discussions**: [GitHub Discussions](https://github.com/levox/levox/discussions)

## 🏆 Enterprise Support

For enterprise customers, we offer:
- Custom detection rules
- API integration
- Dedicated support
- Training and consulting

Contact us at enterprise@levox.ai for more information.
