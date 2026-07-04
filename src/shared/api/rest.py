"""Async HTTP client with retry logic"""

from typing import Any, Literal, assert_never

import httpx
from tenacity import retry, retry_if_exception, stop_after_delay, wait_exponential

from src.shared.constants import RETRYABLE_HTTP_ERROR_CODES


def is_retryable_http_error_code(code: int) -> bool:
    return code in RETRYABLE_HTTP_ERROR_CODES


def is_retryable_http_error(error: BaseException):
    if not isinstance(error, httpx.HTTPStatusError):
        return False

    return is_retryable_http_error_code(error.response.status_code)


@retry(
    retry=retry_if_exception(is_retryable_http_error),
    wait=wait_exponential(min=0.25, multiplier=1, max=10),
    stop=stop_after_delay(30),
)
async def make_http_call(
    *,
    url: str,
    method: Literal["GET", "POST"],
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    timeout: int = 10,
) -> httpx.Response:
    """
    Wrapper around httpx client for async HTTP calls to centralize retry logic
    """

    async with httpx.AsyncClient() as client:
        match method:
            case "GET":
                resp = await client.get(url, params=params, timeout=timeout)

            case "POST":
                resp = await client.post(url, params=params, json=json, timeout=timeout)

            case _ as unreachable:
                assert_never(unreachable)

        resp.raise_for_status()
        return resp
