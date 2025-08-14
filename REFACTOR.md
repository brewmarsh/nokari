# Nokari Refactoring and Improvement Plan

This document outlines a prioritized plan for refactoring and improving the Nokari application. The tasks are ordered by priority, addressing security, reliability, and maintainability.

---

## Priority 1: Critical Security Vulnerabilities
This document outlines potential future improvements for the project, broken down into actionable plans that can be executed by an AI agent. The tasks are prioritized based on their impact on the project's security, reliability, and maintainability.

---

## Prioritization

The refactoring tasks are prioritized as follows:
1.  **Security:** Addressing security vulnerabilities and hardening the application is the highest priority.
2.  **Reliability:** Ensuring the application is stable, resilient, and performs as expected.
3.  **Maintainability:** Improving the codebase, documentation, and development processes to make the project easier to manage and extend.

**Goal:** Address all known security vulnerabilities to protect the application and its users.

### 1.1. Remediate Python Dependency Vulnerabilities

*   **Issue:** The `safety` scan identified a vulnerability in `djangorestframework-simplejwt` (CVE-2024-22513).
*   **Plan:**
    1.  **Investigate:** Review the CVE details to determine the patched version.
    2.  **Update:** Modify `requirements.in` to specify the patched version of `djangorestframework-simplejwt`.
    3.  **Recompile:** Run `pip-compile requirements.in` to update `requirements.txt`.
    4.  **Verify:** Run `safety check -r requirements.txt` to confirm the vulnerability is resolved.

### 1.2. Remediate Frontend Dependency Vulnerabilities

*   **Issue:** `npm audit` reported 9 vulnerabilities (3 moderate, 6 high) in `nth-check`, `postcss`, and `webpack-dev-server`.
*   **Plan:**
    1.  **Attempt Automatic Fix:** In the `frontend/` directory, run `npm audit fix`.
    2.  **Manual Intervention:** If the automatic fix fails or causes breaking changes, manually update the vulnerable packages by editing `frontend/package.json` and `frontend/package-lock.json`. The `resolutions` field might need to be adjusted.
    3.  **Verify:** Run `npm audit` again to ensure all vulnerabilities have been addressed.

### 1.3. Harden the Backend Docker Image

*   **Issue:** The `Dockerfile.backend` has two critical security flaws:
    1.  It uses `apt-get update --allow-insecure-repositories`, which exposes the build process to man-in-the-middle attacks.
    2.  The application is run as the `root` user inside the container.
*   **Plan:**
    1.  **Remove Insecure Flag:** Delete the `--allow-insecure-repositories` flag from the `RUN` command in `Dockerfile.backend`.
    2.  **Create a Non-Root User:** Add commands to `Dockerfile.backend` to create a non-root user and group.
    3.  **Switch User:** Use the `USER` instruction in the Dockerfile to switch to the non-root user before running the application.

---

## Priority 2: Reliability and Best Practices

**Goal:** Improve the stability and consistency of the application and its development environment.

### 2.1. Pin Python Dependencies

*   **Issue:** The original `requirements.txt` did not have pinned versions, leading to unreproducible builds.
*   **Status:** **Done.** A `requirements.in` file has been created, and `pip-tools` has been used to generate a fully pinned `requirements.txt`. This should be maintained as standard practice.

### 2.2. Enhance Docker Workflow

*   **Issue:** The Docker setup can be optimized for better performance and maintainability.
*   **Plan:**
    1.  **Optimize with Multi-Stage Builds:** Refactor `Dockerfile.backend` and `frontend/Dockerfile` to use multi-stage builds. This will create smaller, more secure final images by separating the build environment from the runtime environment.
    2.  **Create an Entrypoint Script:** Instead of a long `CMD` string in the Dockerfile and `docker-compose.yml`, create a `docker-entrypoint.sh` script to handle database migrations, data loading, and starting the gunicorn server. This improves readability and maintainability.
    3.  **Optimize Docker Cache:** Refine the `COPY` instructions in the Dockerfiles to copy only necessary files at each step, improving layer caching and build times.

### 2.3. Expand Test Coverage

*   **Issue:** The project lacks sufficient test coverage, increasing the risk of regressions.
*   **Plan:** Implement the detailed testing plan from the original `REFACTOR.md`, which includes:
    1.  **Backend:** Configure `pytest-django` and `coverage`, write model and API tests, and integrate coverage checks into the CI pipeline.
    2.  **Frontend:** Configure Jest for coverage reporting, write component tests using `@testing-library/react`, and create a frontend CI workflow.

---

## Priority 3: Maintainability and Documentation

**Goal:** Make the project easier for new and existing developers to understand and contribute to.

### 3.1. Add Project Documentation

*   **Issue:** The project lacks centralized documentation.
*   **Plan:** Implement the documentation plan from the original `REFACTOR.md`:
    1.  **Setup:** Add `mkdocs` and `mkdocs-material` to `requirements_dev.txt`.
    2.  **Create Content:** Create a `docs/` directory with initial documentation for project overview, development setup, and architecture.
    3.  **Deploy:** Set up a GitHub Actions workflow to automatically build and deploy the documentation to GitHub Pages.

### 3.2. Automate Dependency Updates

*   **Issue:** Dependencies can become outdated, posing security risks.
*   **Plan:** Implement the `Dependabot` configuration from the original `REFACTOR.md`:
    1.  **Create Config:** Create a `.github/dependabot.yml` file to schedule weekly checks for both `pip` and `npm` dependencies.
    2.  **Activate:** Commit the file to the `main` branch to enable Dependabot.
## Phase 1: Security Hardening (High Priority)

### 1.1. Pin Dependencies

**Goal:** Prevent security vulnerabilities and ensure reproducible builds by pinning all dependencies to specific versions.

**Plan:**
1.  **Backend (pip):**
    *   Create a `requirements.in` file listing the top-level dependencies.
    *   Use `pip-tools` to compile `requirements.in` into a fully-pinned `requirements.txt` file.
    *   Update the Dockerfile to use the new `requirements.txt`.
2.  **Frontend (npm):**
    *   Run `npm audit` to identify and fix any known vulnerabilities.
    *   Ensure that `package-lock.json` is committed to the repository and used for installations (`npm ci`).

### 1.2. Automate Vulnerability Scanning

**Goal:** Proactively identify and address security vulnerabilities in dependencies.

**Plan:**
1.  **Backend:**
    *   Add a step to the `.github/workflows/python-lint.yaml` workflow to run `safety` against `requirements.txt`.
2.  **Frontend:**
    *   Add a step to a new frontend CI workflow to run `npm audit --audit-level=high`.

### 1.3. Secure Django Settings

**Goal:** Harden the Django application by configuring security settings appropriately.

**Plan:**
1.  **Review `nokari/settings.py`:**
    *   Ensure `SECRET_KEY` is loaded from environment variables and not hardcoded.
    *   Ensure `DEBUG` is set to `False` in production.
    *   Configure `ALLOWED_HOSTS` properly.
    *   Review middleware for security best practices.

### 1.4. Harden Docker Images

**Goal:** Improve the security of the Docker images.

**Plan:**
1.  **Run as Non-Root User:**
    *   Update `Dockerfile.backend` and `frontend/Dockerfile` to create and use a non-root user.
2.  **Multi-Stage Builds:**
    *   Refactor the Dockerfiles to use multi-stage builds to reduce the size and attack surface of the final images.

### 1.5. Fix Frontend Directory Structure

**Goal:** Rebuild the frontend directory to follow a standard React project structure, enabling proper dependency management and vulnerability scanning.

**Problem:** The `frontend` directory has a deeply nested and corrupted structure (e.g., `frontend/frontend/frontend/...`), which prevents `npm` commands from running correctly.

**Plan:**
1.  **Create a new React application:**
    *   `npx create-react-app temp-frontend`
2.  **Copy existing source code:**
    *   `cp -R frontend/src/* temp-frontend/src/`
    *   `cp -R frontend/public/* temp-frontend/public/`
3.  **Copy other essential files:**
    *   Copy any other necessary files, such as `.gitignore`, `nginx.conf`, and `Dockerfile`, into the `temp-frontend` directory.
4.  **Replace the old `frontend` directory:**
    *   `rm -rf frontend`
    *   `mv temp-frontend frontend`
5.  **Re-run security checks:**
    *   `cd frontend && npm audit`

---

## Phase 2: Reliability Enhancements (Medium Priority)

### 2.1. Expand Test Coverage

**Goal:** Increase confidence in code quality and prevent regressions by adding comprehensive tests.

**Plan:**
*   Follow the detailed plan in the original `REFACTOR.md` to add unit and integration tests for the backend and frontend, aiming for at least 80% coverage.

### 2.2. Implement Health Checks

**Goal:** Improve the resilience of the application by adding health checks to the services.

**Plan:**
1.  **Add a health check endpoint to the Django application.**
2.  **Add a `healthcheck` to the `backend` service in `docker-compose.yml`.**

### 2.3. Improve Logging

**Goal:** Implement a more robust logging solution to facilitate debugging and monitoring.

**Plan:**
1.  **Configure Django's logging framework in `nokari/settings.py` to output structured logs.**
2.  **Consider sending logs to a centralized logging service in a production environment.**

---

## Phase 3: Maintainability Improvements (Low Priority)

### 3.1. Enhance CI/CD Pipeline

**Goal:** Automate quality checks and streamline the development process.

**Plan:**
1.  **Add linting and testing stages to the CI/CD workflows for both backend and frontend.**
2.  **Consolidate Docker build and push steps into a single workflow.**

### 3.2. Add Project Documentation

**Goal:** Improve project maintainability by creating comprehensive documentation.

**Plan:**
*   Follow the detailed plan in the original `REFACTOR.md` to set up `mkdocs` and create initial documentation.

### 3.3. Automate Dependency Updates

**Goal:** Keep dependencies up-to-date automatically.

**Plan:**
*   Follow the detailed plan in the original `REFACTOR.md` to set up Dependabot.
