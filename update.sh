
#!/bin/bash
cd "$(dirname "$0")"
echo "🔄 Checking updates..."
git pull
docker compose down
docker compose up -d --build
echo "✅ Updated & restarted"
