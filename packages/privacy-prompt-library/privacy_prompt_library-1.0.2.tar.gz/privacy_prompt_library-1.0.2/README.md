# Privacy-Preserving Prompt Library

A comprehensive Python library that transforms user prompts to protect disability privacy while maintaining functional context for AI interactions.

## 🎯 Purpose

This library helps users interact with AI models without disclosing specific medical conditions by:
- **Detecting** disability mentions in prompts
- **Redacting** medical/diagnostic terms
- **Adding** functional context for better AI responses
- **Preserving** user privacy and intent

## 🔄 How It Works

```
Input: "I'm paralyzed and need help finding accessible restaurants"
↓
Output: "I use mobility equipment and need help finding accessible restaurants. I need step-free access to buildings and accessible parking close to entrances."
```

## 🏗️ Architecture

- **14 Disability Categories** with comprehensive subgroups
- **Pattern Detection Engine** for identifying disability mentions
- **Redaction Engine** for replacing medical terms
- **Context Enrichment** for adding functional needs
- **Privacy Validation** to ensure no medical data leaks

## � Installation

```bash
pip install privacy-prompt-library
```

## �🚀 Quick Start

### Python API
```python
from prompt_library import transform_prompt

# Transform a single prompt
result = transform_prompt("I'm blind and need coding help")
print(result['output'])
# "I use screen readers and need coding help. Please ensure any visual content includes text descriptions and is compatible with screen readers."

# Get library information
from prompt_library import get_library_info
info = get_library_info()
print(f"Library version: {info['version']}")
```

### Command Line Interface
```bash
# Transform a prompt via CLI
privacy-prompt "I have ADHD and need focus strategies"

# Get library information
privacy-prompt --info

# Custom privacy level
privacy-prompt --privacy-level medium "Your prompt here"
```

### Async Support
```python
from prompt_library import PromptLibrary

library = PromptLibrary()
await library.initialize()
result = await library.transform_prompt("I'm autistic and need help with social situations")
print(result['output'])
```

## 📋 Categories Supported

1. Physical Disabilities
2. Visual Impairments  
3. Hearing Impairments
4. Speech & Language
5. Intellectual Disabilities
6. Learning Disabilities
7. Autism Spectrum
8. Developmental Disabilities
9. Mental Health
10. Emotional & Behavioral
11. Invisible Disabilities
12. Multiple Disabilities
13. Neurological
14. Genetic & Rare Disorders

## 🔒 Privacy Guarantee

- ✅ No medical terms in output
- ✅ No diagnostic language
- ✅ Functional descriptions only
- ✅ Complete user anonymity

## 🐍 Python Package Features

This repository now includes a fully-featured Python package with:

- **Modern Packaging**: Uses `pyproject.toml` and is available on PyPI
- **Async Support**: Full async/await compatibility
- **CLI Tool**: Command-line interface for easy integration
- **Type Hints**: Complete typing for better development experience
- **Testing**: Comprehensive test suite with pytest

### Python Installation & Usage

```bash
# Install from PyPI
pip install privacy-prompt-library

# Basic usage
python -c "from prompt_library import transform_prompt; print(transform_prompt('I have autism and need help'))"

# CLI usage
privacy-prompt --info
privacy-prompt "I'm deaf and need communication help"
```

### Development Setup

```bash
# Clone repository
git clone https://github.com/git-markkuria/kanuni-layer-sdk.git
cd kanuni-layer-sdk

# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

## 📁 Repository Structure

```
├── prompt_library/          # Python package
│   ├── core/               # Core processing engines
│   ├── engines/            # Context and redaction engines
│   ├── data/               # JSON data files
│   └── cli.py              # Command-line interface
├── src/                    # JavaScript/Node.js version
├── tests/                  # Python tests
├── pyproject.toml          # Python packaging config
└── package.json            # Node.js config
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.