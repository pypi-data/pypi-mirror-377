import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import asyncio
import httpx
from cf_proxy import AsyncProxyClient


async def main():
    worker_url = "https://cf_proxy.NAME.workers.dev"
    
    async with httpx.AsyncClient() as client:
        response = await client.get("https://httpbin.org/ip")
        normal_ip = response.json()["origin"]
        print(f"Your normal IP: {normal_ip}")
    
    print()
    
    httpx_client = httpx.AsyncClient(timeout=10.0, verify=False)
    async with AsyncProxyClient(worker_url=worker_url, client=httpx_client) as client:
        response = await client.request("GET", "https://httpbin.org/ip")
        proxy_ip = response.json()["origin"]
        print(f"Proxy IP: {proxy_ip}")

if __name__ == "__main__":
    asyncio.run(main())
