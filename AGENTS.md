This file provides instructions for AI agents working with this codebase.

## Project Overview

This project consists of a Django backend and a React frontend.

*   `app/`: Contains the Django backend application.
*   `frontend/`: Contains the React frontend application.
*   `docs/`: Contains project documentation.
*   `docker/`: Contains Dockerfiles and Docker Compose configurations.

## Development Setup

### Dependencies
*   **Backend:** `pip install -r requirements.txt`
*   **Frontend:** `npm install`

### Building and Running
*   **Build:** `docker compose build`
*   **Run:** `docker compose up --build -d`

## Coding Standards

### General
*   Error handling should use centralized `try-catch` blocks and log to `console.error`.
*   **Separation of Concerns:** Code should be organized into distinct sections that each address a separate concern. If a component or function is responsible for too many different things, it should be refactored.

### Backend
*   Follow the PEP 8 style guide for Python.
*   Use a linter like `flake8` or `pylint` to check for style issues.
*   Run `black .` and `flake8 .` before submitting any changes to the backend.
*   All public functions and classes must have comprehensive docstrings using the Google Python Style Guide format.
*   All configuration data must be validated using `voluptuous` schemas.
*   Define constants in `custom_components/meraki_ha/const.py`.

### Frontend
*   All React components should be functional components.
*   Use `const` over `let` where variable reassignment is not needed.
*   Generated documentation should follow JSDoc format.

## Testing

*   **Run Tests:**
    *   **Backend:** `python manage.py test`
    *   **Frontend:** `npm test`
*   All new features must be accompanied by unit tests with at least 80% code coverage.
*   Run the entire test suite before submitting code to ensure that no regressions have been introduced.

## Debugging

*   **API Issues:** Check the backend logs for errors: `docker logs app-backend-1`
*   **Docker Container Issues:** Use `docker logs [container_name]` to retrieve logs.
*   **Docker Build Failures:** If a Docker build fails, consider rebuilding with `DOCKER_BUILDKIT=0` for more verbose output to inspect layers.

## Environment Variables

*   The `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` environment variables must be set in the `.env` file for the backend to connect to the database.

## Dependencies

*   Use `dependabot` to keep dependencies up-to-date.
*   Regularly review and update dependencies as needed.

## Resource Optimization

*   Before running large builds, ensure the `/tmp/` directory is cleared.
*   For Node.js projects, execute `npm cache clean --force` to free up disk space.
*   For Python projects, execute `pip cache purge` to free up disk space.
*   If you still have disk space issues, prune the Docker builder cache: `docker builder prune -a -f`.
