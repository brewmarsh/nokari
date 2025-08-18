### User Interface Requirements

---

### User Interface Requirements

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

### **Geolocation & Proximity Requirements**

* The platform will include a **map-based search interface** that shows job postings as interactive pins.
* Users can filter jobs by a **"commute time"** (e.g., 30-minute drive, transit, or bike ride) from a user-specified address.
* Job postings must be clearly distinguished by their work arrangement. Each job card and search result will display a **visual badge** that indicates if the role is:
    * **Remote:** A green badge.
    * **Hybrid:** A blue badge.
    * **Onsite:** A gray badge.
* For hybrid roles, the job posting details must specify the number of required days in the office and the office location.
* The platform will **remember a user's preferred work arrangement** and prioritize those job types in search results and email alerts.
* 
### 1. Enhanced Search & Discovery

* **Advanced Search Filters:** Implement detailed filters beyond the basics, including:
    * Salary range
    * Experience level (e.g., Entry, Mid-level, Senior, Executive)
    * Job type (e.g., Full-time, Part-time, Contract, Internship)
    * Company size and industry
    * Specific required and desired skills (e.g., Python, SQL, Project Management)
* **Saved Searches & Job Alerts:** Users must be able to save specific search queries. They should then have the option to receive real-time email or push notifications when a new job matching their saved criteria is posted. This reduces the need for users to constantly check the site.
* **Geolocation & Proximity Search:** Integrate a mapping feature that allows users to search for jobs within a specific radius of their current location or a specified address.

### 2. User Profile & Application Management

* **Comprehensive User Profiles:** Allow users to build a complete profile that includes not just their resume but also a professional headshot, a personal summary, links to a portfolio or LinkedIn profile, and a list of their skills and certifications.
* **Application History Dashboard:** Provide a centralized dashboard where users can track the status of all their applications (e.g., "Applied," "Viewed by Company," "Interview Scheduled," "Rejected"). This provides clarity and reduces user anxiety.
* **One-Click Application:** For jobs that don't redirect to an external site, users should be able to apply with a single click using their saved profile and resume.

### 3. Personalization & Recommendations

* **Algorithmic Job Recommendations:** Implement a recommendation engine that suggests jobs to users based on their profile data, browsing history, saved jobs, and application patterns. This helps surface relevant opportunities they might not have found through a standard search.
* **Skills-Based Matching:** Use machine learning to match a user's skills directly with the skills listed in a job description, showing a percentage match score on the job card.

### 4. Company & Employer Features

* **Detailed Company Profiles:** Every company with an active job posting should have a profile page that includes:
    * A company description and mission statement.
    * Information about company culture, benefits, and perks.
    * Photos or videos of the office environment.
    * An optional integration for employee reviews (e.g., a link to Glassdoor).
* **In-App Employer Communication:** Provide a secure messaging system that allows employers to directly contact candidates who have applied for their jobs. This streamlines the initial screening process without requiring either party to share personal contact information.

### 5. Content & Resources

* **Career Advice Blog:** A dedicated section with high-quality content, such as resume writing tips, interview preparation guides, salary negotiation advice, and industry insights. This establishes the website as a valuable resource, not just a job board.
* **Community Forums/Q&A:** A place where users can ask questions and share advice with other job seekers and professionals.

### 6. Technical & Accessibility

* **WCAG 2.1 Compliance:** Ensure the entire platform adheres to the Web Content Accessibility Guidelines (WCAG) to make it usable by people with disabilities. This includes proper color contrast, keyboard navigation, and screen reader compatibility.
* **Mobile-First Design:** All UI/UX design and development should prioritize a seamless and complete experience on mobile devices, as a large percentage of users will be accessing the site from their phones.
