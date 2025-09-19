"""
Custom exception types for Reducto document extraction client.

These exceptions are intended to be consumed by higher layers (e.g. server)
to map to platform-friendly error types without relying on broad base
exceptions.
"""

from __future__ import annotations


class ExtractionClientError(Exception):
    """Base error for document-extraction client."""


class UploadError(ExtractionClientError):
    """Base error for upload-related failures."""


class UploadForbiddenError(UploadError):
    """Authentication/authorization failure when requesting upload."""


class UploadPresignRequestError(UploadError):
    """Failure during the presign request to obtain the upload URL."""

    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class UploadMissingPresignedUrlError(UploadError):
    """Presign response did not include a presigned URL."""


class UploadMissingFileIdError(UploadError):
    """Presign response did not include a file ID."""


class UploadPutError(UploadError):
    """Failure when uploading content to the presigned URL."""

    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class ExtractError(ExtractionClientError):
    """Base error for extract-related failures."""


class ExtractFailedError(ExtractError):
    """Failure when extracting content from the document."""

    def __init__(self, message: str, *, reason: str | None = None):
        super().__init__(message)
        self.reason = reason
