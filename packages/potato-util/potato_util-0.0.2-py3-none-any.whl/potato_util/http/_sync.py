from urllib import request
from http.client import HTTPResponse

from pydantic import validate_call, AnyHttpUrl


@validate_call
def is_connectable(
    url: AnyHttpUrl = AnyHttpUrl("https://www.google.com"),
    timeout: int = 3,
    check_status: bool = False,
) -> bool:
    """Check if the url is connectable.

    Args:
        url          (AnyHttpUrl, optional): URL to check. Defaults to 'https://www.google.com'.
        timeout      (int       , optional): Timeout in seconds. Defaults to 3.
        check_status (bool      , optional): Check HTTP status code (200). Defaults to False.

    Raise:
        ValueError: If `timeout` is less than 1.

    Returns:
        bool: True if connectable, False otherwise.
    """

    if timeout < 1:
        raise ValueError(
            f"`timeout` argument value {timeout} is invalid, must be greater than 0!"
        )

    try:
        _response: HTTPResponse = request.urlopen(
            str(url), timeout=timeout
        )  # nosec B310
        if check_status:
            return _response.getcode() == 200
        return True
    except Exception:
        return False


__all__ = [
    "is_connectable",
]
