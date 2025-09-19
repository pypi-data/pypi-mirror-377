# Contributing to Keeya

Thank you for your interest in contributing to Keeya! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- OpenRouter API key (for testing)

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/yourusername/keeya.git
   cd keeya
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Set up your API key:**
   ```bash
   export OPENROUTER_API_KEY="your_key_here"
   ```

## Making Changes

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Add docstrings for all public functions
- Keep functions focused and single-purpose

### Testing
- Write tests for new features
- Ensure all existing tests pass
- Test with multiple Python versions (3.8+)

### Documentation
- Update README.md for user-facing changes
- Add docstrings for new functions
- Update examples if needed

## Submitting Changes

### Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit:**
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```

3. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request:**
   - Use the PR template
   - Describe your changes clearly
   - Link any related issues

### Commit Message Format
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove)
- Keep the first line under 50 characters

## Development Guidelines

### Adding New Features
- Keep the API simple and intuitive
- Add comprehensive tests
- Update documentation
- Consider backward compatibility

### Bug Reports
- Use the issue template
- Provide steps to reproduce
- Include error messages and stack traces
- Specify Python version and OS

### Feature Requests
- Use the issue template
- Describe the use case
- Explain the expected behavior
- Consider implementation complexity

## Code Review Process

- All PRs require review before merging
- Address review comments promptly
- Keep PRs focused and reasonably sized
- Ensure CI tests pass

## Release Process

- Version numbers follow semantic versioning
- Releases are created from the main branch
- Changelog is updated for each release
- PyPI publishing is automated via GitHub Actions

## Questions?

- Open an issue for questions
- Check existing issues first
- Be respectful and constructive

Thank you for contributing to Keeya! 🚀
