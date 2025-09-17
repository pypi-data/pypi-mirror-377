from __future__ import annotations


class DPDError(Exception):
    """Base exception for DPD client."""


class DPDHTTPError(DPDError):
    """HTTP error returned by the DPD API."""

    def __init__(self, status_code: int, message: str = "", *, url: str | None = None):
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.url = url


class DPDDecodeError(DPDError):
    """Raised when the response body cannot be decoded as expected JSON."""


class DPDInvalidParam(DPDError):
    """Raised when invalid parameters are provided to a client method."""
