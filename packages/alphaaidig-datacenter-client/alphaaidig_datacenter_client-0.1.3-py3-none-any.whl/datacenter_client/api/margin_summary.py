from __future__ import annotations
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..base import BaseClient


class MarginSummaryClient:
    """Client for Margin Summary related endpoints."""
    def __init__(self, client: "BaseClient"):
        self._client = client

    def page_list(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        exchange_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Get a paginated list of margin market summaries.
        Corresponds to GET /margin_summary/page_list
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if exchange_id:
            params["exchange_id"] = exchange_id
        
        return self._client._request("GET", "/api/v1/margin_summary/page_list", params=params)