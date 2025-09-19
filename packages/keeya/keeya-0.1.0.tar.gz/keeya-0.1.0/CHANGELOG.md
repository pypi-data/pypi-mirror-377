# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-09-18

### Added
- Initial release of Keeya
- AI-powered Python code generation using OpenRouter API
- Smart model selection based on task complexity
- Support for multiple free AI models:
  - GPT-OSS-20B (fast)
  - Qwen 2.5 Coder 32B (balanced)
  - Qwen3 Coder (powerful)
- Clean code output without markdown formatting
- Comprehensive error handling and validation
- Jupyter notebook support
- Extensive documentation and examples

### Features
- `keeya.generate()` - Generate Python code from natural language
- `keeya.clean()` - AI-powered data cleaning (planned)
- `keeya.analyze()` - AI-powered data analysis (planned)
- `keeya.visualize()` - AI-powered visualization (planned)
- `keeya.train()` - AI-powered ML training (planned)
- `keeya.get_available_models()` - List available AI models

### Technical Details
- Python 3.8+ support
- OpenRouter API integration
- Free model support
- Production-ready code generation
- Type hints and documentation
- MIT License
