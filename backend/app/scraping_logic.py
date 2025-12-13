import logging
import os
import uuid
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

from backend.app.firestore_repo import FirestoreRepo

logger = logging.getLogger(__name__)


class ScraperException(Exception):
    pass


def scrape_job_details(url):
    """
    Scrapes the details of a single job posting from its URL.
    Returns a dictionary with the scraped data.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        details = {}
        # Title
        details["title"] = soup.title.string if soup.title else ""
        # Description
        # This is a generic attempt to get the main content.
        # A more robust solution would have parsers for specific site structures.
        main_content = soup.find("main") or soup.find("article") or soup.find("body")
        if main_content:
            details["description"] = " ".join(main_content.get_text().split())
        else:
            details["description"] = ""

        return details
    except requests.RequestException as e:
        logger.warning(f"Could not fetch URL {url}: {e}")
        return None


def scrape_jobs(query, domain, days=None):
    """
    Scrapes job postings from a given domain using the Google Custom Search API.

    Args:
        query (str): The search query for job titles.
        domain (str): The domain to search within (e.g., "lever.co").
        days (int, optional): The number of past days to restrict the search to.

    Returns:
        list: A list of dictionaries, where each dictionary represents a job posting.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    search_engine_id = os.environ.get("CUSTOM_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        logger.warning("GOOGLE_API_KEY and CUSTOM_SEARCH_ENGINE_ID must be set.")
        # Return empty list instead of raising to avoid crashing the whole loop
        return []

    try:
        service = build("customsearch", "v1", developerKey=api_key)

        search_query = f'{query} -intitle:"jobs at" -intitle:"careers" site:{domain}'

        search_args = {
            "q": search_query,
            "cx": search_engine_id,
            "num": 10,
        }

        if days:
            search_args["dateRestrict"] = f"d{days}"

        result = service.cse().list(**search_args).execute()
    except Exception as e:
        logger.error(f"Error executing Google Custom Search: {e}")
        return []

    jobs = []
    if "items" in result:
        for item in result["items"]:
            pagemap = item.get("pagemap", {})
            metatags = pagemap.get("metatags", [{}])[0]
            title = item.get("title", "")
            description = item.get("snippet", "")
            full_text = f"{title.lower()} {description.lower()}"

            # Process locations
            locations = []
            location_string = metatags.get("joblocation")

            is_remote = "remote" in full_text
            is_hybrid = "hybrid" in full_text
            is_onsite = "onsite" in full_text

            if is_remote:
                locations.append({"type": "remote"})
            if is_hybrid:
                locations.append(
                    {"type": "hybrid", "location_string": location_string or ""}
                )
            if is_onsite:
                locations.append(
                    {"type": "onsite", "location_string": location_string or ""}
                )

            if not locations:
                locations.append(
                    {"type": "onsite", "location_string": location_string or ""}
                )

            # Try to find a date in the metatags
            posting_date_str = (
                metatags.get("pubdate")
                or metatags.get("date")
                or metatags.get("publishdate")
            )
            posting_date = None
            if posting_date_str:
                try:
                    posting_date = datetime.strptime(
                        posting_date_str, "%Y-%m-%d"
                    )
                except (ValueError, TypeError):
                    pass  # Keep as None if parsing fails

            job_data = {
                "title": title,
                "link": item.get("link"),
                "company": metatags.get("og:site_name", "")
                or pagemap.get("cse_thumbnail", [{}])[0].get("src", "")
                or domain.split('.')[0], # Fallback to domain name
                "description": description,
                "locations": locations,
                "posting_date": posting_date,
            }

            # Scrape the actual job page for more details
            if job_data["link"]:
                scraped_details = scrape_job_details(job_data["link"])
                if scraped_details:
                    # Override the initial data with more accurate scraped data
                    job_data["title"] = (
                        scraped_details.get("title") or job_data["title"]
                    )
                    job_data["description"] = (
                        scraped_details.get("description") or job_data["description"]
                    )

            jobs.append(job_data)
    return jobs


def scrape_and_save_jobs(repo: FirestoreRepo, query_term: str, domains, days=None):
    """
    Scrapes jobs from a list of domains and saves new jobs to the database.

    Args:
        repo (FirestoreRepo): The repository to save jobs to.
        query_term (str): The search query for job titles.
        domains (list): A list of dictionaries (from Firestore) or strings.
        days (int, optional): The number of past days to restrict the search to.

    Returns:
        int: The number of new jobs that were scraped and saved.
    """
    scraped_count = 0
    for domain_obj in domains:
        domain_name = (
            domain_obj["domain"] if isinstance(domain_obj, dict) and "domain" in domain_obj else domain_obj
        )
        try:
            logger.info(f"Scraping {domain_name} for {query_term}...")
            jobs = scrape_jobs(query_term, domain_name, days=days)
            for job_data in jobs:
                title = job_data["title"]
                if "Job Application for" in title:
                    title = title.replace("Job Application for", "").strip()

                # Generate a job ID based on the link (deterministic)
                # Or query if it exists by link.
                # Firestore query for link?
                # The repo doesn't support get_by_link easily without index/loop.
                # But we can use URL as ID (encoded) or hash.
                # Let's use uuid5 with namespace_url
                job_id = str(uuid.uuid5(uuid.NAMESPACE_URL, job_data["link"]))

                # Check if exists
                existing_job = repo.get_job_posting(job_id)

                if not existing_job:
                    # Prepare data for Firestore
                    # Map 'locations' to 'location' string if needed by model, or keep 'locations' list?
                    # backend/app/models.py JobPosting has 'location': str.
                    # Frontend Jobs.jsx uses 'locations' array_contains_any.
                    # Ah, mismatch?
                    # backend/app/models.py:
                    # class JobPosting(BaseModel): ... location: str ...
                    # backend/app/firestore_repo.py search_jobs:
                    # if location: query = query.where("locations", "array_contains", location)
                    # So Firestore expects 'locations' array.
                    # But the Pydantic model says 'location' string.
                    # This implies 'location' string in Pydantic is wrong or mapped differently?
                    # backend/app/main.py: return [models.JobPostResponse(..., **job) for job in jobs]
                    # JobPostResponse has 'location' string.
                    # If Firestore has 'locations' array, Pydantic might fail validation if we just unpack `**job`.
                    # But Python unpacking is loose if not validated strictly at that point?
                    # Wait, FastAPI validates the response model.
                    # If `job` dict has `locations` (list) but model expects `location` (str), it will fail or cast.
                    # I should check `models.py` again.
                    # `location: str`.
                    # I should probably update `models.py` to match Firestore usage (`locations: List[...]`).
                    # Or adapt here.
                    # I'll stick to what `scrape_jobs` produces: `locations` list of dicts.

                    # I will adapt `job_data` to match what `repo.put_job_posting` expects.
                    # And `repo` expects dict.

                    # I'll save `locations` as list.
                    # Also map `location` (singular) to a string representation for compatibility.

                    loc_str = "Remote" # Default
                    if job_data["locations"]:
                        # rough heuristic
                        l = job_data["locations"][0]
                        if l.get("location_string"):
                            loc_str = l.get("location_string")
                        elif l.get("type"):
                            loc_str = l.get("type")

                    final_job_data = {
                        "title": title,
                        "company": job_data["company"],
                        "description": job_data["description"],
                        "posting_date": job_data["posting_date"],
                        "locations": job_data["locations"],
                        "location": loc_str, # Polyfill for Pydantic model
                        "work_arrangement": "Unknown", # Add default
                        "link": job_data["link"], # Save link too!
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc),
                    }

                    repo.put_job_posting(job_id, final_job_data)
                    scraped_count += 1

        except Exception as e:
            logger.error(f"Error scraping {domain_name}: {e}")

    return scraped_count
