from typing import Optional

import httpx

from .client import ProxyClientBase


class ProxyClient(ProxyClientBase):
    """Sync client for interfacing with Cloudflare Workers proxy."""
    
    def __init__(
        self, 
        worker_url: str, 
        timeout: float = 10.0,
        client: Optional[httpx.Client] = None
    ):
        super().__init__(worker_url, timeout, client)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        if self._client and hasattr(self._client, 'close'):
            self._client.close()

    def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        # Only prepare the worker URL, let httpx handle everything else
        worker_request_url, remaining_kwargs = self._prepare_worker_url(url, **kwargs)
        
        try:
            if self._client:
                # Use provided client
                response = self._client.request(
                    method=method.upper(),
                    url=worker_request_url,
                    timeout=self.timeout,
                    **remaining_kwargs
                )
            else:
                # Use httpx.request directly
                response = httpx.request(
                    method=method.upper(),
                    url=worker_request_url,
                    timeout=self.timeout,
                    **remaining_kwargs
                )
            
            return response
            
        except Exception as e:
            self._handle_request_error(e)
