# Refactoring and Improvement Plan

This document outlines potential future improvements for the project, broken down into actionable plans that can be executed by an AI agent.

---

## 1. Expand Test Coverage

**Goal:** Increase confidence in code quality and prevent regressions by adding comprehensive unit and integration tests for the backend and frontend, aiming for at least 80% code coverage as per `AGENTS.md`.

### Backend Plan (Django/Pytest)
1.  **Analyze Application:**
    *   **Action:** Use `ls -R app/` to list all files in the Django application.
    *   **Action:** Read `app/models.py`, `app/views.py`, `app/serializers.py`, and `app/urls.py` to identify key business logic, models, and API endpoints.
    *   **Goal:** Create a list of test cases covering all public functions and API endpoints.

2.  **Configure Test Suite:**
    *   **Action:** Create a `pytest.ini` file in the root directory.
    *   **Content:**
        ```ini
        [pytest]
        DJANGO_SETTINGS_MODULE = nokari.settings
        python_files = tests.py test_*.py *_tests.py
        ```
    *   **Action:** Add `pytest-django` and `coverage` to `requirements_dev.txt`.

3.  **Write Model Tests:**
    *   **Action:** Create `app/core/tests/test_models.py`.
    *   **Implementation:** For each model in `app/core/models.py`, write a `TestCase` that validates all fields, properties, and custom methods. Ensure model instances can be created, saved, and deleted successfully.

4.  **Write API Tests:**
    *   **Action:** Create `app/core/tests/test_views.py`.
    *   **Implementation:** Use Django REST Framework's `APITestCase`. For each endpoint in `app/core/urls.py`, write tests that cover:
        *   GET, POST, PUT, DELETE methods as appropriate.
        *   Successful responses (200, 201, 204 status codes).
        *   Authentication and permission checks (401, 403 status codes).
        *   Invalid input and error handling (400, 404 status codes).

5.  **Integrate Code Coverage:**
    *   **Action:** Modify the `pytest` command in the `.github/workflows/python-lint.yaml` workflow.
    *   **Change:**
        ```yaml
        # From:
        run: pytest
        # To:
        run: |
          pip install coverage
          coverage run -m pytest
          coverage report --fail-under=80
        ```
    *   **(Optional) Action:** Add a step to upload the coverage report.
        ```yaml
        - name: Upload coverage to Codecov
          uses: codecov/codecov-action@v3
          with:
            token: ${{ secrets.CODECOV_TOKEN }}
        ```

### Frontend Plan (React/Jest)
1.  **Configure Coverage:**
    *   **Action:** Modify the `test` script in `frontend/package.json`.
    *   **Change:**
        ```json
        "test": "react-scripts test --coverage --watchAll=false"
        ```
    *   **Action:** Add a `jest` block to `frontend/package.json` to enforce coverage.
        ```json
        "jest": {
          "coverageThreshold": {
            "global": {
              "branches": 80,
              "functions": 80,
              "lines": 80,
              "statements": 80
            }
          }
        }
        ```

2.  **Write Component Tests:**
    *   **Action:** For each component in `frontend/src/components`, create a corresponding `*.test.js` file.
    *   **Implementation:** Use `@testing-library/react` to render the component and assert that it displays correctly with various props. Simulate user events (`userEvent.click`, `userEvent.type`) to test interactivity.

3.  **Create Frontend CI Workflow:**
    *   **Action:** Create a new file `.github/workflows/frontend-ci.yaml`.
    *   **Content:**
        ```yaml
        name: Frontend CI
        on:
          push:
            branches: [ main ]
          pull_request:
            branches: [ main ]
        jobs:
          test:
            runs-on: ubuntu-latest
            defaults:
              run:
                working-directory: ./frontend
            steps:
              - uses: actions/checkout@v3
              - name: Use Node.js 18
                uses: actions/setup-node@v3
                with:
                  node-version: 18
              - run: npm ci
              - run: npm test
        ```

---

## 2. Add Project Documentation

**Goal:** Improve project maintainability and make it easier for new contributors to get started by creating and deploying comprehensive documentation using MkDocs.

### Plan
1.  **Add Dependencies:**
    *   **Action:** Add `mkdocs` and `mkdocs-material` to `requirements_dev.txt`.

2.  **Create `docs/` Directory and Content:**
    *   **Action:** `mkdir docs`
    *   **Action:** Create the following files with placeholder content:
        *   `docs/index.md` (Project overview)
        *   `docs/development-setup.md` (How to set up the local environment)
        *   `docs/architecture.md` (High-level architecture overview)

3.  **Configure MkDocs:**
    *   **Action:** Create `mkdocs.yml` in the root directory.
    *   **Content:**
        ```yaml
        site_name: Nokari Project
        theme:
          name: material
        nav:
          - 'Overview': 'index.md'
          - 'Development Setup': 'development-setup.md'
          - 'Architecture': 'architecture.md'
        ```

4.  **Create Deployment Workflow:**
    *   **Action:** Create `.github/workflows/mkdocs-deploy.yaml`.
    *   **Content:**
        ```yaml
        name: Deploy Documentation
        on:
          push:
            branches:
              - main
        jobs:
          deploy:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v3
              - name: Set up Python
                uses: actions/setup-python@v4
                with:
                  python-version: 3.9
              - name: Install dependencies
                run: pip install -r requirements_dev.txt
              - name: Deploy to GitHub Pages
                run: mkdocs gh-deploy --force
        ```

---

## 3. Enhance Docker Workflow

**Goal:** Improve consistency between environments and optimize Docker images.

### Plan
1.  **Optimize with Multi-Stage Builds:**
    *   **Action:** Refactor `Dockerfile.backend` to use a `builder` stage for installing dependencies and a slim final stage for the runtime.
    *   **Action:** Refactor `frontend/Dockerfile` to use a `node` stage for `npm run build` and a final `nginx` stage to serve the static files.

2.  **Integrate Testing into Docker:**
    *   **Action:** Add a `test` service to `docker-compose.yml`.
    *   **Implementation:** The service will use the backend Dockerfile, but override the command to run `pytest`.
        ```yaml
        services:
          # ... other services
          backend-tests:
            build:
              context: .
              dockerfile: Dockerfile.backend
            command: ["pytest"]
            # ... env vars and volumes
        ```

3.  **Enable Live-Reloading:**
    *   **Action:** Modify the `backend` and `frontend` services in `docker-compose.yml`.
    *   **Implementation:** Add volume mounts to map the host source code directories to the container directories.
        ```yaml
        volumes:
          - .:/app  # For backend
          - ./frontend:/app/frontend # For frontend
        ```

---

## 4. Automate Dependency Updates

**Goal:** Enhance security and maintenance by automatically keeping dependencies up-to-date using Dependabot.

### Plan
1.  **Create Dependabot Config:**
    *   **Action:** Create the file `.github/dependabot.yml`.
    *   **Content:**
        ```yaml
        version: 2
        updates:
          # Python dependencies
          - package-ecosystem: "pip"
            directory: "/"
            schedule:
              interval: "weekly"
            target-branch: "main"
          # Frontend dependencies
          - package-ecosystem: "npm"
            directory: "/frontend"
            schedule:
              interval: "weekly"
            target-branch: "main"
        ```
2.  **Commit and Activate:**
    *   **Action:** Add, commit, and push the `.github/dependabot.yml` file to the `main` branch. Dependabot will be activated automatically.
