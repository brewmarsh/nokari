# Code Refactoring and Improvement Report

This document outlines a plan for refactoring and improving the codebase. The following sections detail identified issues and suggest improvements for the backend and frontend, as well as cross-cutting concerns.

## Proposed Refactoring Plan

The refactoring will be done in the following order:

1.  **Stabilize the Backend:**
    *   Address the critical `match_resume` bug.
    *   Fix the `JobPostingView` performance issue.
2.  **Improve Backend Modularity:**
    *   Refactor the scraping and ML utility code.
    *   Replace `threading` with a proper task queue.
3.  **Clean Up the Backend:**
    *   Remove the security vulnerability in `UserSerializer`.
    *   Remove dead code and clean up imports.
4.  **Refactor the Frontend:**
    *   Break down the `Jobs.jsx` monolith.
    *   Improve code style by moving icons and styles to separate files.
5.  **Improve Frontend Performance and UX:**
    *   Implement optimistic UI updates.
    *   Clean up `api.js` and logging.
6.  **Enhance Scraper Reliability:**
    *   Investigate and implement more robust scraping methods.

---

## Current Refactoring Task: Integrate Celery for Background Tasks

The goal of this task is to replace the current `threading`-based background tasks with a robust and scalable task queue using Celery and Redis. This will improve the reliability and performance of the application and enhance modularity by separating background work from the web request-response cycle.

### Detailed Plan:

1.  **Integrate Celery and Redis**:
    *   Add `celery` and `redis` packages to `requirements.txt`.
    *   Create a `celery.py` module to define the Celery application instance.
    *   Configure Celery within the Django settings (`nokari/settings.py`).
    *   Update `docker-compose.yml` to include a `redis` service for the message broker and a `celery-worker` service to run the tasks.
2.  **Create a Celery Task for Scraping**:
    *   Create a new `app/core/tasks.py` module.
    *   Define a Celery task in this file that encapsulates the background scraping logic, currently in `scrape_in_background` in `views.py`.
3.  **Refactor `FindSimilarJobsView` to Use the Celery Task**:
    *   Modify the `FindSimilarJobsView` in `app/core/views.py`.
    *   Replace the `threading.Thread` implementation with a call to the new Celery task using `.delay()`.
    *   Remove the old `scrape_in_background` function.
4.  **Submit the refactoring.**
    *   Once the integration is complete and verified, commit the changes.

---

## Backend Refactoring Details

### 1. Critical Bug: Missing `match_resume` Function

*   **Issue:** The `JobPostingView` in `app/core/views.py` calls a function `match_resume` that is not defined or imported, which will cause the application to crash.
*   **Recommendation:**
    *   Locate the intended `match_resume` function or implement it if it was never written. Given its name, it's likely a text-matching or ML function.
    *   If the feature is not ready, comment out the code that calls it to prevent crashes.

### 2. Performance: Inefficient `JobPostingView`

*   **Issue:** The `JobPostingView` calculates a `confidence_score` for every job on every request. This is highly inefficient and will lead to slow response times and high database load.
*   **Recommendation:**
    *   Move the `confidence_score` calculation to an asynchronous background task.
    *   The calculation should be triggered when a user's resume is uploaded or updated, or when a new job is scraped, not during a `GET` request.

### 3. Modularity and Duplication

*   **Issue:**
    *   Scraping logic is duplicated in `ScrapeView` and the `scrape_in_background` function in `app/core/views.py`.
    *   The `generate_embedding` function is located in `views.py`, but it's a utility function.
    *   The `sentence-transformers` model is loaded at the module level in `views.py`, impacting startup time and modularity.
*   **Recommendation:**
    *   Create a new module `app/core/scraping_logic.py` and move all scraping-related functions into it.
    *   Create a new module `app/core/ml_utils.py` and move `generate_embedding` and the model loading logic into it. The model should be loaded on demand if possible.

### 4. Reliability

*   **Issue:**
    *   Background tasks are run using Python's `threading` module, which is not ideal for a production Django application.
    *   Exception handling in the scraper is too broad (`except Exception as e:`).
*   **Recommendation:**
    *   Replace `threading` with a proper task queue like Celery with Redis or RabbitMQ.
    *   Use more specific exception handling in the scraper to provide better error logging and debugging.

### 5. Security

*   **Issue:** The `UserSerializer` allows creating superusers via an API endpoint.
*   **Recommendation:** Remove this functionality. Superuser creation should be handled exclusively through the `createsuperuser` management command.

### 6. Code Cleanliness

*   **Issue:**
    *   The `test_page` view in `app/core/views.py` appears to be unused.
    *   There is a duplicate `numpy` import in `app/core/views.py`.
*   **Recommendation:**
    *   Remove the `test_page` view and its corresponding URL pattern.
    *   Remove the duplicate import.

## Frontend Refactoring

### 1. Component Architecture

*   **Issue:** The `Jobs.jsx` component is a large, monolithic component that handles too much state and logic.
*   **Recommendation:**
    *   Break down `Jobs.jsx` into smaller, more manageable components. For example, create a `JobCard.jsx`, `JobFilters.jsx`, and `ActionMenu.jsx`.
    *   Consider using a state management library like Zustand or Redux Toolkit to manage shared state, especially if the application is expected to grow.

### 2. Code Duplication and Style

*   **Issue:**
    *   SVG icons are defined as components directly within `Jobs.jsx`, and the `HideIcon` is duplicated.
    *   There is a heavy reliance on inline styles.
*   **Recommendation:**
    *   Move SVG icon components to their own files in a `components/icons` directory.
    *   Move all inline styles to their corresponding CSS files (`Jobs.css`, etc.) to improve maintainability and reusability.

### 3. API and State Management

*   **Issue:**
    *   The `axios` configuration in `services/api.js` has some duplication.
    *   Some UI updates (like pinning a job) trigger a full refetch of all jobs, which is inefficient.
*   **Recommendation:**
    *   Refactor the `axios` configuration to avoid duplication.
    *   Implement optimistic UI updates for actions like pinning, hiding, etc. The UI should update immediately, and then be reverted if the API call fails.

### 4. Code Cleanliness

*   **Issue:** There are numerous `console.log` statements throughout the code.
*   **Recommendation:** Remove `console.log` statements or replace them with a proper logging framework for production builds.

## Cross-cutting Concerns

### 1. Scraper Reliability

*   **Issue:** The scraper relies on heuristics to parse information from Google search results, which is fragile and can break if the structure of the search results changes.
*   **Recommendation:**
    *   For each `ScrapableDomain`, investigate if they provide a more direct API for job postings.
    *   Implement more robust parsing logic with better error handling and logging to identify when a scraper for a specific domain breaks.
