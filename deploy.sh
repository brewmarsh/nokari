#!/bin/bash
set -e

# This script will be run on the VPS to deploy the application.
# It will be called from the GitHub Actions workflow.

# Variables will be passed from the GitHub Actions workflow
# DOCKERHUB_USERNAME
# DOCKERHUB_TOKEN
# IMAGE_NAME_BACKEND
# IMAGE_NAME_FRONTEND
# IMAGE_TAG

echo "Starting deployment..."

# Set the app directory
APP_DIR="/home/$VPS_USERNAME/nokari-app"

# Create app directory if it doesn't exist
mkdir -p $APP_DIR
cd $APP_DIR

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Please create it on the server."
    exit 1
fi

# Log in to Docker Hub
echo "Logging in to Docker Hub..."
echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

# Pull the latest images
echo "Pulling latest images..."
docker pull "$DOCKERHUB_USERNAME/$IMAGE_NAME_BACKEND:$IMAGE_TAG"
docker pull "$DOCKERHUB_USERNAME/$IMAGE_NAME_FRONTEND:$IMAGE_TAG"

# Stop the current services and start the new ones
echo "Stopping and restarting services..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Clean up unused images
echo "Cleaning up unused images..."
docker image prune -a -f

echo "Deployment finished successfully."
