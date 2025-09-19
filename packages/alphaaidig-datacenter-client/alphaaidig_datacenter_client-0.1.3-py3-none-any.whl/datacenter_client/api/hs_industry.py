from __future__ import annotations
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..base import BaseClient


class HSIndustryClient:
    """Client for HS-Industry related endpoints."""
    def __init__(self, client: "BaseClient"):
        self._client = client

    def page_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        business_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a paginated list of HS-industries.
        Corresponds to GET /hs_industry/page_list
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        if business_category:
            params["business_category"] = business_category
        
        return self._client._request("GET", "/api/v1/hs_industry/page_list", params=params)

    def get(self, industry_code: str) -> Dict[str, Any]:
        """
        Get details for a specific HS-industry by its code.
        Corresponds to GET /hs_industry/{industry_code}
        """
        return self._client._request("GET", f"/api/v1/hs_industry/{industry_code}")

    def summary(self) -> Dict[str, Any]:
        """
        Get statistical summary of HS-industries.
        Corresponds to GET /hs_industry/stats/summary
        """
        return self._client._request("GET", "/api/v1/hs_industry/stats/summary")