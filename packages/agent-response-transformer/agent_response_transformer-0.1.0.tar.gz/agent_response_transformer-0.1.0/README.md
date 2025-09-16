# Agent Response Transformer

A Python SDK to transform Claude response to OpenAI response format.

## Installation

Install the package via pip:

```bash
pip install agent-response-transformer
```

## Usage

```python
from agent_response_transformer import ResponseTransformer

# Create an instance of the transformer
transformer = ResponseTransformer()

# Transform Claude response to OpenAI format
result = transformer.claude_json_to_openai_response(claude_response)
```

## Features

- Transform Claude response format to OpenAI response format
- Support for text content and function calls
- Proper handling of tool usage and results

## Development

To install the package in development mode:

```bash
pip install -e .
```

## Dependencies

The package has no direct dependencies. However, when using this package in your projects, you may need to install:

- openai
- agents (if it's a separate package)

For development, you can install all dependencies using:

```bash
pip install -r requirements.txt
```

## Publishing to PyPI

To publish a new version to PyPI:

1. Update the version in `setup.py`
2. Build the package:
   ```bash
   python setup.py sdist bdist_wheel
   ```
3. Upload to Test PyPI first:
   ```bash
   twine upload --repository testpypi dist/*
   ```
4. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

## License

MIT
