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

*   Users can upload multiple resumes and cover letters.
*   Users can choose a default resume and cover letter.
*   Users can delete resumes and cover letters.

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

### 7.4. Environment

*   The version of `npm` should be updated to the latest version.
*   The application should be containerized using Docker.

## 8. New Requirements

### 8.1. User Interface Requirements

---

#### **Brand Colors**

* **Primary Blue:** `#2F4C82` (Trust, Professionalism)
* **Secondary Green:** `#4CAF50` (Growth, Success)
* **Accent Orange:** `#FF9800` (Energy, Motivation)
* **Neutral Gray:** `#607D8B` (Balance, Seriousness)
* **Light Gray/White:** `#EFEFEF` (Cleanliness, Readability)

---

#### **Job Posting Card**

* Each Job Posting card must display a single **Pin/Unpin toggle icon** in the top left corner.
    * The icon should be an outline when the job is not pinned and a solid fill when the job is pinned.
    * Clicking the solid icon will unpin the job, returning it to its original position in the list.
    * Clicking the outline icon will pin the job to the top of the list.
* The card must include a **three-dot action menu** (`...`) in the top right corner.
    * This menu will contain a "Hide Job" action.
* The **Company Name** will be displayed below the Job Posting title.
* The **Remote icon** will be displayed to the right of the job's location, using the Neutral Gray color (`#607D8B`).

---

#### **Top Navigation Menu**

* When a user is logged in, the top menu will show a **Dashboard link** and a **user profile icon** that, when clicked, opens a dropdown menu containing **Profile, Settings, and Logout** links.
* When a user is not logged in, the top menu will display a **Login link** and a visually distinct **Register button** using the Accent Orange color (`#FF9800`).

---

#### **Admin User Interface**

* On the **Job Titles list** and the **Scrapable Domains list**, a **Delete icon** will appear to the right of each item.
    * The Delete icon should be colored red to signify a destructive action.
    * Clicking the Delete icon will trigger a **confirmation pop-up** that requires the user to confirm the action before the item is permanently deleted.

---

### 8.2. **Geolocation & Proximity Requirements**

* The platform will include a **map-based search interface** that shows job postings as interactive pins.
* Users can filter jobs by a **"commute time"** (e.g., 30-minute drive, transit, or bike ride) from a user-specified address.
* Job postings must be clearly distinguished by their work arrangement. Each job card and search result will display a **visual badge** that indicates if the role is:
    * **Remote:** A green badge.
    * **Hybrid:** A blue badge.
    * **Onsite:** A gray badge.
* For hybrid roles, the job posting details must specify the number of required days in the office and the office location.
* The platform will **remember a user's preferred work arrangement** and prioritize those job types in search results and email alerts.
