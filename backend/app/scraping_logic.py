import fnmatch
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

from backend.app.firestore_repo import FirestoreRepo

logger = logging.getLogger(__name__)


class ScraperException(Exception):
    pass


def get_session():
    """Returns a requests Session with common browser headers."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Referer": "https://www.google.com/",
        }
    )
    return session


def scrape_job_details(url):
    """
    Scrapes the details of a single job posting from its URL.
    Returns a dictionary with the scraped data.
    """
    session = get_session()
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        details = {}

        # 1. Try JSON-LD (Preferred method for structured data)
        json_ld_scripts = soup.find_all("script", type="application/ld+json")
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                # Should be type JobPosting
                if data.get("@type") == "JobPosting":
                    details["title"] = data.get("title")

                    if "hiringOrganization" in data:
                        org = data["hiringOrganization"]
                        if isinstance(org, dict):
                            details["company"] = org.get("name")
                        elif isinstance(org, str):
                            details["company"] = org

                    if "description" in data:
                        # Keep description as is (HTML) but maybe normalize whitespace
                        # to avoid massive spacing issues, but don't strip tags.
                        details["description"] = data["description"].strip()

                    if "datePosted" in data:
                        try:
                            # Handle ISO format
                            # Example: 2025-10-14T21:34:00+0000
                            # Python 3.11+ handles this well. Python 3.12 is used.
                            details["posting_date"] = datetime.fromisoformat(
                                data["datePosted"]
                            )
                        except ValueError:
                            pass

                    # Locations
                    if "jobLocation" in data:
                        locs = data["jobLocation"]
                        if not isinstance(locs, list):
                            locs = [locs]

                        parsed_locs = []
                        first_loc_string = None
                        for loc in locs:
                            if loc.get("@type") == "Place" and "address" in loc:
                                addr = loc["address"]
                                parts = []
                                if isinstance(addr, dict):
                                    if addr.get("streetAddress"):
                                        parts.append(
                                            addr["streetAddress"].replace("\n", ", ")
                                        )
                                    if addr.get("addressLocality"):
                                        parts.append(addr["addressLocality"])
                                    if addr.get("addressRegion"):
                                        parts.append(addr["addressRegion"])
                                    if addr.get("addressCountry"):
                                        country = addr["addressCountry"]
                                        # addressCountry can be string or object
                                        if isinstance(country, dict):
                                            parts.append(country.get("name", ""))
                                        else:
                                            parts.append(country)

                                loc_str = ", ".join([p for p in parts if p])
                                if loc_str:
                                    if not first_loc_string:
                                        first_loc_string = loc_str
                                    # Infer type
                                    # Default to onsite unless we detect otherwise?
                                    parsed_locs.append(
                                        {"type": "onsite", "location_string": loc_str}
                                    )

                        if parsed_locs:
                            details["locations"] = parsed_locs

                            # Extract city, state, country from first valid location
                            for loc in locs:
                                if loc.get("@type") == "Place" and "address" in loc:
                                    addr = loc["address"]
                                    if isinstance(addr, dict):
                                        if addr.get("addressLocality"):
                                            details["city"] = addr["addressLocality"]
                                        if addr.get("addressRegion"):
                                            details["state"] = addr["addressRegion"]
                                        if addr.get("addressCountry"):
                                            country = addr["addressCountry"]
                                            if isinstance(country, dict):
                                                details["country"] = country.get("name", "")
                                            else:
                                                details["country"] = country
                                        # Use the first one found
                                        break

                    # If we found valid data, we can return or merge.
                    if details.get("title"):
                        # Clean title
                        if " | " in details["title"]:
                            details["title"] = details["title"].split(" | ")[0]
                        if " - " in details["title"]:
                            # Often companies append " - Company Name"
                            details["title"] = details["title"].split(" - ")[0]

                        # Clean company
                        if details.get("company") and details["company"].lower() in ["careers", "job"]:
                             # Try to fallback to something better if possible, or leave it blank
                             pass

                        return details
            except json.JSONDecodeError:
                continue

        # Check for iCIMS iframe (Fallback / Legacy logic)
        iframe = soup.find("iframe", id="icims_content_iframe") or soup.find(
            "iframe", id="noscript_icims_content_iframe"
        )
        if iframe:
            src = iframe.get("src")
            if src:
                from urllib.parse import urljoin

                iframe_url = urljoin(url, src)
                try:
                    logger.info(f"Following iframe to {iframe_url}")
                    iframe_response = session.get(iframe_url, timeout=10)
                    iframe_response.raise_for_status()
                    soup = BeautifulSoup(iframe_response.content, "html.parser")
                except Exception as e:
                    logger.warning(f"Failed to follow iframe: {e}")

        # Title - Try h1 first
        h1 = soup.find("h1")
        if h1:
            details["title"] = h1.get_text(strip=True)
        else:
            details["title"] = soup.title.string if soup.title else ""

        # Clean title (remove common suffixes)
        if details.get("title"):
            separators = [" | ", " - ", " : "]
            for sep in separators:
                 if sep in details["title"]:
                      parts = details["title"].split(sep)
                      # Heuristic: Job title is usually the first part
                      details["title"] = parts[0]

        parsed_url = urlparse(url)
        # Check for Lever specific logic
        if "lever.co" in parsed_url.netloc:
            # Company from path
            path_parts = parsed_url.path.strip("/").split("/")
            if len(path_parts) > 0:
                # e.g. "palantir" -> "Palantir"
                # If there are dashes or special formatting, we might want to be careful,
                # but capitalizing is a good start.
                details["company"] = path_parts[0].capitalize()

            # Title from h2
            # Lever usually puts the job title in an h2 tag (often with 'posting-headline' class parent,
            # but h2 is distinctive enough in the top section)
            h2 = soup.find("h2")
            if h2:
                details["title"] = h2.get_text(strip=True)

            # Locations and Type
            # Inspecting Lever pages, we see classes like:
            # location -> class="location" or class="sort-by-time posting-category ... location"
            # workplace type -> class="workplaceTypes"
            # commitment -> class="commitment"
            # department -> class="department"

            lever_locations = []

            # Location
            loc_div = soup.find("div", class_="location")
            location_str = loc_div.get_text(strip=True) if loc_div else None

            # Workplace Type (Hybrid, Remote, Onsite)
            type_div = soup.find("div", class_="workplaceTypes")
            workplace_type_str = type_div.get_text(strip=True) if type_div else None

            if location_str or workplace_type_str:
                # Determine type
                loc_type = "onsite"  # Default
                if workplace_type_str:
                    w_type_lower = workplace_type_str.lower()
                    if "hybrid" in w_type_lower:
                        loc_type = "hybrid"
                    elif "remote" in w_type_lower:
                        loc_type = "remote"
                elif location_str:
                    if "remote" in location_str.lower():
                        loc_type = "remote"
                    elif "hybrid" in location_str.lower():
                        loc_type = "hybrid"

                # Construct location object
                # If we have both strings, we can combine or just use location_str as the string
                final_loc_str = location_str or workplace_type_str

                lever_locations.append(
                    {"type": loc_type, "location_string": final_loc_str}
                )

                details["locations"] = lever_locations

        # Fallback Locations if Lever logic didn't find anything or for non-Lever sites
        if "locations" not in details:
            locations = []
            # Look for "Job Locations"
            for element in soup.find_all(
                string=lambda text: text and "Job Locations" in text
            ):
                # Check parent text
                parent = element.parent
                if not parent:
                    continue
                text = parent.get_text(strip=True)
                # If the text is just "Job Locations", check siblings
                if text == "Job Locations":
                    # Next sibling element?
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        loc = next_elem.get_text(strip=True)
                        if loc:
                            locations.append({"type": "onsite", "location_string": loc})
                elif text.startswith("Job Locations"):
                    loc = text.replace("Job Locations", "").strip()
                    if loc:
                        locations.append({"type": "onsite", "location_string": loc})

            if locations:
                details["locations"] = locations

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


def scrape_jobs(query, domain, days=None, blocked_patterns=None):
    """
    Scrapes job postings from a given domain using the Google Custom Search API.

    Args:
        query (str): The search query for job titles.
        domain (str): The domain to search within (e.g., "lever.co").
        days (int, optional): The number of past days to restrict the search to.
        blocked_patterns (list, optional): List of URL patterns to block.

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
            link = item.get("link")
            if blocked_patterns and link:
                is_blocked = False
                for pattern in blocked_patterns:
                    if fnmatch.fnmatch(link, pattern):
                        logger.info(f"Skipping blocked URL: {link} (matches {pattern})")
                        is_blocked = True
                        break
                if is_blocked:
                    continue

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
                    posting_date = datetime.strptime(posting_date_str, "%Y-%m-%d")
                except (ValueError, TypeError):
                    pass  # Keep as None if parsing fails

            job_data = {
                "title": title,
                "link": item.get("link"),
                "company": metatags.get("og:site_name", "")
                or pagemap.get("cse_thumbnail", [{}])[0].get("src", "")
                or domain.split(".")[0],  # Fallback to domain name
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
                    if scraped_details.get("locations"):
                        job_data["locations"] = scraped_details["locations"]

                    if scraped_details.get("city"):
                        job_data["city"] = scraped_details["city"]
                    if scraped_details.get("state"):
                        job_data["state"] = scraped_details["state"]
                    if scraped_details.get("country"):
                        job_data["country"] = scraped_details["country"]

                    # Update company if scraped_details found a better one
                    if scraped_details.get("company"):
                        if scraped_details["company"].lower() not in ["careers", "home", "index"]:
                            job_data["company"] = scraped_details["company"]

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
    # Fetch blocked patterns once
    try:
        blocked_patterns_docs = repo.get_blocked_patterns()
        blocked_patterns = [doc["pattern"] for doc in blocked_patterns_docs]
    except Exception as e:
        logger.warning(f"Failed to fetch blocked patterns: {e}")
        blocked_patterns = []

    scraped_count = 0
    for domain_obj in domains:
        domain_name = (
            domain_obj["domain"]
            if isinstance(domain_obj, dict) and "domain" in domain_obj
            else domain_obj
        )
        try:
            logger.info(f"Scraping {domain_name} for {query_term}...")
            jobs = scrape_jobs(
                query_term, domain_name, days=days, blocked_patterns=blocked_patterns
            )
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
                    # Flatten locations for searching
                    searchable_locations = []
                    for loc in job_data["locations"]:
                        if loc.get("type"):
                            searchable_locations.append(loc["type"])
                        if loc.get("location_string"):
                            searchable_locations.append(loc["location_string"])

                    # Default location string for display
                    loc_str = "Remote"
                    if job_data["locations"]:
                        first_location = job_data["locations"][0]
                        if first_location.get("location_string"):
                            loc_str = first_location.get("location_string")
                        elif first_location.get("type"):
                            loc_str = first_location.get("type")

                    final_job_data = {
                        "title": title,
                        "company": job_data["company"],
                        "description": job_data["description"],
                        "posting_date": job_data["posting_date"],
                        "locations": job_data["locations"],
                        "searchable_locations": searchable_locations,
                        "city": job_data.get("city"),
                        "state": job_data.get("state"),
                        "country": job_data.get("country"),
                        "work_arrangement": "Unknown",
                        "link": job_data["link"],
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc),
                    }

                    repo.put_job_posting(job_id, final_job_data)
                    scraped_count += 1

        except Exception as e:
            logger.error(f"Error scraping {domain_name}: {e}")

    return scraped_count
