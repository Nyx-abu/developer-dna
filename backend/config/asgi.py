"""ASGI config for Developer DNA."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_application = get_asgi_application()

# Import mcp here so it's loaded after Django setup
from mcp_server import mcp

mcp_asgi = None
try:
    mcp_asgi = mcp.http_app()
except Exception:
    pass

async def application(scope, receive, send):
    if scope["type"] == "http" and scope["path"].startswith("/mcp"):
        # Check Bearer token
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode("utf-8")
        
        # A simple token check. In production, this might validate against DB or settings.
        # But we'll just check if there is a bearer token for now, or match a simple env var.
        expected_token = os.environ.get("MCP_TOKEN", "developer-dna-mcp-secret")
        
        if not auth_header.startswith("Bearer ") or auth_header.split(" ")[1] != expected_token:
            await send({
                "type": "http.response.start",
                "status": 401,
                "headers": [[b"content-type", b"text/plain"]],
            })
            await send({
                "type": "http.response.body",
                "body": b"Unauthorized",
            })
            return

        if mcp_asgi:
            return await mcp_asgi(scope, receive, send)
        else:
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [[b"content-type", b"text/plain"]],
            })
            await send({
                "type": "http.response.body",
                "body": b"MCP not configured",
            })
            return
            
    return await django_application(scope, receive, send)
