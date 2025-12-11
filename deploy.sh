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

# Configure ALLOWED_HOSTS
echo "Configuring ALLOWED_HOSTS..."
# Remove existing DJANGO_ALLOWED_HOSTS line if it exists
sed -i '/^DJANGO_ALLOWED_HOSTS=/d' .env
# Add the new DJANGO_ALLOWED_HOSTS line, including localhost and the server's IP
echo "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,$VPS_HOST,pickaladder.io" >> .env

# Log in to Docker Hub
echo "Logging in to Docker Hub..."
echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

# Pull the latest images
echo "Pulling latest images..."
docker pull "$DOCKERHUB_USERNAME/$IMAGE_NAME_BACKEND:$IMAGE_TAG"
docker pull "$DOCKERHUB_USERNAME/$IMAGE_NAME_FRONTEND:$IMAGE_TAG"

# Stop the current services and start the new ones
echo "Stopping and restarting services..."
docker-compose -f docker-compose.prod.yml down --remove-orphans
docker-compose -f docker-compose.prod.yml up -d

# Clean up unused images
echo "Cleaning up unused images..."
docker image prune -a -f

echo "Deployment finished successfully."
