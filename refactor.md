# Refactoring and Performance Improvements

This document tracks the ongoing refactoring and performance improvement tasks for the application.

## Frontend

- [ ] **Memoization:**
  - [ ] Use `useCallback` for handler functions in `App.jsx`, `Dashboard.jsx`, and `Jobs.jsx`.
  - [ ] Use `React.memo` for pure components like `Jobs`, `JobTitles`, etc.
- [ ] **Debouncing:**
  - [ ] Debounce the search/filter inputs in the `Jobs` component to avoid excessive API calls.
- [ ] **Optimistic UI Updates:**
  - [ ] Implement optimistic UI updates for pinning jobs to provide a faster user experience.
- [ ] **"Find Similar" Button:**
  - [ ] The "find similar" button is not working correctly. This needs to be investigated and fixed.

## Backend

- [ ] **Asynchronous Tasks:**
  - [ ] Move the job scraping logic to a background task queue (e.g., Celery).
  - [ ] Move the resume matching logic to a background task.
- [ ] **Database Indexing:**
  - [ ] Add database indexes to frequently queried fields in the `JobPosting` and `HiddenCompany` models.
- [ ] **Primary Key:**
  - [ ] Change the primary key of the `JobPosting` model from a URL to an auto-incrementing integer.
- [ ] **Query Optimization:**
  - [ ] Review and optimize database queries, looking for N+1 problems.
