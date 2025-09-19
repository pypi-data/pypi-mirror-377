from __future__ import annotations
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..base import BaseClient


class SWIndustryCompanyClient:
    """Client for SW-Industry-Company related endpoints."""
    def __init__(self, client: "BaseClient"):
        self._client = client

    def page_list(
        self,
        page: int = 1,
        page_size: int = 50,
        stock_code: Optional[str] = None,
        stock_name: Optional[str] = None,
        industry_code: Optional[str] = None,
        level1_industry_code: Optional[str] = None,
        level2_industry_code: Optional[str] = None,
        level3_industry_code: Optional[str] = None,
        level1_industry: Optional[str] = None,
        level2_industry: Optional[str] = None,
        level3_industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a paginated list of SW-industry companies.
        Corresponds to GET /sw_industry_company/page_list
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if stock_code:
            params["stock_code"] = stock_code
        if stock_name:
            params["stock_name"] = stock_name
        if industry_code:
            params["industry_code"] = industry_code
        if level1_industry_code:
            params["level1_industry_code"] = level1_industry_code
        if level2_industry_code:
            params["level2_industry_code"] = level2_industry_code
        if level3_industry_code:
            params["level3_industry_code"] = level3_industry_code
        if level1_industry:
            params["level1_industry"] = level1_industry
        if level2_industry:
            params["level2_industry"] = level2_industry
        if level3_industry:
            params["level3_industry"] = level3_industry
        
        return self._client._request("GET", "/api/v1/sw_industry_company/page_list", params=params)

    def list(
        self,
        stock_code: Optional[str] = None,
        stock_name: Optional[str] = None,
        industry_code: Optional[str] = None,
        level1_industry_code: Optional[str] = None,
        level2_industry_code: Optional[str] = None,
        level3_industry_code: Optional[str] = None,
        level1_industry: Optional[str] = None,
        level2_industry: Optional[str] = None,
        level3_industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a list of SW-industry companies without pagination.
        Corresponds to GET /sw_industry_company/list
        """
        params: Dict[str, Any] = {}
        if stock_code:
            params["stock_code"] = stock_code
        if stock_name:
            params["stock_name"] = stock_name
        if industry_code:
            params["industry_code"] = industry_code
        if level1_industry_code:
            params["level1_industry_code"] = level1_industry_code
        if level2_industry_code:
            params["level2_industry_code"] = level2_industry_code
        if level3_industry_code:
            params["level3_industry_code"] = level3_industry_code
        if level1_industry:
            params["level1_industry"] = level1_industry
        if level2_industry:
            params["level2_industry"] = level2_industry
        if level3_industry:
            params["level3_industry"] = level3_industry
        
        return self._client._request("GET", "/api/v1/sw_industry_company/list", params=params)