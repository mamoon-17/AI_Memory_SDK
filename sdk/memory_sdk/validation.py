"""Runtime validation shared by Python entry points and the JSON bridge."""


def validate_limit(limit: int) -> int:
    if type(limit) is not int:
        raise TypeError("limit must be an integer")
    if limit < 1:
        raise ValueError("limit must be at least 1")
    return limit
