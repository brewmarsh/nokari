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

## Find Similar Jobs Feature

This feature allows users to find job postings that are similar to one they are interested in.

### API Design

*   A new API endpoint will be created at `POST /jobs/{job_id}/find-similar`.
*   The endpoint will take a `job_id` as a path parameter.
*   The request will trigger an asynchronous task on the backend to find similar jobs.
*   The API will immediately return a task ID, which the frontend can use to poll for the results. (Note: For the MVP, we might opt for a simpler approach where the frontend just waits for the results, with a timeout. The asynchronous task queue might be a post-MVP enhancement).
*   The results will be a list of job postings, ranked by similarity score.

### Similarity Logic (MVP)

For the initial implementation (MVP), the similarity logic will be based on a combination of job title and keywords from the job description.

1.  **Job Title Similarity:**
    *   The titles of all job postings will be compared using a simple string similarity algorithm (e.g., Levenshtein distance or n-gram similarity).
2.  **Keyword Extraction:**
    *   For the selected job, a set of key skills and technologies will be extracted from its description. This can be done using a pre-defined list of keywords or a simple NLP library for noun phrase extraction.
3.  **Keyword Matching:**
    *   Other job postings will be scored based on the number of matching keywords found in their descriptions.
4.  **Combined Score:**
    *   The final similarity score will be a weighted combination of the title similarity score and the keyword matching score.

### Asynchronous Processing

*   To avoid blocking the UI, the similarity calculation will be performed asynchronously.
*   For the MVP, this can be achieved by running the calculation in a separate thread or using a simple background task runner integrated with Django (e.g., `threading` module for simplicity, or a more robust solution like Celery for a production environment).
