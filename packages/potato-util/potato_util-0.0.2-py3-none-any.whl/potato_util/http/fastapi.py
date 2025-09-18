from pydantic import validate_call
from starlette.datastructures import URL
from fastapi import Request


@validate_call(config={"arbitrary_types_allowed": True})
def get_relative_url(val: Request | URL) -> str:
    """Get relative url only path with query params from request object or URL object.

    Args:
        val (Union[Request, URL]): Request object or URL object to extract relative url.

    Returns:
        str: Relative url only path with query params.
    """

    if isinstance(val, Request):
        val = val.url

    _relative_url = str(val).replace(f"{val.scheme}://{val.netloc}", "")
    return _relative_url


__all__ = [
    "get_relative_url",
]
