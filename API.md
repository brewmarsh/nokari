# API Documentation

This document provides an overview of the API endpoints available in the application.

## Authentication

Authentication is handled via JWT (JSON Web Tokens). To access protected endpoints, you must include an `Authorization` header with the value `Bearer <token>`.

### Endpoints

*   **POST /api/register/**: Register a new user.
*   **POST /api/login/**: Log in and receive a JWT.
*   **POST /api/login/refresh/**: Refresh an access token.

## Users

*   **GET /api/me/**: Get the details of the currently authenticated user.

## Job Postings

*   **GET /api/jobs/**: Get a list of all job postings.
*   **POST /api/jobs/**: Create a new job posting.

## Resumes

*   **GET /api/resumes/**: Get a list of all resumes for the authenticated user.
*   **POST /api/resumes/**: Upload a new resume.
*   **GET /api/resumes/<id>/**: Get a specific resume.
*   **DELETE /api/resumes/<id>/**: Delete a specific resume.

## Cover Letters

*   **GET /api/cover-letters/**: Get a list of all cover letters for the authenticated user.
*   **POST /api/cover-letters/**: Upload a new cover letter.
*   **GET /api/cover-letters/<id>/**: Get a specific cover letter.
*   **DELETE /api/cover-letters/<id>/**: Delete a specific cover letter.

## Scrapable Domains

*   **GET /api/scrapable-domains/**: Get a list of all scrapable domains. (Admin only)
*   **POST /api/scrapable-domains/**: Add a new scrapable domain. (Admin only)

## Scraping

*   **POST /api/scrape/**: Trigger the job scraping process. (Admin only)
*   **GET /api/scrape-history/**: Get the history of scraping events. (Admin only)
*   **GET /api/scrape-schedule/**: Get the current daily scrape schedule. (Admin only)
*   **PUT /api/scrape-schedule/**: Update the daily scrape schedule. (Admin only)
