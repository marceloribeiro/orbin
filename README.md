# Orbin

A collection of helpful utilities and helpers for Python development.

## Installation

### From PyPI (Recommended)

```bash
pip install orbin
```

### From Local Development (For Development)

If you want to install the package locally for development purposes:

1. Clone or download this repository
2. Navigate to the project directory
3. Install in development mode:

```bash
# Navigate to the project directory
cd /path/to/orbin

# Install in development/editable mode
pip install -e .

# Or install with development dependencies
pip install -e .[dev]
```

The `-e` flag installs the package in "editable" mode, which means changes to the source code will be immediately reflected without needing to reinstall the package.

## Usage

### Hello World Helper

The package includes a simple hello world helper with several functions:

```python
# Import the functions
from orbin import hello_world, hello_world_with_name, get_hello_world_message

# Basic hello world - prints to console
hello_world()
# Output: hello world

# Personalized greeting - prints to console
hello_world_with_name("Alice")
# Output: hello Alice

hello_world_with_name()  # Uses default "World"
# Output: hello World

# Get the message as a string instead of printing
message = get_hello_world_message()
print(f"Message: {message}")
# Output: Message: hello world
```

### Alternative Import Style

You can also import from the helpers module directly:

```python
from orbin.helpers import hello_world, hello_world_with_name, get_hello_world_message

# Or import the entire helpers module
from orbin import helpers

helpers.hello_world()
helpers.hello_world_with_name("Bob")
```

### Import the Entire Module

```python
import orbin

orbin.hello_world()
orbin.hello_world_with_name("Charlie")
message = orbin.get_hello_world_message()
```

## Development

### Setting up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/orbin.git
cd orbin
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode with development dependencies:
```bash
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black orbin/
```

### Type Checking

```bash
mypy orbin/
```

## Requirements

- Python 3.7 or higher

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### 0.1.0 (2025-08-24)
- Initial release
- Added hello world helper functions
- Basic package structure
