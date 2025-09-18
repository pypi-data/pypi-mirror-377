from typing import Optional

from .base import BaseClient
from .api.a_stock import AStockClient

class DatacenterClient(BaseClient):
    """
    The main client for interacting with all Datacenter API services.
    
    This client provides access to different API resource groups (e.g., A-stocks)
    through dedicated sub-clients.
    
    Usage:
        with DatacenterClient(base_url="...") as client:
            stocks = client.a_stock.list()
    """
    def __init__(self, base_url: str, token: Optional[str] = None, timeout: int = 30):
        """
        Initializes the main client.

        Args:
            base_url: The base URL for the API, e.g., "http://localhost:8000".
            token: An optional authentication token.
            timeout: The request timeout in seconds.
        """
        super().__init__(base_url, token, timeout)
        
        # Initialize sub-clients for each API resource
        self.a_stock = AStockClient(self)
        # Other clients like self.hk_stock = HKStockClient(self) can be added here.