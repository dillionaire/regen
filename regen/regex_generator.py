from typing import List, Sequence, Union
import re

class RegexGenerator:
    """
    A class for generating optimized regular expression patterns.

    The RegexGenerator provides methods to create regex patterns with automatic
    optimization for common cases like numeric sequences and alternations.

    Attributes:
        _pattern (str): Internal storage for the current pattern

    Examples:
        >>> gen = RegexGenerator()
        >>> gen.create_optimized_pattern(["2024_Launch", "2025_Launch"])
        '202[45]_Launch'
        >>> gen.create_alternation(["foo", "bar"])
        '(?:foo|bar)'
    """

    def __init__(self):
        """Initialize a new RegexGenerator instance."""
        self._pattern = ""

    def create_alternation(self, patterns: Sequence[str]) -> str:
        """
        Create a regex pattern that matches any of the given patterns.

        This method creates an optimized alternation pattern that matches any
        of the provided strings. It automatically handles escaping of special
        regex characters.

        Args:
            patterns: A sequence of strings to match

        Returns:
            str: A regex pattern that matches any of the input patterns

        Examples:
            >>> gen = RegexGenerator()
            >>> gen.create_alternation(["file.txt", "file.pdf"])
            '(?:file\\.txt|file\\.pdf)'
        """
        if not patterns:
            return ""
        if len(patterns) == 1:
            return re.escape(patterns[0])
        return "(?:" + "|".join(map(re.escape, patterns)) + ")"

    def create_optimized_pattern(self, strings: Sequence[str]) -> str:
        """
        Create an optimized regex pattern that matches any of the given strings.

        This method analyzes the input strings to detect patterns and creates
        an optimized regex that matches any of them. It's particularly effective
        for strings that differ only in numeric portions.

        The optimization process:
        1. Finds common prefixes and suffixes
        2. Identifies positions where strings differ only in numeric values
        3. Creates character classes for numeric differences
        4. Falls back to alternation if optimization isn't possible

        Args:
            strings: A sequence of strings to match

        Returns:
            str: An optimized regex pattern that matches any of the input strings

        Examples:
            >>> gen = RegexGenerator()
            >>> gen.create_optimized_pattern(["2024_Launch", "2025_Launch"])
            '202[45]_Launch'
            >>> gen.create_optimized_pattern(["v1.2.3", "v1.2.4"])
            'v1\\.2\\.[34]'
        """
        if not strings:
            return ""
        if len(strings) == 1:
            return re.escape(strings[0])

        # Find common prefix and suffix
        first = strings[0]
        prefix = first
        for s in strings[1:]:
            while not s.startswith(prefix):
                prefix = prefix[:-1]
                if not prefix:
                    break

        if prefix:
            suffixes = [s[len(prefix):] for s in strings]
            if all(len(s) == len(suffixes[0]) for s in suffixes):
                # Check if differences are only numeric
                numeric_positions = []
                for i in range(len(suffixes[0])):
                    chars = {s[i] for s in suffixes}
                    if all(c.isdigit() for c in chars):
                        numeric_positions.append((i, sorted(chars)))

                if numeric_positions:
                    result = re.escape(prefix)
                    pos = 0
                    for i, chars in numeric_positions:
                        if i > pos:
                            result += re.escape(suffixes[0][pos:i])
                        result += f"[{''.join(chars)}]"
                        pos = i + 1
                    if pos < len(suffixes[0]):
                        result += re.escape(suffixes[0][pos:])
                    return result

        # Fall back to alternation if optimization not possible
        return self.create_alternation(strings)

    def escape(self, pattern: str) -> str:
        """
        Escape special regex characters in the pattern.

        Args:
            pattern: The string pattern to escape

        Returns:
            str: The escaped pattern safe for regex use

        Examples:
            >>> gen = RegexGenerator()
            >>> gen.escape("file.txt")
            'file\\.txt'
        """
        return re.escape(pattern)