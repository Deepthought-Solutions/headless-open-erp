"""Report DTOs - HTTP request models."""

from pydantic import BaseModel


class ReportRequest(BaseModel):
    """Report creation request."""
    altcha: str
    visitorId: str
    page: str
