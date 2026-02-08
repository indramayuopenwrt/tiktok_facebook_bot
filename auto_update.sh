
#!/bin/bash
cd "$(dirname "$0")"
while true; do
  sleep 300
  git fetch origin
  LOCAL=$(git rev-parse @)
  REMOTE=$(git rev-parse @{u})
  if [ "$LOCAL" != "$REMOTE" ]; then
    echo "🚀 Update detected!"
    ./update.sh
  fi
done
