#!/bin/bash

# Default to the production container name if it exists, otherwise try the compose service name
CONTAINER_NAME="nokari-frontend"

# Check if the container is running
if ! sudo docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    CONTAINER_NAME=$(sudo docker ps --format '{{.Names}}' | grep "frontend" | head -n 1)
fi

if [ -z "$CONTAINER_NAME" ]; then
    echo "Error: Could not find a running frontend container."
    exit 1
fi

echo "Inspecting Frontend Container: $CONTAINER_NAME"
echo "Searching for Firebase Project ID in compiled assets..."

# We look for the "projectId" key which is standard in firebase config objects
# The output might be messy as it is minified JS.
sudo docker exec "$CONTAINER_NAME" grep -r "projectId" /usr/share/nginx/html/assets/ | head -n 1 | grep -o 'projectId:"[^"]*"'

echo ""
echo "Instructions:"
echo "1. Verify that the Project ID above matches the one printed by 'make_admin.sh'."
echo "2. If they do not match, your Frontend was built with different credentials than your Backend."
echo "3. To fix, ensure VITE_FIREBASE_PROJECT_ID is set correctly during the build (docker compose build)."
