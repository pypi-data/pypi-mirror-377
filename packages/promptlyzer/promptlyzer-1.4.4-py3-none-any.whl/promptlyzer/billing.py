"""
Billing Manager for Promptlyzer Client

Provides minimal billing functionality for credit balance checking.
"""

from typing import Dict, Optional
import logging
import time
from .exceptions import AuthenticationError, ServerError, PromptlyzerError

logger = logging.getLogger(__name__)


class BillingManager:
    """
    Manages billing operations for the Promptlyzer client.
    
    This is a minimal implementation that only provides balance checking.
    All other billing operations (transactions, cost calculation, etc.) 
    are handled automatically by the backend.
    """
    
    def __init__(self, client):
        """
        Initialize the BillingManager.
        
        Args:
            client: The PromptlyzerClient instance
        """
        self.client = client
        self._balance_cache = None
        self._cache_timestamp = None
    
    def get_balance(self, force_refresh: bool = False) -> Dict:
        """
        Get the current user's credit balance.
        
        Args:
            force_refresh: Force a fresh API call, bypassing cache
            
        Returns:
            A dictionary containing:
                - credits: Current credit balance
                - is_low_balance: True if credits < 5.0
                
        Raises:
            AuthenticationError: If the API key is invalid
            ServerError: If the server returns an error
            
        Example:
            >>> balance = client.billing.get_balance()
            >>> print(f"Credits: {balance['credits']}")
            >>> if balance['is_low_balance']:
            ...     print("Warning: Low credit balance!")
        """
        # Check cache if not forcing refresh
        if not force_refresh and self._is_cache_valid():
            logger.debug("Returning cached balance")
            return self._balance_cache
        
        # Make API request
        try:
            response = self.client._make_request(
                method="GET",
                endpoint="/billing/balance"
            )
            
            # Extract relevant fields for client
            balance_data = {
                "credits": response.get("credits", 0.0),
                "is_low_balance": response.get("is_low_balance", False)
            }
            
            # Update cache
            self._balance_cache = balance_data
            self._cache_timestamp = time.time()
            
            logger.info(f"Balance retrieved: {balance_data['credits']} credits")
            return balance_data
            
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            raise PromptlyzerError(f"Failed to get balance: {str(e)}")
    
    def _is_cache_valid(self) -> bool:
        """
        Check if the balance cache is still valid.
        
        Returns:
            True if cache is valid, False otherwise
        """
        if self._balance_cache is None or self._cache_timestamp is None:
            return False
        
        # Cache is valid for 60 seconds
        cache_age = time.time() - self._cache_timestamp
        return cache_age < 60
    
    def clear_cache(self):
        """
        Clear the balance cache.
        
        This can be useful after operations that might change the balance.
        """
        self._balance_cache = None
        self._cache_timestamp = None
        logger.debug("Balance cache cleared")