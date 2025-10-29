import os
from googleapiclient.discovery import build
from datetime import datetime
from .models import JobPosting, ScrapableDomain
from .ml_utils import generate_embedding
import requests
from bs4 import BeautifulSoup
import logging

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
        raise ScraperException(
            "GOOGLE_API_KEY and CUSTOM_SEARCH_ENGINE_ID must be set in the environment."
        )

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
                    ).date()
                except (ValueError, TypeError):
                    pass  # Keep as None if parsing fails

            job_data = {
                "title": title,
                "link": item.get("link"),
                "company": metatags.get("og:site_name", "")
                or pagemap.get("cse_thumbnail", [{}])[0].get("src", ""),
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


def scrape_and_save_jobs(query, domains, days=None):
    """
    Scrapes jobs from a list of domains and saves new jobs to the database.

    Args:
        query (str): The search query for job titles.
        domains (QuerySet or list): A list of ScrapableDomain objects or strings.
        days (int, optional): The number of past days to restrict the search to.

    Returns:
        int: The number of new jobs that were scraped and saved.
    """
    scraped_count = 0
    for domain_obj in domains:
        domain_name = (
            domain_obj.domain if isinstance(domain_obj, ScrapableDomain) else domain_obj
        )
        try:
            jobs = scrape_jobs(query, domain_name, days=days)
            for job_data in jobs:
                title = job_data["title"]
                if "Job Application for" in title:
                    title = title.replace("Job Application for", "").strip()

                obj, created = JobPosting.objects.get_or_create(
                    link=job_data["link"],
                    defaults={
                        "title": title,
                        "company": job_data["company"],
                        "description": job_data["description"],
                        "posting_date": job_data["posting_date"],
                        "locations": job_data["locations"],
                    },
                )
                if created:
                    text = f"{obj.title} {obj.description}"
                    obj.embedding = generate_embedding(text)
                    obj.save()
                    scraped_count += 1
        except Exception as e:
            # In a real app, you'd want to log this properly
            print(f"Error scraping {domain_name}: {e}")

    return scraped_count


def parse_job_title(title):
    """
    Parses a job title to extract the company and work types.
    """
    cleaned_title = title
    company = None
    work_types = []

    # Handle work types first
    if " - " in cleaned_title:
        parts = cleaned_title.split(" - ")
        for i, part in enumerate(parts):
            if part.lower() in ["remote", "hybrid", "onsite"]:
                work_types.append(part.lower())
                parts.pop(i)
                break
        cleaned_title = " - ".join(parts)

    if "," in cleaned_title:
        parts = cleaned_title.split(",")
        if len(parts) > 1:
            cleaned_title = parts[0].strip()
            company = parts[1].strip()

    # Example: "Software Engineer at Google (Remote)"
    if " at " in cleaned_title:
        parts = cleaned_title.split(" at ")
        cleaned_title = parts[0].strip()
        company = parts[1].strip()

    if "(" in cleaned_title and ")" in cleaned_title:
        work_type_part = cleaned_title.split("(")[-1].split(")")[0]
        # common work types
        if "remote" in work_type_part.lower():
            work_types.append("remote")
        if "hybrid" in work_type_part.lower():
            work_types.append("hybrid")
        if "on-site" in work_type_part.lower() or "onsite" in work_type_part.lower():
            work_types.append("onsite")

        cleaned_title = cleaned_title.split("(")[0].strip()

    return {
        "cleaned_title": cleaned_title.strip(),
        "company": company,
        "work_types": list(set(work_types)),
    }
