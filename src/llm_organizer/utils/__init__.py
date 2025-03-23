"""Utility functions for the LLM Directory Organizer."""

import re


def format_naming_scheme(text: str, scheme: str) -> str:
    """
    Format text according to the specified naming scheme.

    Args:
        text: The text to format
        scheme: The naming scheme (snake_case, camel_case, pascal_case, title_case, lower_case)

    Returns:
        Formatted text
    """
    # First normalize the string: replace non-alphanumeric with spaces and lowercase
    normalized = re.sub(r"[^a-zA-Z0-9]", " ", text).lower()
    words = normalized.split()

    if not words:
        return ""

    if scheme == "snake_case":
        return "_".join(words)

    elif scheme == "camel_case":
        return words[0] + "".join(word.capitalize() for word in words[1:])

    elif scheme == "pascal_case":
        return "".join(word.capitalize() for word in words)

    elif scheme == "title_case":
        return " ".join(word.capitalize() for word in words)

    elif scheme == "lower_case":
        return " ".join(words)

    # Default to snake_case if scheme not recognized
    return "_".join(words)
