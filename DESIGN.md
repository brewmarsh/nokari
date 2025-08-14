# Design Decisions

## Job Search Engine

Instead of direct web scraping, we will use the **Google Custom Search API** to find job postings. This approach is more robust and less likely to break if the target websites change their HTML structure. It leverages Google's powerful search capabilities to find relevant job postings across specified domains.

## Resume Matching Model

We will use a model from **Hugging Face's Transformers** library for resume matching. This will give us access to a wide range of pre-trained models that can be fine-tuned for our specific needs. This will allow us to achieve high accuracy for text matching and professional text generation, and the ability to fine-tune the model will allow it to "learn" from feedback.

## Deployment

We will use **Docker** to containerize the application. This will make it easy to deploy the application in a local network and also to a cloud platform in the future. The `docker-compose.yml` file defines three services: `backend`, `frontend`, and `db`.

- The `backend` service is a Django application running on port 8000.
- The `frontend` service is a React application running on port 3000.
- The `db` service is a PostgreSQL database.

## Component-Based Architecture

The application is broken down into the following components:

*   **User Management:** This component is responsible for user authentication, registration, and profile management.
*   **Job Postings:** This component is responsible for scraping, storing, and displaying job postings.
*   **Resume and Cover Letter Management:** This component is responsible for storing and managing user resumes and cover letters.
*   **Resume Matching:** This component is responsible for matching resumes to job postings and providing a confidence score.
*   **Admin:** This component is responsible for providing administrative functionality, such as managing scrapable domains.
