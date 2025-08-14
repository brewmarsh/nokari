# Refactoring and Improvement Plan

This document outlines potential future improvements for the project, broken down into actionable plans that can be executed by an AI agent. The tasks are prioritized based on their impact on the project's security, reliability, and maintainability.

---

## Prioritization

The refactoring tasks are prioritized as follows:
1.  **Security:** Addressing security vulnerabilities and hardening the application is the highest priority.
2.  **Reliability:** Ensuring the application is stable, resilient, and performs as expected.
3.  **Maintainability:** Improving the codebase, documentation, and development processes to make the project easier to manage and extend.

---

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
