# End-to-End (E2E) Test Cases

This document outlines the end-to-end test cases for the application.

## P0: Critical Path

- [ ] **First User Onboarding:**
  - **Scenario:** A new user visits the application when there are no existing users.
  - **Steps:**
    1. Navigate to the application's root URL.
    2. Should be redirected to the `/onboarding` page.
    3. Fill out the onboarding form with valid details and submit.
    4. Should be redirected to the `/dashboard`.
    5. The new user should have the 'admin' role.
- [ ] **Successful Login:**
  - **Scenario:** An existing user logs into the application.
  - **Steps:**
    1. Navigate to the `/login` page.
    2. Enter valid credentials for an existing user.
    3. Click the "Login" button.
    4. Should be redirected to the `/dashboard`.
- [ ] **View Jobs:**
  - **Scenario:** A logged-in user views the job postings on the dashboard.
  - **Steps:**
    1. Log in as a regular user.
    2. Navigate to the `/dashboard`.
    3. A list of job postings should be visible.

## P1: Important Functionality

- [ ] **User Registration:**
  - **Scenario:** A new user registers for an account when other users already exist.
  - **Steps:**
    1. Navigate to the `/register` page.
    2. Fill out the registration form with valid details and submit.
    3. Should be redirected to the `/login` page or automatically logged in and redirected to the dashboard.
- [ ] **Logout:**
  - **Scenario:** A logged-in user logs out of the application.
  - **Steps:**
    1. Log in to the application.
    2. Click the "Logout" button (Note: This button doesn't exist yet, I'll need to add it).
    3. Should be redirected to the `/login` page.
- [ ] **Filter and Search Jobs:**
  - **Scenario:** A user filters and searches for jobs on the dashboard.
  - **Steps:**
    1. Log in and navigate to the dashboard.
    2. Enter text into the "Filter by title" input. The job list should update.
    3. Enter text into the "Filter by company" input. The job list should update.
    4. Enter text into the "Search by keyword" input. The job list should update.
- [ ] **Pin/Unpin Job:**
  - **Scenario:** A user pins and unpins a job.
  - **Steps:**
    1. Log in and navigate to the dashboard.
    2. Click the "Pin" icon on a job card.
    3. The job card should be visually highlighted as pinned.
    4. Click the "Pin" icon again.
    5. The visual highlight should be removed.
- [ ] **Hide Job:**
  - **Scenario:** A user hides a job.
  - **Steps:**
    1. Log in and navigate to the dashboard.
    2. Click the "Hide" icon on a job card.
    3. The job card should be removed from the list.
- [ ] **Hide Company:**
  - **Scenario:** A user hides a company.
  - **Steps:**
    1. Log in and navigate to the dashboard.
    2. Click the "Hide Company" button on a job card.
    3. All jobs from that company should be removed from the list.
- [ ] **Admin View:**
  - **Scenario:** Verify that admin tools are only visible to admin users.
  - **Steps:**
    1. Log in as an admin user. The "Admin Tools" section should be visible on the dashboard.
    2. Log out and log in as a regular user. The "Admin Tools" section should not be visible.

## P2: Less Critical / Admin

- [ ] **Failed Login:**
  - **Scenario:** A user tries to log in with invalid credentials.
  - **Steps:**
    1. Navigate to the `/login` page.
    2. Enter invalid credentials.
    3. Click the "Login" button.
    4. An error message should be displayed.
- [ ] **Scrape Jobs:**
  - **Scenario:** An admin user triggers a job scrape.
  - **Steps:**
    1. Log in as an admin user.
    2. Click the "Scrape Jobs" button.
    3. A status message should be displayed indicating that the scrape has started.
- [ ] **Manage Job Titles:**
  - **Scenario:** An admin user adds and deletes a searchable job title.
  - **Steps:**
    1. Log in as an admin user.
    2. In the "Admin Tools" section, enter a new job title and click "Add".
    3. The new title should appear in the list.
    4. Click the "Delete" button next to the new title.
    5. The title should be removed from the list.
- [ ] **Manage Scrapable Domains:**
  - **Scenario:** An admin user adds a scrapable domain.
  - **Steps:**
    1. Log in as an admin user.
    2. In the "Admin Tools" section, enter a new domain and click "Add".
    3. The new domain should appear in the list.
