# Privacy Prompt Library - Quick Reference

## 🐍 Python Version (Recommended)

### Installation
```bash
pip install privacy-prompt-library
```

### Basic Usage
```python
from prompt_library import transform_prompt, get_library_info

# Transform a prompt
result = transform_prompt("I'm paralyzed and need accessibility help")
print(result['output'])

# Get library info
info = get_library_info()
print(f"Version: {info['version']}")
```

### CLI Usage
```bash
# Transform via command line
privacy-prompt "I have ADHD and need focus strategies"

# Get info
privacy-prompt --info

# Custom options
privacy-prompt --privacy-level medium --output-format json "Your prompt"
```

### Async Usage
```python
from prompt_library import PromptLibrary

library = PromptLibrary()
await library.initialize()
result = await library.transform_prompt("I'm autistic and need help")
```

## 📦 Package Information

- **PyPI Package**: `privacy-prompt-library`
- **Import Name**: `prompt_library`
- **CLI Command**: `privacy-prompt`
- **GitHub**: https://github.com/git-markkuria/kanuni-layer-sdk
- **TestPyPI**: https://test.pypi.org/project/privacy-prompt-library/

## 🚀 Node.js/JavaScript Version

### Usage
```javascript
import { transformPrompt } from './src/index.js';

const result = await transformPrompt("I'm blind and need coding help");
console.log(result.transformed);
```

### Running
```bash
npm install
npm start
```

## 🔄 Migration Guide

**JavaScript → Python**

```javascript
// JavaScript
import { transformPrompt } from './src/index.js';
const result = await transformPrompt(prompt);
```

```python
# Python
from prompt_library import transform_prompt
result = transform_prompt(prompt)
```

## 🛠️ Development

### Python Development
```bash
git clone https://github.com/git-markkuria/kanuni-layer-sdk.git
cd kanuni-layer-sdk
pip install -e .
pytest tests/
```

### Building & Publishing
```bash
python -m build
twine upload --repository testpypi dist/*
twine upload dist/*
```