# cf_proxy

Python package utilizing Cloudflare Workers to proxy requests

## Prerequisites
- Python 3.8+
- Node.js
- Cloudflare account (100k request/day free)

## Setup (Cloudflare)

1. Deploy the Cloudflare worker
   ```bash
   cd worker
   npx wrangler@latest deploy
   ```

2. Grab your worker URL
   After successful deployment, Wrangler will output your worker URL. It will look like:
   ```
   https://cf_proxy.<username>.workers.dev
   ```

## Getting Started

1. Install the package
   ```
   pip install cf-proxy
   ```

2. Run an [example](https://github.com/kevintsoii/cf_proxy/tree/main/example)
   ```
   pip install httpx
   cd example
   python sync_example.py
   ```

