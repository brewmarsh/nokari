# API Documentation

This document outlines the API endpoints for the nokari application.

## Authentication

*   **POST /api/register/**: Register a new user.
    *   **Request Body:** `{ "email": "user@example.com", "password": "password", "role": "user" }`
    *   **Response:** `{ "email": "user@example.com", "role": "user" }`
*   **POST /api/login/**: Log in an existing user.
    *   **Request Body:** `{ "email": "user@example.com", "password": "password" }`
    *   **Response:** `{ "access": "...", "refresh": "..." }`
*   **POST /api/login/refresh/**: Refresh an access token.
    *   **Request Body:** `{ "refresh": "..." }`
    *   **Response:** `{ "access": "..." }`

## Job Postings

*   **GET /api/jobs/**: Get a list of job postings.
    *   **Query Parameters:** `title`, `company`, `search`
    *   **Response:** `[{ "id": 1, "company": "...", "title": "...", "description": "...", "posting_date": "...", "confidence_score": 0.8 }]`

## Resumes

*   **GET /api/resumes/**: Get a list of the current user's resumes.
    *   **Response:** `[{ "id": 1, "name": "My Resume", "file": "...", "uploaded_at": "..." }]`
*   **POST /api/resumes/**: Upload a new resume.
    *   **Request Body:** `{ "name": "My Resume", "file": "..." }`
    *   **Response:** `{ "id": 1, "name": "My Resume", "file": "...", "uploaded_at": "..." }`
*   **GET /api/resumes/<id>/**: Get a specific resume.
    *   **Response:** `{ "id": 1, "name": "My Resume", "file": "...", "uploaded_at": "..." }`
*   **PUT /api/resumes/<id>/**: Update a specific resume.
    *   **Request Body:** `{ "name": "My Updated Resume" }`
    *   **Response:** `{ "id": 1, "name": "My Updated Resume", "file": "...", "uploaded_at": "..." }`
*   **DELETE /api/resumes/<id>/**: Delete a specific resume.

## Cover Letters

*   **GET /api/cover-letters/**: Get a list of the current user's cover letters.
    *   **Response:** `[{ "id": 1, "name": "My Cover Letter", "file": "...", "uploaded_at": "..." }]`
*   **POST /api/cover-letters/**: Upload a new cover letter.
    *   **Request Body:** `{ "name": "My Cover Letter", "file": "..." }`
    *   **Response:** `{ "id": 1, "name": "My Cover Letter", "file": "...", "uploaded_at": "..." }`
*   **GET /api/cover-letters/<id>/**: Get a specific cover letter.
    *   **Response:** `{ "id": 1, "name": "My Cover Letter", "file": "...", "uploaded_at": "..." }`
*   **PUT /api/cover-letters/<id>/**: Update a specific cover letter.
    *   **Request Body:** `{ "name": "My Updated Cover Letter" }`
    *   **Response:** `{ "id": 1, "name": "My Updated Cover Letter", "file": "...", "uploaded_at": "..." }`
*   **DELETE /api/cover-letters/<id>/**: Delete a specific cover letter.

## Resume Generation

*   **POST /api/generate-resume/**: Generate a new resume based on a job posting.
    *   **Request Body:** `{ "job_posting_id": 1 }`
    *   **Response:** `{ "resume_text": "..." }`

## Cover Letter Generation

*   **POST /api/generate-cover-letter/**: Generate a new cover letter based on a job posting.
    *   **Request Body:** `{ "job_posting_id": 1 }`
    *   **Response:** `{ "cover_letter_text": "..." }`

## Admin

*   **GET /api/scrapable-domains/**: Get a list of scrapable domains.
    *   **Response:** `[{ "id": 1, "domain": "..." }]`
*   **POST /api/scrapable-domains/**: Add a new scrapable domain.
    *   **Request Body:** `{ "domain": "..." }`
    *   **Response:** `{ "id": 1, "domain": "..." }`
