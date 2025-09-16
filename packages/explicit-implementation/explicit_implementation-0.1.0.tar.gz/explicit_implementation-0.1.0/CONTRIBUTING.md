# Contributing to Explicit Implementation

Thank you for your interest in contributing to Explicit Implementation! We welcome contributions from everyone.

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/explicit-implementation.git
   cd explicit-implementation
   ```

2. **Set up Development Environment**
   ```bash
   # Install uv if you haven't already
   pip install uv
   
   # Create virtual environment and install dependencies
   uv sync --dev
   ```

3. **Run Tests**
   ```bash
   uv run pytest tests/ -v
   ```

## Development Workflow

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write your code
   - Add tests for new functionality
   - Update documentation if needed

3. **Run Quality Checks**
   ```bash
   # Format code
   uv run black src/ tests/
   uv run isort src/ tests/
   
   # Run linting
   uv run flake8 src/ tests/
   
   # Run type checking
   uv run mypy src/
   
   # Run tests
   uv run pytest tests/ -v --cov=src/explicit_implementation
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## Code Style

- We use [Black](https://black.readthedocs.io/) for code formatting
- We use [isort](https://isort.readthedocs.io/) for import sorting
- We use [flake8](https://flake8.pycqa.org/) for linting
- We use [mypy](https://mypy.readthedocs.io/) for type checking

## Testing Guidelines

- All new features must include tests
- Aim for high test coverage
- Test both success and failure cases
- Use descriptive test names
- Group related tests in classes

Example test structure:
```python
class TestNewFeature:
    """Test the new feature functionality."""
    
    def test_basic_usage(self):
        """Test that basic usage works as expected."""
        # Test implementation
        
    def test_error_handling(self):
        """Test that errors are handled correctly."""
        # Test implementation
```

## Documentation

- Update docstrings for new/modified functions
- Update README.md if adding user-facing features
- Add examples for new functionality
- Keep documentation clear and concise

## Submitting Changes

### Pull Request Guidelines

- **Title**: Use a clear, descriptive title
- **Description**: Explain what changes you made and why
- **Testing**: Describe how you tested your changes
- **Breaking Changes**: Highlight any breaking changes

### What to Include

- [ ] Tests for new functionality
- [ ] Documentation updates
- [ ] Type hints for new code
- [ ] Changelog entry (if significant change)

### Review Process

1. Automated checks must pass (CI/CD)
2. Code review by maintainers
3. Address any feedback
4. Merge when approved

## Bug Reports

When reporting bugs, please include:

- Python version
- Package version
- Minimal code example that reproduces the issue
- Expected vs actual behavior
- Error messages/tracebacks

## Feature Requests

When requesting features:

- Explain the use case
- Provide examples of how it would be used
- Consider backwards compatibility
- Be open to alternative solutions

## Questions?

- Open an issue for questions about the codebase
- Check existing issues and documentation first
- Be specific about what you're trying to achieve

## Code of Conduct

Please be respectful and constructive in all interactions. We want to maintain a welcoming environment for all contributors.

Thank you for contributing! 🎉