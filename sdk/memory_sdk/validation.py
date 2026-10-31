"""Runtime validation shared by Python entry points and the JSON bridge."""


def validate_identifier(value: str, name: str = "user_id") -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must not be blank")
    return value


def validate_limit(limit: int) -> int:
    if type(limit) is not int:
        raise TypeError("limit must be an integer")
    if limit < 1:
        raise ValueError("limit must be at least 1")
    return limit
