REQUEST_ID_REGEX = (
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b|"
    r"\b[0-9a-fA-F]{32}\b"
)

# Invalid characters:
SPECIAL_CHARS_REGEX = r"[&'\"<>]"
SPECIAL_CHARS_BASE_REGEX = r"[&'\"<>\\\/]"
SPECIAL_CHARS_LOW_REGEX = r"[&'\"<>\\\/`{}|]"
SPECIAL_CHARS_MEDIUM_REGEX = r"[&'\"<>\\\/`{}|()\[\]]"
SPECIAL_CHARS_HIGH_REGEX = r"[&'\"<>\\\/`{}|()\[\]!@#$%^*;:?]"
SPECIAL_CHARS_STRICT_REGEX = r"[&'\"<>\\\/`{}|()\[\]~!@#$%^*_=\-+;:,.?\t\n ]"


__all__ = [
    "REQUEST_ID_REGEX",
    "SPECIAL_CHARS_REGEX",
    "SPECIAL_CHARS_BASE_REGEX",
    "SPECIAL_CHARS_LOW_REGEX",
    "SPECIAL_CHARS_MEDIUM_REGEX",
    "SPECIAL_CHARS_HIGH_REGEX",
    "SPECIAL_CHARS_STRICT_REGEX",
]
