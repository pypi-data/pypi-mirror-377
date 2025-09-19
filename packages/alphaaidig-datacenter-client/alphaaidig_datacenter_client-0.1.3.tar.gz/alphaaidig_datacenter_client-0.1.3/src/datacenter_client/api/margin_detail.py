from __future__ import annotations
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..base import BaseClient


class MarginDetailClient:
    """Client for Margin Detail related endpoints."""
    def __init__(self, client: "BaseClient"):
        self._client = client

    def page_list_by_date(
        self,
        trade_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> Dict[str, Any]:
        """
        Get a paginated list of margin details by date.
        Corresponds to GET /margin_detail/page_list_by_date
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if trade_date:
            params["trade_date"] = trade_date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if order_by:
            params["order_by"] = order_by
        if order_desc:
            params["order_desc"] = order_desc
        
        return self._client._request("GET", "/api/v1/margin_detail/page_list_by_date", params=params)

    def page_list_by_stock(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> Dict[str, Any]:
        """
        Get a paginated list of margin details by stock code.
        Corresponds to GET /margin_detail/page_list_by_stock
        """
        params: Dict[str, Any] = {"stock_code": stock_code, "page": page, "page_size": page_size}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if order_by:
            params["order_by"] = order_by
        if order_desc:
            params["order_desc"] = order_desc
        
        return self._client._request("GET", "/api/v1/margin_detail/page_list_by_stock", params=params)