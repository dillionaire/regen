"""Module for handling Unicode properties and categories.

This module provides functionality for managing and querying Unicode character properties,
categories, and scripts. It includes support for loading property files, caching data
for performance, and providing various ways to access Unicode character information.
"""

from __future__ import annotations
import re
from typing import Dict, Set, Optional, List, Union, TypeVar, overload, Literal, Iterator, cast
from pathlib import Path
import unicodedata
from functools import lru_cache
from .code_point_set import CodePointSet

PropertyType = Literal['name', 'numeric', 'decimal']
T = TypeVar('T', str, float, CodePointSet)

class UnicodeData:
    """A class for managing Unicode character properties and categories.

    This class provides comprehensive access to Unicode character information,
    including categories, properties, scripts, and numeric values. It supports
    both direct property lookups for individual code points and bulk queries
    for sets of characters sharing specific properties.

    The class implements efficient caching mechanisms to improve performance
    when working with frequently accessed data. It can load and parse Unicode
    property files (like Scripts.txt) and provides various methods to query
    this information.

    Attributes:
        CATEGORIES (dict): Mapping of Unicode category codes to their descriptions.
        MAJOR_CATEGORIES (dict): Mapping of major category codes to their descriptions.
        _category_cache (dict): Cache of category code to CodePointSet mappings.
        _property_cache (dict): Cache of property file data.
        _initialized (bool): Whether the cache has been initialized.
    """

    # Unicode General Categories
    CATEGORIES: Dict[str, str] = {
        'Lu': 'Uppercase Letter',
        'Ll': 'Lowercase Letter',
        'Lt': 'Titlecase Letter',
        'Lm': 'Modifier Letter',
        'Lo': 'Other Letter',
        'Mn': 'Nonspacing Mark',
        'Mc': 'Spacing Mark',
        'Me': 'Enclosing Mark',
        'Nd': 'Decimal Number',
        'Nl': 'Letter Number',
        'No': 'Other Number',
        'Pc': 'Connector Punctuation',
        'Pd': 'Dash Punctuation',
        'Ps': 'Open Punctuation',
        'Pe': 'Close Punctuation',
        'Pi': 'Initial Punctuation',
        'Pf': 'Final Punctuation',
        'Po': 'Other Punctuation',
        'Sm': 'Math Symbol',
        'Sc': 'Currency Symbol',
        'Sk': 'Modifier Symbol',
        'So': 'Other Symbol',
        'Zs': 'Space Separator',
        'Zl': 'Line Separator',
        'Zp': 'Paragraph Separator',
        'Cc': 'Control',
        'Cf': 'Format',
        'Cs': 'Surrogate',
        'Co': 'Private Use',
        'Cn': 'Unassigned'
    }

    # Major Categories (first letter of category)
    MAJOR_CATEGORIES: Dict[str, str] = {
        'L': 'Letter',
        'M': 'Mark',
        'N': 'Number',
        'P': 'Punctuation',
        'S': 'Symbol',
        'Z': 'Separator',
        'C': 'Other'
    }

    def __init__(self) -> None:
        """Initialize the Unicode data manager.

        Creates a new UnicodeData instance with empty caches. The caches are
        lazily initialized when first accessed through any of the query methods.
        This approach helps reduce memory usage when only a subset of the
        Unicode data is needed.
        """
        self._category_cache: Dict[str, CodePointSet] = {}
        self._property_cache: Dict[str, Dict[str, CodePointSet]] = {}
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure the category cache is initialized.

        This method lazily initializes the category cache by scanning the Basic
        Multilingual Plane (BMP) for efficiency. It populates the cache with
        CodePointSets for each Unicode category.

        The initialization is performed only once, when first needed. Subsequent
        calls to this method will have no effect if the cache is already initialized.
        """
        if self._initialized:
            return

        # Initialize category cache
        for category in self.CATEGORIES:
            self._category_cache[category] = CodePointSet()

        # Scan the Basic Multilingual Plane in chunks for better memory usage
        CHUNK_SIZE = 1024
        for start in range(0, 0x10000, CHUNK_SIZE):
            end = min(start + CHUNK_SIZE, 0x10000)
            for code_point in range(start, end):
                try:
                    char = chr(code_point)
                    category = unicodedata.category(char)
                    if category in self._category_cache:
                        self._category_cache[category].add(code_point)
                except ValueError:
                    continue

        self._initialized = True

    @overload
    def get_category(self, value: int) -> str: ...

    @overload
    def get_category(self, value: str) -> CodePointSet: ...

    def get_category(self, value: Union[int, str]) -> Union[str, CodePointSet]:
        """Get either the category of a code point or the code points in a category.

        This method provides dual functionality based on the type of input:
        1. For code points (int): Returns the Unicode category of that code point
        2. For category names (str): Returns all code points in that category

        Args:
            value: Either a Unicode code point (int) or a category name (str).
                  Category names can be either general (e.g., 'Lu') or major
                  categories (e.g., 'L' for all letters).

        Returns:
            - For code points (int): The category string (e.g., 'Lu', 'Nd')
            - For category names (str): A CodePointSet containing all code points
              in that category

        Raises:
            ValueError: If the code point or category is invalid
            TypeError: If value is not an int or str

        Examples:
            >>> unicode_data = UnicodeData()
            >>> unicode_data.get_category(65)  # 'A'
            'Lu'
            >>> 65 in unicode_data.get_category('Lu')  # Check if 'A' is uppercase
            True
        """
        if isinstance(value, int):
            if not 0 <= value <= 0x10FFFF:
                raise ValueError(f"Invalid code point: {value}")
            try:
                return unicodedata.category(chr(value))
            except ValueError:
                raise ValueError(f"No category found for code point: U+{value:04X}")
        elif isinstance(value, str):
            self._ensure_initialized()
            if value in self._category_cache:
                return self._category_cache[value]
            if value in self.MAJOR_CATEGORIES:
                result = CodePointSet()
                for sub_cat in self._category_cache:
                    if sub_cat.startswith(value):
                        result |= self._category_cache[sub_cat]
                return result
            raise ValueError(f"Unknown Unicode category: {value}")
        else:
            raise TypeError("value must be an int or str")

    def get_category_set(self, category: str) -> CodePointSet:
        """Get the set of code points in a Unicode category.

        This is the preferred method for getting code points by category as it
        returns a CodePointSet, which is more efficient for set operations
        and range-based manipulations.

        Args:
            category: The Unicode category (e.g., 'Lu' for uppercase letters)
                     or major category (e.g., 'L' for all letters).

        Returns:
            A CodePointSet containing all code points in the category.

        Raises:
            ValueError: If the category is invalid.

        Examples:
            >>> unicode_data = UnicodeData()
            >>> uppercase = unicode_data.get_category_set('Lu')
            >>> lowercase = unicode_data.get_category_set('Ll')
            >>> letters = uppercase | lowercase  # Union of upper and lowercase
        """
        result = self.get_category(category)
        if not isinstance(result, CodePointSet):
            raise ValueError(f"Invalid category: {category}")
        return result

    @overload
    def get_property(self, prop_file: int, prop_name: PropertyType) -> Union[str, float]: ...

    @overload
    def get_property(self, prop_file: str, prop_name: str) -> CodePointSet: ...

    def get_property(
        self,
        prop_file: Union[int, str],
        prop_name: Union[PropertyType, str]
    ) -> Union[str, float, CodePointSet]:
        """Get a property value or set of code points with a specific Unicode property.

        This method provides dual functionality:
        1. For code points: Retrieves specific properties like name or numeric value
        2. For property files: Returns all code points having a specific property

        Args:
            prop_file: Either:
                - A code point (int) to get its property value
                - A property file name (str) like 'Scripts' to get code points
            prop_name: Either:
                - For code points: property type ('name', 'numeric', 'decimal')
                - For property files: property name (e.g., 'Latin' for Scripts)

        Returns:
            - For code point properties:
                - str: Character name when prop_name is 'name'
                - float: Numeric value when prop_name is 'numeric' or 'decimal'
            - For property files:
                - CodePointSet: Set of code points with the specified property

        Raises:
            ValueError: If property file/name is invalid or property value not found
            TypeError: If arguments have invalid types

        Examples:
            >>> unicode_data = UnicodeData()
            >>> unicode_data.get_property(65, 'name')  # Get name of 'A'
            'LATIN CAPITAL LETTER A'
            >>> unicode_data.get_property('Scripts', 'Latin')  # Get Latin script chars
            <CodePointSet with Latin script characters>
        """
        if isinstance(prop_file, int):
            if not 0 <= prop_file <= 0x10FFFF:
                raise ValueError(f"Invalid code point: {prop_file}")

            char = chr(prop_file)
            if prop_name == 'name':
                try:
                    return unicodedata.name(char)
                except ValueError:
                    raise ValueError(f"No name found for code point: U+{prop_file:04X}")
            elif prop_name in ('numeric', 'decimal'):
                try:
                    value = unicodedata.numeric(char) if prop_name == 'numeric' else unicodedata.decimal(char)
                    return float(value)
                except ValueError:
                    raise ValueError(f"No {prop_name} value for code point: U+{prop_file:04X}")
            else:
                raise ValueError(f"Unsupported property type: {prop_name}. Supported types are: name, numeric, decimal")

        elif isinstance(prop_file, str):
            if prop_file not in self._property_cache:
                self._load_property_file(prop_file)
            if prop_file not in self._property_cache:
                raise ValueError(f"Unknown property file: {prop_file}")
            if prop_name not in self._property_cache[prop_file]:
                raise ValueError(f"Unknown property value '{prop_name}' in {prop_file}")
            return self._property_cache[prop_file][prop_name]
        else:
            raise TypeError("prop_file must be an int or str")

    @lru_cache(maxsize=8)  # Cache recently accessed property files
    def _load_property_file(self, prop_file: str) -> None:
        """Load and parse a Unicode property file.

        This method loads and parses a Unicode property file (e.g., Scripts.txt,
        Blocks.txt) from the data directory. The file format should follow the
        standard Unicode property file format:

        Format:
            code_point_range; property_value # Comment
            Examples:
            0041..005A; Latin  # Basic Latin uppercase
            0061..007A; Latin  # Basic Latin lowercase

        Args:
            prop_file: Name of the property file to load (e.g., 'Scripts')

        Raises:
            ValueError: If the property file cannot be found or is invalid.
            FileNotFoundError: If the property file does not exist.
        """
        if prop_file in self._property_cache:
            return

        self._property_cache[prop_file] = {}
        data_dir = Path(__file__).parent / 'data'
        file_path = data_dir / f'{prop_file}.txt'

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    try:
                        range_str, value = line.split(';', 1)
                        value = value.split('#')[0].strip()

                        if '..' in range_str:
                            start, end = map(lambda x: int(x, 16), range_str.split('..'))
                        else:
                            start = end = int(range_str, 16)

                        if value not in self._property_cache[prop_file]:
                            self._property_cache[prop_file][value] = CodePointSet()
                        self._property_cache[prop_file][value].add_range(start, end)

                    except (ValueError, IndexError) as e:
                        raise ValueError(f"Invalid line in {prop_file}.txt: {line}") from e

        except FileNotFoundError:
            raise FileNotFoundError(f"Property file not found: {file_path}")

    def get_all_properties(self, prop_file: str) -> List[str]:
        """Get all available property values from a property file.

        This method returns a list of all property values defined in a specific
        property file (e.g., all script names from Scripts.txt).

        Args:
            prop_file: The name of the property file (e.g., 'Scripts', 'Blocks')

        Returns:
            A list of all property values defined in the file.

        Raises:
            ValueError: If the property file is invalid or not found.

        Examples:
            >>> unicode_data = UnicodeData()
            >>> scripts = unicode_data.get_all_properties('Scripts')
            >>> 'Latin' in scripts
            True
        """
        if prop_file not in self._property_cache:
            self._load_property_file(prop_file)
        return sorted(self._property_cache[prop_file].keys())

    def get_script(self, code_point: int) -> Optional[str]:
        """Get the script name for a Unicode code point.

        This method returns the script name (e.g., 'Latin', 'Greek', 'Cyrillic')
        for a given Unicode code point.

        Args:
            code_point: The Unicode code point to look up.

        Returns:
            The script name, or None if the code point has no assigned script.

        Raises:
            ValueError: If the code point is invalid.

        Examples:
            >>> unicode_data = UnicodeData()
            >>> unicode_data.get_script(65)  # 'A'
            'Latin'
            >>> unicode_data.get_script(0x0391)  # 'Α'
            'Greek'
        """
        if not 0 <= code_point <= 0x10FFFF:
            raise ValueError(f"Invalid code point: {code_point}")

        if 'Scripts' not in self._property_cache:
            self._load_property_file('Scripts')

        for script, code_points in self._property_cache['Scripts'].items():
            if code_point in code_points:
                return script

        return None

    def iter_code_points(self, category: str) -> Iterator[int]:
        """Iterate over code points in a category efficiently.

        This method provides memory-efficient iteration over code points
        in a category without creating intermediate sets.

        Args:
            category: The Unicode category to iterate over.

        Yields:
            Code points in the specified category.

        Examples:
            >>> unicode_data = UnicodeData()
            >>> for cp in unicode_data.iter_code_points('Lu'):
            ...     print(f"U+{cp:04X}")
        """
        result = self.get_category(category)
        if not isinstance(result, CodePointSet):
            raise ValueError(f"Invalid category: {category}")
        yield from result