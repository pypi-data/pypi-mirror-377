from __future__ import annotations
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..base import BaseClient


class AStockClient:
    """Client for A-Stock related endpoints."""
    def __init__(self, client: "BaseClient"):
        self._client = client

    def list(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        exchange: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a paginated list of A-stocks.
        Corresponds to GET /a-stock/
        """
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if search:
            params["search"] = search
        if exchange:
            params["exchange"] = exchange
        
        return self._client._request("GET", "/a-stock/", params=params)

    def get(self, stock_code: str) -> Dict[str, Any]:
        """
        Get details for a specific A-stock by its code.
        Corresponds to GET /a-stock/{stock_code}
        """
        return self._client._request("GET", f"/a-stock/{stock_code}")

    def summary(self) -> Dict[str, Any]:
        """
        Get statistical summary of A-stocks.
        Corresponds to GET /a-stock/stats/summary
        """
        return self._client._request("GET", "/a-stock/stats/summary")