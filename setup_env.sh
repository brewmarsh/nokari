#!/bin/bash

# setup_env.sh
# This script sets up the local environment file (.env) for development.
# It copies .env.example to .env and fills in dummy values for required fields
# to allow the application to build and start locally without real credentials.

if [ -f .env ]; then
    echo ".env file already exists."
else
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# Function to set a variable if it's empty
set_var() {
    local var_name=$1
    local default_value=$2
    # Check if the variable exists and is empty (ends with =)
    if grep -q "^$var_name=$" .env; then
        echo "Setting default value for $var_name"
        # use sed to replace empty var with default
        # Escape special characters in default value if necessary
        # For simplicity, assuming default values don't have special regex chars except maybe quotes
        # We use a different delimiter for sed if needed, but | is usually safe for these simple strings
        sed -i "s|^$var_name=$|$var_name=$default_value|" .env
    fi
}

# Set dummy values for frontend to prevent crash
set_var "VITE_FIREBASE_API_KEY" "test-api-key"
set_var "VITE_FIREBASE_AUTH_DOMAIN" "test-auth-domain"
set_var "VITE_FIREBASE_PROJECT_ID" "test-project-id"
set_var "VITE_FIREBASE_STORAGE_BUCKET" "test-storage-bucket"
set_var "VITE_FIREBASE_MESSAGING_SENDER_ID" "test-sender-id"
set_var "VITE_FIREBASE_APP_ID" "test-app-id"
set_var "VITE_FIREBASE_MEASUREMENT_ID" "test-measurement-id"

echo ".env setup complete. Please update it with real credentials if needed."
