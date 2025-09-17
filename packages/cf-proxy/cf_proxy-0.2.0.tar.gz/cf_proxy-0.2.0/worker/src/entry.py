import json

from workers import Response, WorkerEntrypoint, fetch
from urllib.parse import urlparse, parse_qs

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        try:
            # Grab query params from the original URL, e.g. https://cf_proxy.<username>.workers.dev?url=https://example.com
            original_url = request.url
            query_params = parse_qs(urlparse(original_url).query)
            
            # Validate target URL
            target_url_list = query_params.get('url', [])
            if not target_url_list:
                return Response(
                    json.dumps({"error": "Missing 'url' parameter"}),
                    status=400,
                    headers={"Content-Type": "application/json"}
                )
            
            target_url = target_url_list[0]
            parsed_target = urlparse(target_url)
            if parsed_target.scheme not in ['http', 'https'] or not parsed_target.netloc: # scheme://netloc.com/home
                return Response(
                    json.dumps({"error": "Invalid URL provided"}),
                    status=400,
                    headers={"Content-Type": "application/json"}
                )
            
            # Prepare request options for the proxy request
            proxy_request_options = {
                "method": request.method,
            }

            skip_headers = {
                'host', 'connection', 'keep-alive', 'proxy-authenticate', 
                'proxy-authorization', 'te', 'trailer', 'transfer-encoding', 
                'upgrade', 'x-forwarded-for', 'x-forwarded-proto', 'x-real-ip'
            }
            proxy_headers = {
                key: value
                for key, value in request.headers.items()
                if not (key.lower().startswith('cf-') or key.lower() in skip_headers)
            }
            if proxy_headers:
                proxy_request_options["headers"] = proxy_headers
            
            if request.method not in ("GET", "HEAD"):
                body = await request.body()
                if body:
                    proxy_request_options["body"] = body
            
            response = await fetch(target_url, **proxy_request_options)
            response_body = await response.text()
            response_headers = {}
            for key, value in response.headers.items():
                if key.lower() not in ['transfer-encoding', 'connection', 'keep-alive', 'upgrade']:
                    response_headers[key] = value
            
            response_headers['Access-Control-Allow-Origin'] = '*'
            response_headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD'
            response_headers['Access-Control-Allow-Headers'] = '*'
            
            return Response(
                response_body,
                status=response.status,
                headers=response_headers
            )
            
        except Exception as e:
            return Response(
                json.dumps({"error": f"{e}"}),
                status=500,
                headers={"Content-Type": "application/json"}
            )
