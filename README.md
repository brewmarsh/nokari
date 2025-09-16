# Nokari Job Scraper

<!-- Add your project badges here -->
<!-- Please replace YOUR_USERNAME/YOUR_REPO with your actual GitHub username and repository name to enable the badges -->
[![CI Status](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO/branch/main/graph/badge.svg?token=YOUR_CODECOV_TOKEN)](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO)
[![version](https://img.shields.io/github/v/release/YOUR_USERNAME/YOUR_REPO)](https://github.com/YOUR_USERNAME/YOUR_REPO/releases)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Nokari is a web application designed to scrape job postings from various sources, helping users to find relevant job opportunities efficiently. It features a Django backend and a React frontend.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need to have [Docker](https://www.docker.com/get-started) installed on your system.

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
    cd YOUR_REPO
    ```

2.  **Create an environment file:**
    Copy the example environment file `.env.example` to a new file named `.env`.
    ```sh
    cp .env.example .env
    ```
    You will need to fill in the required environment variables in this file. See the Configuration section below for more details.

3.  **Install dependencies and start the application:**
    ```sh
    make up
    ```
    The application will be available at `http://localhost:3000`.

## Running Tests

To run the full suite of tests and code quality checks:
```sh
make all-checks
```

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