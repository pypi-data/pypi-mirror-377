from typing import Optional

import httpx

from .client import ProxyClientBase


class AsyncProxyClient(ProxyClientBase):
    """Async client for interfacing with Cloudflare Workers proxy."""
    
    def __init__(
        self, 
        worker_url: str, 
        timeout: float = 10.0,
        client: Optional[httpx.AsyncClient] = None
    ):
        super().__init__(worker_url, timeout, client)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        if self._client and hasattr(self._client, 'aclose'):
            await self._client.aclose()
    
    async def request(
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
                response = await self._client.request(
                    method=method.upper(),
                    url=worker_request_url,
                    timeout=self.timeout,
                    **remaining_kwargs
                )
            else:
                # Use httpx.request directly
                async with httpx.AsyncClient(timeout=self.timeout) as temp_client:
                    response = await temp_client.request(
                        method=method.upper(),
                        url=worker_request_url,
                        **remaining_kwargs
                    )
            
            return response
                
        except Exception as e:
            self._handle_request_error(e)
