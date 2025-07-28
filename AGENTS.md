This file provides instructions for AI agents working with this codebase.

## Project Structure

*   `app/`: Contains the Django backend application.
*   `frontend/`: Contains the React frontend application.
*   `docs/`: Contains project documentation.
*   `docker/`: Contains Dockerfiles and Docker Compose configurations.

## Build, Test, and Deployment

*   **To install dependencies:**
    *   Backend: `pip install -r requirements.txt`
    *   Frontend: `npm install`
*   **To run unit tests:**
    *   Backend: `python manage.py test`
    *   Frontend: `npm test`
*   **To build the project:**
    *   `docker compose build`
*   **To start local services:**
    *   `docker compose up --build -d`

## Common Debugging Procedures

*   **API Issues:** Check the backend logs for errors: `docker logs app-backend-1`
*   **Docker Container Issues:** Use `docker logs [container_name]` to retrieve logs.
*   **Docker Build Failures:** If a Docker build fails, consider rebuilding with `DOCKER_BUILDKIT=0` for more verbose output to inspect layers.

## Coding Standards and Best Practices

*   **Backend:**
    *   Follow the PEP 8 style guide for Python.
    *   Use docstrings for all modules, classes, and functions.
*   **Frontend:**
    *   All React components should be functional components.
    *   Use `const` over `let` where variable reassignment is not needed.
*   **General:**
    *   Error handling should use centralized `try-catch` blocks and log to `console.error`.

## Resource Optimization Guidelines

*   Before running large builds, ensure the `/tmp/` directory is cleared.
*   For Node.js projects, execute `npm cache clean --force` to free up disk space in the VM.
*   For Python projects, execute `pip cache purge` to free up disk space in the VM.
*   If you are still running into disk space issues, you can prune the docker builder cache with `docker builder prune -a -f`.

## Environment Variables

*   The `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` environment variables must be set for the backend to connect to the database. These are set in the `.env` file.

## Input/Output Conventions

*   Generated documentation should follow JSDoc format.
*   All new features should include corresponding unit tests with at least 80% code coverage.
# Agent Guidelines

This document provides guidelines for agents working on this codebase.

## 1. Code Style

- All Python code must adhere to the PEP 8 style guide.
- Use a linter like `flake8` or `pylint` to check for style issues before submitting code.

## 2. Documentation

- All public functions and classes must have comprehensive docstrings that explain their purpose, arguments, and return values.
- Use the Google Python Style Guide for docstring formatting.

## 3. Configuration

- All configuration data must be validated using `voluptuous` schemas.
- Provide clear error messages for invalid configuration.

## 4. Constants

- All constants must be defined in `custom_components/meraki_ha/const.py`.
- Do not use magic strings or numbers in the code.

## 5. Testing

- All new features must be accompanied by unit tests.
- Run the entire test suite before submitting code to ensure that no regressions have been introduced.

## 6. Dependencies

- Use `dependabot` to keep dependencies up-to-date.
- Regularly review and update dependencies as needed.
