# Product Requirements: nokari
## 1. Vision

To provide a simple way of finding jobs and helping to tailor the resume and cover letter for chosen roles.

## 2. Goals

*   **Primary Goal:** To help the user find relevant roles in their chosen industry.

## 3. User Stories

### 3.1. As a new user, I want to...

*   ...be able to create an account easily so that I can access the application's features.
*   ...be able to log in securely to my account.

### 3.2. As a logged-in user, I want to...

*   ...be able to save one or more resumes as part of my account.
*   ...be able to save one or more cover letters as part of my account.
*   ...be able to see a list of open roles and companies that match my current resume.
*   ...be able to filter the roles by company.
*   ...be able to filter the roles by job title.
*   ...be able to click and see a quick preview of the role.
*   ...be able to click to open roles in a new window so that I can review them. 
*   ...be able to see a level of confidence that my resume matches the role.
*   ...be able to refresh the list of web scraping results. 
*   ...be able to generate an updated resume based on a job posting.
*   ...be able to generate an updated cover letter based on a job posting.
*   ...be able to change my password securely.

### 3.3 As a system administrator, I want to...
*   ...be able to see administrative options that are not available to non-adminstrator users.
*   ...be able to add new domains for scraping job roles.
*   ...be able to see statistics for job matching.

## 4. Non-Functional Requirements

### 4.1. Performance

*   The application should load quickly and respond to user input within a reasonable timeframe.

### 4.2. Security

*   User passwords must be stored securely using modern hashing techniques.
*   The application should be protected against common web vulnerabilities (e.g., XSS, CSRF).
*   User data should be handled with care to ensure privacy.

### 4.3. Usability

*   The user interface should be intuitive and easy to navigate.
*   The application should be accessible to users with disabilities.
*   The application should be responsive and work well on different screen sizes.

### 4.4. Reliability

*   The application should be available and functioning correctly with minimal downtime.

## 5. Future Features

*   TBD

## 7. Development Requirements

### 7.1. CI/CD

*   A CI/CD pipeline should be established to automate testing and deployment.
*   Every commit to the main branch should trigger a build and run the test suite.
*   Automated deployments to a staging environment should be configured for pull requests.
*   Production deployments should be manual, triggered by a release tag.

### 7.2. Security

*   Regular security scans should be performed on the codebase to identify vulnerabilities.
*   Dependencies should be kept up-to-date to avoid known vulnerabilities.
*   The principle of least privilege should be applied to all system components.

### 7.3. Code Quality

*   The codebase should adhere to the PEP 8 style guide for Python.
*   Code should be well-documented with comments and docstrings.
*   A linter (e.g., Flake8) should be used to enforce code quality standards.
*   All new features should be accompanied by unit tests.
