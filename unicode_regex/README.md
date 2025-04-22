# Unicode Regex Generator

A Python library for handling Unicode properties and categories, with efficient caching and set operations.

## UnicodeData Class

The `UnicodeData` class provides a comprehensive interface for working with Unicode properties and categories. It includes efficient caching mechanisms and supports various Unicode operations.

### Features

- Unicode category management (letters, numbers, symbols, etc.)
- Property file handling
- Character numeric value retrieval
- Unicode name lookups
- Efficient caching of code point sets

### Installation

```bash
pip install unicode-regex
```

### Usage

```python
from unicode_regex import UnicodeData

# Initialize the Unicode data manager
ud = UnicodeData()

# Get all uppercase letters
uppercase = ud.get_category('Lu')
print('A' in uppercase)  # True
print('a' in uppercase)  # False

# Get all letters (combines Lu, Ll, Lt, Lm, Lo)
all_letters = ud.get_category('L')
print('A' in all_letters)  # True
print('a' in all_letters)  # True
print('1' in all_letters)  # False

# Get numeric value of a character
print(ud.get_numeric_value('1'))  # 1.0
print(ud.get_numeric_value('½'))  # 0.5
print(ud.get_numeric_value('A'))  # None

# Get Unicode name of a character
print(ud.get_name('A'))  # 'LATIN CAPITAL LETTER A'
print(ud.get_name('1'))  # 'DIGIT ONE'
```

### Unicode Categories

The class supports all standard Unicode categories:

- Letters (L)
  - Lu: Uppercase Letter
  - Ll: Lowercase Letter
  - Lt: Titlecase Letter
  - Lm: Modifier Letter
  - Lo: Other Letter
- Marks (M)
  - Mn: Nonspacing Mark
  - Mc: Spacing Mark
  - Me: Enclosing Mark
- Numbers (N)
  - Nd: Decimal Number
  - Nl: Letter Number
  - No: Other Number
- Punctuation (P)
  - Pc: Connector Punctuation
  - Pd: Dash Punctuation
  - Ps: Open Punctuation
  - Pe: Close Punctuation
  - Pi: Initial Punctuation
  - Pf: Final Punctuation
  - Po: Other Punctuation
- Symbols (S)
  - Sm: Math Symbol
  - Sc: Currency Symbol
  - Sk: Modifier Symbol
  - So: Other Symbol
- Separators (Z)
  - Zs: Space Separator
  - Zl: Line Separator
  - Zp: Paragraph Separator
- Other (C)
  - Cc: Control
  - Cf: Format
  - Cs: Surrogate
  - Co: Private Use
  - Cn: Unassigned

### Property Files

The class can load and handle Unicode property files:

```python
# Get all properties from a specific property file
scripts = ud.get_all_properties('Scripts')
print(scripts)  # ['Latin', 'Greek', 'Cyrillic', ...]

# Get code points for a specific property
latin_chars = ud.get_property('Scripts', 'Latin')
```

### Performance Considerations

- The class uses lazy initialization to avoid unnecessary processing
- Code points are cached for efficient repeated access
- The Basic Multilingual Plane (BMP) is pre-scanned for better performance
- Property files are loaded only when needed

### Testing

The package includes comprehensive tests. To run them:

```bash
pytest unicode_regex/tests/
```

### Contributing

Contributions are welcome! Please ensure:

1. All tests pass
2. New features include tests
3. Documentation is updated
4. Code follows the project's style guide

### License

MIT License - See LICENSE file for details