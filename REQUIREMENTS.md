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
*   ...be able to find jobs similar to one I'm interested in, so I can discover more relevant opportunities.

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

### 8.3. Find Similar Jobs Feature

#### 8.3.1. User Experience

*   **Trigger:** A "Find similar" button or link will be displayed on each job posting card.
*   **Interaction:**
    *   When a user clicks the "Find similar" button, the main job list will be updated to show only jobs that are similar to the selected one.
    *   A clear heading, such as "Jobs similar to [Original Job Title]", will be displayed above the results.
    *   A loading indicator will be shown while the search is in progress.
*   **Display:** The similar jobs will be ranked by their similarity score, with the most similar jobs appearing first.

#### 8.3.2. Similarity Engine (MVP)

For the initial implementation (MVP), similarity will be determined based on the following factors:

*   **Job Title:** Matching keywords and phrases in the job title.
*   **Key Skills:** Automatically extracting key skills and technologies from the job description (e.g., "Python", "React", "Project Management") and finding other jobs that mention the same skills.

#### 8.3.3. Future Enhancements (Post-MVP)

*   **Semantic Understanding:** Enhance the similarity model using advanced NLP techniques (e.g., document embeddings) to understand the meaning and context of the job description, not just keywords.
*   **Company & Industry:** Factor in the company's industry, size, and reputation to improve similarity matching.
*   **User Feedback:** Introduce a mechanism for users to provide feedback on the similarity results (e.g., "This job is not similar"), which can be used to fine-tune the model over time.

## 9. New User Requirements

### 9.1. Admin functionality
*   Move the admin tools to an admin-only page, whose link is visible only for logged-in admins.
*   Move the scrape function into a menu that is only visible for logged-in admins.
*   Add a users view that is only visible for logged-in admins from the admin menu.
*   Allow admins to promote regular users to admins.
*   For the admin, add a configurable window of time for job scraping, e.g. 7 days, 30 days, etc.

### 9.2. Job Card UI
*   Update the detail information for each card. From top to bottom, these are the fields:
    *   pin icon (upper left)
    *   three dot menu (upper right)
    *   job title (largest font)
    *   company (smaller font) with hide company button
    *   location (smaller font), including the onsite / hybrid / remote badges
    *   job summary
    *   job posting date (smallest font)
*   Ensure that the full product color scheme is being used.

### 9.3. Job filtering and search
*   Make the job postings filter section collapsible.
*   Improve the searching to filter out batch pages like "Jobs at Garner Health" or "Careers - Imbuit" and instead link to the job listings on those pages.
*   Filter "Job Application for" out of the job title.

### 9.4. Job Card Enhancements
*   Scan each job posting for the type of work that is included (Hybrid, Onsite and / or Remote).
*   If none are specified, assume Onsite.
*   Each job card should have one or more badges showing the type of work (Hybrid, Onsite or Remote) that the job posting allows.
*   Each job card should show the location of the job (city, state, country, etc.)
*   Each job card should show the company name and a "Hide" icon next to it that allows the user to hide the company from future searches.
