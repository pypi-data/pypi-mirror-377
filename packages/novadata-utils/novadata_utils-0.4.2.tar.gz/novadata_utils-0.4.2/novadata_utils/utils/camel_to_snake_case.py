import re


def camel_to_snake_case(string):
    """Convert a camel case string to snake case."""
    string = re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()
    return string
