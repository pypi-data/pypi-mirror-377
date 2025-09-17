import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import httpx
from cf_proxy import ProxyClient


def main():
    worker_url = "https://cf_proxy.NAME.workers.dev"

    response = httpx.get("https://httpbin.org/ip")
    normal_ip = response.json()["origin"]
    print(f"Your normal IP: {normal_ip}")
    
    print()
    
    with ProxyClient(worker_url=worker_url) as client:
        response = client.request("GET", "https://httpbin.org/ip", verify=False)
        proxy_ip = response.json()["origin"]
        print(f"Proxy IP:  {proxy_ip}")


if __name__ == "__main__":
    main()
