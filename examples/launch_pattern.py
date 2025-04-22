from regen import RegexGenerator, CodePointSet

def create_launch_pattern():
    """Generate a regex pattern for matching launch-related commands."""
    gen = RegexGenerator()

    # Define common launch words
    launch_words = [
        "launch", "start", "begin", "initiate", "execute",
        "run", "deploy", "trigger", "activate"
    ]

    # Create alternation pattern for launch words
    launch_pattern = gen.create_alternation(launch_words)

    # Add optional whitespace and target
    pattern = (
        f"^{launch_pattern}"  # Start with launch word
        r"\s+"  # Required whitespace
        r"([A-Za-z0-9_-]+)"  # Target name
        r"(?:\s+--?\w+)*$"  # Optional flags
    )

    return pattern

def test_launch_pattern():
    """Test the generated launch pattern with various inputs."""
    pattern = create_launch_pattern()
    test_cases = [
        "launch app-server",
        "start test_suite --verbose",
        "execute backup -daily",
        "deploy webapp --prod -v",
        "initiate batch_job",
        # Invalid cases
        "invalid command",
        "launch",  # Missing target
        "launch app server",  # Extra word
    ]

    import re
    regex = re.compile(pattern)

    print("Testing launch pattern:", pattern)
    print("\nTest Results:")
    for test in test_cases:
        match = regex.match(test)
        result = "✓" if match else "✗"
        target = match.group(1) if match else None
        print(f"{result} {test:<30} Target: {target}")

if __name__ == "__main__":
    test_launch_pattern()