from __future__ import annotations

import json
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception

from .errors import DPDHTTPError, DPDDecodeError


Retryable = (httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError, httpx.PoolTimeout)


def _is_retryable_exception(exc: BaseException) -> bool:
    if isinstance(exc, Retryable):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or 500 <= status < 600
    return False


class HTTPClient:
    """Internal HTTP helper wrapping httpx with retries and defaults."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 15.0,
        max_retries: int = 3,
        user_agent: str | None = None,
        headers: dict[str, str] | None = None,
        cache_ttl: float | int | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)
        self._cache_ttl = float(cache_ttl) if cache_ttl else 0.0
        self._cache: dict[str, tuple[float, Any]] = {}
        default_headers = {"Accept": "application/json"}
        if user_agent:
            default_headers["User-Agent"] = user_agent
        if headers:
            default_headers.update(headers)
        self._client.headers.update(default_headers)

    def close(self) -> None:
        self._client.close()

    def _request(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        @retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential_jitter(initial=0.5, max=4),
            retry=retry_if_exception(_is_retryable_exception),
            reraise=True,
        )
        def _do() -> httpx.Response:
            resp = self._client.get(url, params=params)
            if resp.status_code == 429 or 500 <= resp.status_code < 600:
                # surface as HTTPStatusError to trigger retry predicate
                try:
                    resp.raise_for_status()
                except httpx.HTTPStatusError as exc:  # pragma: no cover - re-raised by tenacity
                    raise exc
            return resp

        try:
            return _do()
        except httpx.HTTPStatusError as exc:
            raise DPDHTTPError(exc.response.status_code, exc.response.text, url=str(exc.request.url)) from exc
        except httpx.HTTPError as exc:
            raise DPDHTTPError(-1, str(exc)) from exc

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        key = _cache_key(url, params)
        if self._cache_ttl:
            hit = self._cache.get(key)
            if hit and hit[0] >= _now():
                return hit[1]
        resp = self._request(url, params=params)
        if 400 <= resp.status_code < 500:
            req_url = str(resp.request.url) if getattr(resp, "request", None) else None
            raise DPDHTTPError(resp.status_code, resp.text, url=req_url)
        try:
            data = resp.json()
            if self._cache_ttl:
                self._cache[key] = (_now() + self._cache_ttl, data)
            return data
        except json.JSONDecodeError as exc:  # pragma: no cover
            raise DPDDecodeError("Failed to decode JSON response") from exc


class AsyncHTTPClient:
    """Async variant of the HTTP helper."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 15.0,
        max_retries: int = 3,
        user_agent: str | None = None,
        headers: dict[str, str] | None = None,
        cache_ttl: float | int | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)
        self._cache_ttl = float(cache_ttl) if cache_ttl else 0.0
        self._cache: dict[str, tuple[float, Any]] = {}
        default_headers = {"Accept": "application/json"}
        if user_agent:
            default_headers["User-Agent"] = user_agent
        if headers:
            default_headers.update(headers)
        self._client.headers.update(default_headers)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _request(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        # Manual retry loop for async to avoid tenacity's async overhead.
        attempts = 0
        last_exc: BaseException | None = None
        while attempts < self.max_retries:
            try:
                resp = await self._client.get(url, params=params)
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    resp.raise_for_status()
                return resp
            except (
                httpx.ConnectError,
                httpx.ReadError,
                httpx.RemoteProtocolError,
                httpx.PoolTimeout,
                httpx.HTTPStatusError,
            ) as exc:
                last_exc = exc
                attempts += 1
                # exponential backoff with jitter
                sleep_for = min(4.0, (2 ** (attempts - 1)) + (0.1 * attempts))
                await _async_sleep(sleep_for)
        # exhausted retries
        assert last_exc is not None
        if isinstance(last_exc, httpx.HTTPStatusError):
            raise DPDHTTPError(last_exc.response.status_code, last_exc.response.text, url=str(last_exc.request.url)) from last_exc
        raise DPDHTTPError(-1, str(last_exc)) from last_exc

    async def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        key = _cache_key(url, params)
        if self._cache_ttl:
            hit = self._cache.get(key)
            if hit and hit[0] >= _now():
                return hit[1]
        resp = await self._request(url, params=params)
        if 400 <= resp.status_code < 500:
            req_url = str(resp.request.url) if getattr(resp, "request", None) else None
            raise DPDHTTPError(resp.status_code, resp.text, url=req_url)
        try:
            data = resp.json()
            if self._cache_ttl:
                self._cache[key] = (_now() + self._cache_ttl, data)
            return data
        except json.JSONDecodeError as exc:  # pragma: no cover
            raise DPDDecodeError("Failed to decode JSON response") from exc


async def _async_sleep(seconds: float) -> None:
    # simple local sleep to avoid bringing in asyncio in the module API
    import asyncio

    await asyncio.sleep(seconds)


def _cache_key(url: str, params: dict[str, Any] | None) -> str:
    if not params:
        return url
    parts = [f"{k}={params[k]}" for k in sorted(params.keys())]
    return f"{url}?{'&'.join(parts)}"


def _now() -> float:
    import time

    return time.time()
