# Nokari Refactoring and Improvement Plan

This document outlines a prioritized plan for refactoring and improving the Nokari application. The tasks are ordered by priority, addressing security, reliability, and maintainability.

---

## Priority 1: Critical Security Vulnerabilities

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
