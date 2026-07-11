#!/bin/bash
echo "✨ Starting Developer DNA Magic Setup..."

# Bring up the full stack including the public Cloudflare tunnel
docker compose -f docker-compose.prod.yml --profile public up -d

echo "⏳ Waiting for backend and cloudflared to spin up (15 seconds)..."
sleep 15

# Extract the trycloudflare URL from the logs
CF_URL=$(docker logs devdna-cloudflared 2>&1 | grep -o 'https://[-a-zA-Z0-9]*\.trycloudflare\.com' | tail -n 1)

if [ -z "$CF_URL" ]; then
    echo "❌ Failed to retrieve Cloudflare URL. Check logs: docker logs devdna-cloudflared"
else
    echo "✅ Setup Complete!"
    echo "🌐 Your Public MCP Endpoint: $CF_URL/mcp"
    echo "📊 Your Public SVG API: $CF_URL/api/v1/badges/"
    
    # Update frontend .env if needed
    echo "NEXT_PUBLIC_API_URL=$CF_URL/api/v1" > frontend/.env.local
    echo "Restarting frontend to pick up new URL..."
    docker restart devdna-frontend

    echo "🚀 Dashboard available at: http://localhost:3000"
fi
