# Privacy Prompt Library - Python Package

A privacy-preserving prompt transformation library that redacts disability mentions while maintaining functional context for AI interactions.

## Installation

### From PyPI (when published)
```bash
pip install privacy-prompt-library
```

### Development Installation
```bash
git clone https://github.com/git-markkuria/kanuni-layer-sdk.git
cd kanuni-layer-sdk
pip install -e .
```

## Quick Start

### Python API
```python
from prompt_library import transform_prompt, get_library_info

# Get library information
info = get_library_info()
print(f"Library version: {info['version']}")

# Transform a prompt
result = transform_prompt("I am paralyzed and need help with accessibility.")
print(f"Original: {result['input']}")
print(f"Transformed: {result['output']}")
```

### Command Line Interface
```bash
# Get library info
privacy-prompt --info

# Transform a prompt
privacy-prompt "I am paralyzed and need help with accessibility."

# Transform with options
privacy-prompt --privacy-level medium --no-context "I have ADHD and need focus strategies."

# Output as JSON
privacy-prompt --output-format json "I am blind and need screen reader compatible solutions."
```

## Features

- **Medical Term Redaction**: Automatically removes medical diagnoses and disability-specific terms
- **Functional Context Addition**: Adds appropriate accessibility context to maintain prompt effectiveness  
- **Privacy Preservation**: Ensures no personal health information is disclosed
- **Intent Maintenance**: Preserves the original intent and functionality of prompts
- **Batch Processing**: Process multiple prompts efficiently
- **Async Support**: Full async/await support for modern applications

## API Reference

### Main Functions

#### `transform_prompt(prompt, options=None)`
Transform a single prompt with privacy protection.

**Parameters:**
- `prompt` (str): The input prompt to transform
- `options` (dict, optional): Transformation options
  - `privacy_level` (str): "low", "medium", or "high" (default: "high")
  - `add_context` (bool): Whether to add functional context (default: True)

**Returns:**
- `dict`: Transformation result with input, output, and metadata

#### `transform_batch(prompts, options=None)`
Transform multiple prompts efficiently.

**Parameters:**
- `prompts` (list): List of input prompts
- `options` (dict, optional): Same as `transform_prompt`

**Returns:**
- `list`: List of transformation results

#### `get_library_info()`
Get information about the library capabilities.

**Returns:**
- `dict`: Library version, features, and capabilities

### Classes

#### `PromptLibrary`
Main library class with async support.

```python
from prompt_library import PromptLibrary

library = PromptLibrary()
await library.initialize()
result = await library.transform_prompt("Your prompt here")
```

## Development

### Building the Package

1. **Install build tools:**
   ```bash
   pip install build twine
   ```

2. **Build the package:**
   ```bash
   python -m build
   ```

3. **Check the built package:**
   ```bash
   twine check dist/*
   ```

### Publishing to PyPI

1. **Test on TestPyPI first:**
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. **Publish to PyPI:**
   ```bash
   twine upload dist/*
   ```

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black prompt_library/

# Sort imports  
isort prompt_library/

# Type checking
mypy prompt_library/

# Linting
flake8 prompt_library/
```

## Package Structure

```
prompt_library/
├── __init__.py           # Main package exports
├── main.py              # Core PromptLibrary class
├── cli.py               # Command line interface
├── core/                # Core processing modules
│   ├── __init__.py
│   ├── pipeline.py      # Transformation pipeline
│   ├── detector.py      # Privacy term detection
│   └── redactor.py      # Term redaction engine
├── engines/             # Processing engines
│   ├── __init__.py
│   └── context/         # Context addition engine
│       ├── __init__.py
│       └── context_engine.py
└── data/                # Data files (JSON)
    ├── patterns.json
    ├── redaction-rules.json
    └── context-library.json
```

## Configuration Files

- `pyproject.toml`: Modern Python packaging configuration
- `requirements.txt`: Development dependencies
- `MANIFEST.in`: Include non-Python files in package
- `LICENSE`: MIT license
- `README.md`: Package documentation

## Dependencies

### Runtime Dependencies
- `aiofiles>=23.0.0`: Async file operations
- `pydantic>=2.0.0`: Data validation
- `typing-extensions>=4.0.0`: Type hints support

### Development Dependencies
- `pytest>=7.0.0`: Testing framework
- `pytest-asyncio>=0.21.0`: Async testing support
- `black>=23.0.0`: Code formatting
- `isort>=5.12.0`: Import sorting
- `flake8>=6.0.0`: Linting
- `mypy>=1.0.0`: Type checking

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: https://github.com/git-markkuria/kanuni-layer-sdk/issues
- Documentation: https://github.com/git-markkuria/kanuni-layer-sdk#readme