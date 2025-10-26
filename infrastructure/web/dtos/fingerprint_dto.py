"""Fingerprint DTOs - HTTP request models."""

from pydantic import BaseModel


class FingerprintRequest(BaseModel):
    """Fingerprint creation request."""
    altcha: str
    visitorId: str
    components: dict
