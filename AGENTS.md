# Agent Instructions

## 1. High-Level Architectural Overview
This project consists of a Django backend and a React frontend. The backend is in the `app` directory and the frontend is in the `frontend` directory. It uses Celery for asynchronous tasks and Redis as a message broker. The application is containerized using Docker.

## 2. Key Files and Directories
- `README.md`: Project overview, setup, and usage.
- `app/`: Main application source code.
- `tests/`: All application tests.
- `Makefile`: All common commands for development and CI.
- `docker-compose.yml`: Defines the development environment.
- `Dockerfile`: Instructions to build a production-ready container.
- `entrypoint.sh`: Runs database migrations and starts the application.

## 3. Build, Test, and Deployment
- **To set up the local environment:** `make install`
- **To build and start the application:** `make up`
- **To run all tests and quality checks:** `make all-checks`
- **To clean the environment:** `make clean`

## Coding Standards

### General
*   Error handling should use centralized `try-catch` blocks and log to `console.error`.

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
