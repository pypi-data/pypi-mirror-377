# Contributing to Video Transcription Agent

Thank you for your interest in contributing to the Video Transcription Agent! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- FFmpeg installed on your system
- Git for version control
- Basic understanding of Python and AI/ML concepts

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/video-transcription-agent.git
   cd video-transcription-agent
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Install Development Dependencies**
   ```bash
   pip install -r requirements-dev.txt  # If available
   # Or install manually:
   pip install pytest black flake8 mypy pre-commit
   ```

## 🛠️ Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/urgent-fix` - Critical fixes

### Making Changes

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run tests
   pytest tests/
   
   # Run linting
   flake8 src/
   
   # Run type checking
   mypy src/
   
   # Format code
   black src/
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Code Style Guidelines

### Python Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use meaningful variable and function names

### Example Code Style

```python
from typing import Dict, Any, Optional
import asyncio

class ExampleAgent:
    """Example agent demonstrating code style guidelines."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the agent with configuration.
        
        Args:
            config: Configuration dictionary containing agent settings
        """
        self.config = config
        self.status = "initialized"
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main functionality.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Dictionary containing execution results
            
        Raises:
            ValueError: If input_data is invalid
        """
        if not input_data:
            raise ValueError("input_data cannot be empty")
        
        # Implementation here
        return {"status": "success", "result": "processed"}
```

### Documentation Style

- Use clear, concise language
- Include examples for complex functionality
- Update README.md for user-facing changes
- Update CHANGELOG.md for significant changes

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/     # Integration tests for workflows
├── fixtures/        # Test data and fixtures
└── conftest.py     # Pytest configuration
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch
from src.agents.transcriber_agent import TranscriberAgent

class TestTranscriberAgent:
    """Test cases for TranscriberAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        config = {"model_size": "base"}
        agent = TranscriberAgent(config)
        assert agent.model_size == "base"
    
    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful execution."""
        config = {"model_size": "base"}
        agent = TranscriberAgent(config)
        
        with patch.object(agent, 'model') as mock_model:
            mock_model.transcribe.return_value = {
                "text": "test transcription",
                "language": "en"
            }
            
            result = await agent.execute({"audio_path": "test.wav"})
            assert result["status"] == "success"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_transcriber_agent.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v
```

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (if applicable)
- [ ] No merge conflicts with main branch

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues
2. Try the latest version
3. Check documentation
4. Test with minimal example

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 13.0]
- Python: [e.g., 3.11.0]
- Package version: [e.g., 1.1.1]

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

### Before Requesting

1. Check existing feature requests
2. Consider if it fits project scope
3. Provide clear use case

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches you've considered

## Additional Context
Any other relevant information
```

## 🏷️ Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] Tag created
- [ ] Release notes written
- [ ] PyPI package built and uploaded

## 📞 Getting Help

- 📧 Email: contact@lopand.com
- 🐛 Issues: [GitHub Issues](https://github.com/lopand-solutions/video-transcription-agent/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/lopand-solutions/video-transcription-agent/discussions)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Video Transcription Agent!** 🎬🚀
