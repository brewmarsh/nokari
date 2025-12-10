# Nokari Job Scraper

Nokari is a web application designed to scrape job postings from various sources, helping users to find relevant job opportunities efficiently. It features a Django backend and a React frontend.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need to have [Docker](https://www.docker.com/get-started) installed on your system.

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/nokari.git
    cd nokari
    ```

2.  **Create an environment file:**
    You can use the provided setup script to create a `.env` file with placeholder values, which allows the application to build and start locally:
    ```sh
    ./setup_env.sh
    ```
    Alternatively, copy the example environment file `.env.example` to a new file named `.env` and fill it manually:
    ```sh
    cp .env.example .env
    ```
    You will need to fill in the required environment variables in this file with real credentials for full functionality. See the Configuration section below for more details.

3.  **Build and run the application using Docker Compose:**
    ```sh
    docker-compose up --build
    ```
    The application will be available at `http://localhost:3000`.

## Configuration

The application is configured using environment variables, which are defined in the `.env` file.

### Google API Credentials

To enable the job scraping functionality, you need to obtain a Google API Key and a Custom Search Engine ID.

#### How to get a Google API Key:

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.
3.  From the navigation menu, go to **APIs & Services > Credentials**.
4.  Click on **+ CREATE CREDENTIALS** and select **API key**.
5.  Your new API key will be created. Copy this key.
6.  It is highly recommended to restrict your API key to prevent unauthorized use. You can restrict it to the **Custom Search API**.
7.  Add the API key to your `.env` file:
    ```
    GOOGLE_API_KEY=your_api_key_here
    ```

#### How to get a Custom Search Engine ID:

1.  Go to the [Programmable Search Engine control panel](https://programmablesearchengine.google.com/controlpanel/all).
2.  Click **Add** to create a new search engine.
3.  Give your search engine a name.
4.  In the "What to search?" section, you can specify the sites you want to search. For this application, you will be providing the sites via the UI, so you can enter a placeholder like `www.google.com` for now. You can also choose to "Search the entire web".
5.  Click **Create**.
6.  After creation, go to the **Basics** tab of your search engine's control panel.
7.  Copy the **Search engine ID**.
8.  Add the Search Engine ID to your `.env` file:
    ```
    CUSTOM_SEARCH_ENGINE_ID=your_search_engine_id_here
    ```
9.  **Important**: Make sure "Search the entire web" is turned **ON** in your search engine's setup tab. This is required for the `site:` search operator to work correctly.

## Automatic Scraping

The application is configured to automatically scrape for new jobs every day. The time of the daily scrape can be configured from the admin panel.

To access the admin panel, you need to be logged in as an admin user. The first user created in the application is automatically an admin.

Once logged in, navigate to the "Admin" page from the user menu. Here you will find the "Scheduled Scrape" section where you can set the time for the daily scrape.
## Deployment

This project is configured for continuous deployment to a Hostinger VPS using GitHub Actions.

### How it Works

When code is pushed to the `main` branch, a GitHub Actions workflow is triggered. This workflow performs the following steps:

1.  **Builds Docker Images**: It builds the backend and frontend Docker images.
2.  **Pushes to Docker Hub**: The newly built images are pushed to Docker Hub.
3.  **Deploys to VPS**: The workflow then connects to the Hostinger VPS via SSH and runs a deployment script. This script pulls the latest images from Docker Hub and restarts the application services using `docker-compose`.

### Server Setup

Before the first deployment, you need to set up the `.env` file on your production server.

1.  SSH into your VPS:
    ```sh
    ssh your_vps_user@your_vps_ip
    ```
2.  Create the application directory (replace `your_vps_user` with your actual username):
    ```sh
    mkdir -p /home/your_vps_user/nokari-app
    ```
3.  Create a `.env` file in the application directory:
    ```sh
    nano /home/your_vps_user/nokari-app/.env
    ```
4.  Add the necessary environment variables to this file. You can use the `.env.example` file as a reference. Make sure to set the production values for your database, API keys, and other secrets.

### Triggering a Deployment

To deploy a new version of the application, simply push your changes to the `main` branch. The GitHub Actions workflow will handle the rest.

### Manual Deployment

While deployment is automated, you can manually trigger the deployment script on the server if needed.

1.  SSH into your VPS:
    ```sh
    ssh your_user@your_vps_ip
    ```
2.  Navigate to the application directory:
    ```sh
    cd /home/user/nokari-app
    ```
3.  Run the deployment script:
    ```sh
    ./deploy.sh
    ```
