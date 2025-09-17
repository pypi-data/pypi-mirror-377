import json
from abc import ABC, abstractmethod
from typing import Optional, Any, Union
from urllib.parse import urlencode, urlparse

import httpx

from .common import CFProxyError


class ProxyClientBase(ABC):
    """Base class for Proxy clients with common functionality."""
    
    def __init__(
        self, 
        worker_url: str, 
        timeout: float = 10.0,
        client: Optional[Union[httpx.Client, httpx.AsyncClient]] = None
    ):
        """
        Initialize the Proxy client.
        
        Args:
            worker_url: The URL of your deployed Cloudflare Worker
            timeout: Request timeout in seconds
            client: Optional httpx Client/AsyncClient to use
        """
        self.worker_url = worker_url.rstrip('/')
        self.timeout = timeout
        self._client = client
        
        # Validate worker URL
        parsed = urlparse(worker_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid worker URL provided")
    
    def _prepare_worker_url(self, url: str, **kwargs) -> tuple[str, dict]:
        """
        Prepare the worker URL with target URL as query parameter.
        
        Args:
            url: Target URL to proxy to
            **kwargs: Request parameters
            
        Returns:
            Tuple of (worker_request_url, remaining_kwargs)
        """
        # Extract params to build target URL with query parameters
        params = kwargs.pop('params', None)
        
        # Build the target URL with params if provided
        target_url = url
        if params:
            target_url = f"{url}?{urlencode(params)}"
        
        # Build the worker URL with target URL as query parameter
        worker_params = {'url': target_url}
        worker_request_url = f"{self.worker_url}?{urlencode(worker_params)}"
        
        return worker_request_url, kwargs
    
    def _handle_request_error(self, error: Exception) -> None:
        """Handle request errors by wrapping them in CFProxyError."""
        raise CFProxyError(f"{error}")
    
    @abstractmethod
    def close(self):
        """Close the HTTP client if we own it."""
        pass

    @abstractmethod
    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Make a proxied request through the Cloudflare Worker.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL to proxy to
            **kwargs: Additional request parameters:
                - headers: Optional headers to send
                - data: Optional request body data
                - json: Optional JSON data to send
                - params: Optional query parameters
                - Any other httpx parameters
            
        Returns:
            httpx.Response object
        """
        pass
