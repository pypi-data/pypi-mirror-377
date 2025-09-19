from __future__ import annotations
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..base import BaseClient


class MarginAnalysisClient:
    """Client for Margin Analysis related endpoints."""
    def __init__(self, client: "BaseClient"):
        self._client = client

    def page_list(
        self,
        trade_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        analysis_type: Optional[str] = None,
        target_code: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> Dict[str, Any]:
        """
        Get a paginated list of margin analysis results.
        Corresponds to GET /margin_analysis/page_list
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if trade_date:
            params["trade_date"] = trade_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if analysis_type:
            params["analysis_type"] = analysis_type
        if target_code:
            params["target_code"] = target_code
        if order_by:
            params["order_by"] = order_by
        if order_desc:
            params["order_desc"] = order_desc
        
        return self._client._request("GET", "/api/v1/margin_analysis/page_list", params=params)

    def page_list_by_index(
        self,
        trade_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        target_code: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> Dict[str, Any]:
        """
        Get a paginated list of margin analysis results by index.
        Corresponds to GET /margin_analysis/page_list_by_index
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if trade_date:
            params["trade_date"] = trade_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if target_code:
            params["target_code"] = target_code
        if order_by:
            params["order_by"] = order_by
        if order_desc:
            params["order_desc"] = order_desc
        
        return self._client._request("GET", "/api/v1/margin_analysis/page_list_by_index", params=params)

    def page_list_by_industry(
        self,
        trade_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        target_code: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> Dict[str, Any]:
        """
        Get a paginated list of margin analysis results by industry.
        Corresponds to GET /margin_analysis/page_list_by_industry
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if trade_date:
            params["trade_date"] = trade_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if target_code:
            params["target_code"] = target_code
        if order_by:
            params["order_by"] = order_by
        if order_desc:
            params["order_desc"] = order_desc
        
        return self._client._request("GET", "/api/v1/margin_analysis/page_list_by_industry", params=params)