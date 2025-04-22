"""Performance benchmarks for unicode-regex operations."""

import pytest
import random
import string
from unicode_regex.unicode_data import UnicodeData
from unicode_regex.code_point_set import CodePointSet
from unicode_regex.regex_generator import RegexGenerator
from unicode_regex.optimizer import Optimizer


@pytest.fixture(scope="module")
def ud():
    """Create a UnicodeData instance for benchmarks."""
    return UnicodeData()


@pytest.fixture(scope="module")
def generator():
    """Create a RegexGenerator instance for benchmarks."""
    return RegexGenerator()


@pytest.fixture(scope="module")
def optimizer():
    """Create an Optimizer instance for benchmarks."""
    return Optimizer()


def generate_random_text(size, scripts=None):
    """Generate random Unicode text for benchmarking."""
    if not scripts:
        # Default to Basic Latin for predictable testing
        return ''.join(random.choices(string.ascii_letters + string.digits, k=size))

    # Generate text using specified scripts
    chars = []
    for _ in range(size):
        script = random.choice(scripts)
        code_point = random.choice(list(script))
        chars.append(chr(code_point))
    return ''.join(chars)


class TestPropertyLookupPerformance:
    """Benchmark property lookup operations."""

    def test_category_lookup_performance(self, benchmark, ud):
        """Benchmark category lookup performance."""
        def lookup_categories():
            categories = ['Lu', 'Ll', 'Nd', 'P', 'S']
            results = []
            for cat in categories:
                results.append(ud.get_category(cat))
            return results

        benchmark(lookup_categories)

    def test_script_lookup_performance(self, benchmark, ud):
        """Benchmark script property lookup performance."""
        def lookup_scripts():
            scripts = ['Latin', 'Greek', 'Cyrillic', 'Arabic']
            results = []
            for script in scripts:
                results.append(ud.get_property('Script', script))
            return results

        benchmark(lookup_scripts)

    def test_numeric_property_lookup_performance(self, benchmark, ud):
        """Benchmark numeric property lookup performance."""
        def lookup_numeric():
            # Test range of code points with numeric properties
            results = []
            for cp in range(0x30, 0x40):  # ASCII digits and some symbols
                try:
                    results.append(ud.get_property(cp, 'numeric'))
                except ValueError:
                    continue
            return results

        benchmark(lookup_numeric)


class TestPatternGenerationPerformance:
    """Benchmark pattern generation operations."""

    @pytest.mark.parametrize("size", [10, 100, 1000])
    def test_pattern_generation_scaling(self, benchmark, generator, ud, size):
        """Benchmark pattern generation with different set sizes."""
        def generate_large_pattern():
            # Create a large set of code points
            code_points = set(range(0x0000, size))
            pattern_set = CodePointSet(code_points)
            return generator.generate_pattern(pattern_set)

        benchmark(generate_large_pattern)

    def test_complex_pattern_generation(self, benchmark, generator, ud):
        """Benchmark generation of complex patterns with multiple properties."""
        def generate_complex_pattern():
            # Combine multiple properties
            latin = ud.get_property('Script', 'Latin')
            greek = ud.get_property('Script', 'Greek')
            digits = ud.get_category('Nd')
            combined = (latin | greek) & ~digits
            return generator.generate_pattern(combined)

        benchmark(generate_complex_pattern)


class TestPatternMatchingPerformance:
    """Benchmark pattern matching performance."""

    @pytest.mark.parametrize("text_size", [100, 1000, 10000])
    def test_pattern_matching_scaling(self, benchmark, generator, ud, text_size):
        """Benchmark pattern matching with different text sizes."""
        # Generate test pattern and text
        latin = ud.get_property('Script', 'Latin')
        pattern = generator.generate_pattern(latin)
        text = generate_random_text(text_size)

        def match_pattern():
            import re
            regex = re.compile(pattern)
            return [m.span() for m in regex.finditer(text)]

        benchmark(match_pattern)

    def test_multilingual_pattern_matching(self, benchmark, generator, ud):
        """Benchmark matching patterns with multiple scripts."""
        # Get multiple scripts
        latin = ud.get_property('Script', 'Latin')
        greek = ud.get_property('Script', 'Greek')
        cyrillic = ud.get_property('Script', 'Cyrillic')

        # Generate mixed script text
        text = generate_random_text(1000, [latin, greek, cyrillic])
        pattern = generator.generate_pattern(latin | greek | cyrillic)

        def match_multilingual():
            import re
            regex = re.compile(pattern)
            return [m.span() for m in regex.finditer(text)]

        benchmark(match_multilingual)


class TestOptimizationPerformance:
    """Benchmark pattern optimization operations."""

    @pytest.mark.parametrize("complexity", ["simple", "medium", "complex"])
    def test_optimization_scaling(self, benchmark, optimizer, complexity):
        """Benchmark optimization performance with different pattern complexities."""
        patterns = {
            "simple": r"[a-zA-Z0-9]+",
            "medium": r"[a-z]+|[A-Z]+|[0-9]+|[\u0370-\u03FF]+",
            "complex": r"(?:[a-zA-Z][\u0370-\u03FF])+|[\u0400-\u04FF]{2,4}|[0-9]+(?:\.[0-9]+)?"
        }
        pattern = patterns[complexity]

        def optimize_pattern():
            return optimizer.optimize(pattern)

        benchmark(optimize_pattern)

    def test_range_compression_performance(self, benchmark, optimizer):
        """Benchmark range compression performance."""
        # Create a pattern with many ranges
        ranges = []
        for i in range(0, 1000, 2):
            ranges.append(f"\\u{i:04x}-\\u{i+1:04x}")
        pattern = f"[{''.join(ranges)}]"

        def compress_ranges():
            return optimizer.compress_ranges(pattern)

        benchmark(compress_ranges)


class TestMemoryUsage:
    """Benchmark memory usage of various operations."""

    def test_property_cache_memory(self, benchmark, ud):
        """Benchmark memory usage of property caching."""
        def cache_properties():
            # Access various properties to test cache behavior
            scripts = ['Latin', 'Greek', 'Cyrillic', 'Arabic', 'Han']
            categories = ['Lu', 'Ll', 'Nd', 'P', 'S']

            for script in scripts:
                ud.get_property('Script', script)
            for cat in categories:
                ud.get_category(cat)

        benchmark(cache_properties)

    @pytest.mark.parametrize("set_size", [1000, 10000, 100000])
    def test_code_point_set_memory(self, benchmark, set_size):
        """Benchmark memory usage of CodePointSet operations."""
        def create_and_operate_sets():
            # Create and operate on large sets
            set1 = CodePointSet(set(range(0, set_size, 2)))
            set2 = CodePointSet(set(range(1, set_size, 2)))
            return set1 | set2, set1 & set2, set1 - set2

        benchmark(create_and_operate_sets)