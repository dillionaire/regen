# Regen

A Python library for generating optimized regular expressions with Unicode support and pattern optimization.

## Features

- Optimized regex pattern generation
- Unicode support via CodePointSet
- Pattern composition and optimization strategies
- Comprehensive example coverage
- Performance-focused design

## Installation

```bash
pip install regen
```

## Quick Start

```python
from regen import RegexGenerator

# Create a generator instance
gen = RegexGenerator()

# Generate an optimized pattern for matching version numbers
pattern = gen.create_optimized_pattern([
    "v1.2.3",
    "v1.2.4",
    "v1.2.5"
])
# Result: 'v1\.2\.[345]'

# Create an alternation pattern
pattern = gen.create_alternation([
    "file.txt",
    "file.pdf"
])
# Result: '(?:file\.txt|file\.pdf)'
```

## Documentation

For detailed documentation and examples, please visit our [documentation](https://github.com/dillionaire/regen/wiki).

### Basic Usage

```python
from regen import RegexGenerator

gen = RegexGenerator()

# Simple pattern optimization
pattern = gen.create_optimized_pattern([
    "2024_Launch",
    "2025_Launch"
])
# Result: '202[45]_Launch'

# Pattern with special characters
pattern = gen.create_alternation([
    "test.txt",
    "test.pdf"
])
# Result: '(?:test\.txt|test\.pdf)'
```

## Development

### Prerequisites

- Python 3.8+
- pip or uv for package management

### Setup

1. Clone the repository:

```bash
git clone https://github.com/dillionaire/regen.git
cd regen
```

2. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

3. Run tests:

```bash
pytest
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Status

Current version: 0.1.0

This project is under active development. See our [Project Plan](PLAN.md) and [Task List](TASK.md) for current status and upcoming features.
