"""Exceptions for pyutilitati_md library."""


class UtilitatiMDError(Exception):
    """Base exception for pyutilitati_md."""


class UtilitatiMDAuthError(UtilitatiMDError):
    """Exception raised when provider authentication fails."""


class UtilitatiMDConnectionError(UtilitatiMDError):
    """Exception raised when network connection to provider fails."""


class UtilitatiMDApiError(UtilitatiMDError):
    """Exception raised when provider API returns invalid or malformed data."""
