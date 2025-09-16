"""Helper functions."""


def snake_to_pascal(v: str) -> str:
    """
    Convert string from snake_case to PascalCase.

    Args:
        v: snake_case string

    Returns:
        PascalCase string.
    """

    return "".join(word.title() for word in v.split("_"))
