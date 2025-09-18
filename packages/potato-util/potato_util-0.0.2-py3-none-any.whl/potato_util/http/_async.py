import aiohttp
from pydantic import validate_call, AnyHttpUrl


@validate_call
async def async_is_connectable(
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
        async with aiohttp.ClientSession() as _session:
            async with _session.get(str(url), timeout=timeout) as _response:
                if check_status:
                    return _response.status == 200
                return True
    except Exception:
        return False


__all__ = [
    "async_is_connectable",
]
