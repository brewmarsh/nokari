#!/bin/bash

# Default to the production container name if it exists, otherwise try the compose service name
CONTAINER_NAME="nokari-backend"

# Check if the container is running
if ! sudo docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    # Try finding it by compose service name if production name isn't found
    # This assumes standard docker compose naming (project-service-1)
    # We'll try to grep for a container that contains "backend"
    CONTAINER_NAME=$(sudo docker ps --format '{{.Names}}' | grep "backend" | head -n 1)
fi

if [ -z "$CONTAINER_NAME" ]; then
    echo "Error: Could not find a running backend container."
    echo "Please ensure the backend service is running."
    exit 1
fi

if [ -z "$1" ]; then
    echo "Usage: ./make_admin.sh <email>"
    exit 1
fi

EMAIL="$1"

echo "Executing set_admin command on container: $CONTAINER_NAME"
sudo docker exec -it "$CONTAINER_NAME" python -m backend.app.set_admin "$EMAIL"
