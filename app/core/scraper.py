import os
import re
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from datetime import datetime, timezone

JOB_TITLE_KEYWORDS = [
    "engineer", "director", "manager", "analyst", "developer", "specialist",
    "consultant", "architect", "designer", "lead", "president", "officer",
    "recruiter", "coordinator"
]
WORK_TYPE_KEYWORDS = ["remote", "hybrid", "onsite", "on-site"]
SEPARATORS = [' at ', ' | ', ' - ', ',']

def parse_job_title(title):
    """
    Parses a job title to extract the company name and work type.
    Returns a dictionary with cleaned_title, company, and work_types.
    """
    original_title = title
    extracted_company = None
    extracted_work_types = []

    # First, extract work types and clean the title
    for work_type in WORK_TYPE_KEYWORDS:
        if re.search(r'\b' + work_type + r'\b', title, re.IGNORECASE):
            extracted_work_types.append(work_type.replace("-", ""))
            title = re.sub(r'\b' + work_type + r'\b', '', title, flags=re.IGNORECASE).strip()

    # Then, try to extract company
    for sep in SEPARATORS:
        if sep in title:
            # Special handling for ' at '
            if sep == ' at ':
                parts = title.rsplit(sep, 1)
                if len(parts) == 2:
                    title, extracted_company = parts[0].strip(), parts[1].strip()
                    break
            else:
                parts = title.split(sep, 1)
                if len(parts) == 2:
                    part1, part2 = parts[0].strip(), parts[1].strip()

                    p1_is_title = any(keyword in part1.lower() for keyword in JOB_TITLE_KEYWORDS)
                    p2_is_title = any(keyword in part2.lower() for keyword in JOB_TITLE_KEYWORDS)

                    if p1_is_title and not p2_is_title:
                        title, extracted_company = part1, part2
                        break
                    elif p2_is_title and not p1_is_title:
                        title, extracted_company = part2, part1
                        break
                    # If ambiguous, could fall back to length, but for now we'll be conservative
                    # and not extract a company.

    if extracted_company is not None:
        extracted_company = extracted_company.strip(" ,-|")
        if not extracted_company:
            extracted_company = None

    # Final cleanup of title
    title = title.strip(" ,-|")

    return {
        'cleaned_title': title or original_title,
        'company': extracted_company,
        'work_types': extracted_work_types
    }


class ScraperException(Exception):
    pass

def scrape_jobs(query, domain, days=None):
    api_key = os.environ.get('GOOGLE_API_KEY')
    search_engine_id = os.environ.get('CUSTOM_SEARCH_ENGINE_ID')

    if not api_key or not search_engine_id:
        raise ScraperException("GOOGLE_API_KEY and CUSTOM_SEARCH_ENGINE_ID must be set in the environment.")

    service = build("customsearch", "v1", developerKey=api_key)

    search_query = f'{query} -intitle:"jobs at" -intitle:"careers" site:{domain}'

    search_args = {
        'q': search_query,
        'cx': search_engine_id,
        'num': 10,
    }

    if days:
        search_args['dateRestrict'] = f'd{days}'

    result = service.cse().list(**search_args).execute()

    jobs = []
    if 'items' in result:
        for item in result['items']:
            pagemap = item.get('pagemap', {})
            metatags = pagemap.get('metatags', [{}])[0]
            title = item.get('title', '')
            description = item.get('snippet', '')
            full_text = f"{title.lower()} {description.lower()}"

            # Process locations
            locations = []
            location_string = metatags.get('joblocation')

            is_remote = 'remote' in full_text
            is_hybrid = 'hybrid' in full_text
            is_onsite = 'onsite' in full_text

            if is_remote:
                locations.append({"type": "remote"})
            if is_hybrid:
                locations.append({"type": "hybrid", "location_string": location_string or ''})
            if is_onsite:
                locations.append({"type": "onsite", "location_string": location_string or ''})

            # If no specific work arrangement is mentioned, but there's a location, assume onsite.
            # If no work arrangement and no location, still default to onsite.
            if not locations:
                locations.append({"type": "onsite", "location_string": location_string or ''})

            # Try to find a date in the metatags
            posting_date_str = metatags.get('pubdate') or metatags.get('date') or metatags.get('publishdate')
            posting_date = None
            if posting_date_str:
                try:
                    posting_date = datetime.strptime(posting_date_str, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass  # Keep as None if parsing fails

            # Parse the title to extract company and work types
            parsed_title_data = parse_job_title(title)
            cleaned_title = parsed_title_data['cleaned_title']
            extracted_company = parsed_title_data['company']
            extracted_work_types = parsed_title_data['work_types']

            # Get company from metatags
            company = metatags.get('og:site_name', '') or pagemap.get('cse_thumbnail', [{}])[0].get('src', '')
            # If company from metatags is a URL or empty, try to use the one from the title
            if (not company or company.startswith('http')) and extracted_company:
                company = extracted_company

            # Add extracted work types to locations list
            existing_work_types = {loc['type'] for loc in locations}
            for work_type in extracted_work_types:
                if work_type not in existing_work_types:
                    locations.append({'type': work_type})

            jobs.append({
                'title': cleaned_title,
                'link': item.get('link'),
                'company': company,
                'description': description,
                'locations': locations,
                'posting_date': posting_date,
            })
    return jobs

def scrape_job_details(url):
    """
    Scrapes the job description from a given URL.
    Returns the full description text.
    Raises ScraperException on failure.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 404:
                raise ScraperException(f"URL not found (404): {url}")
            if e.response.status_code == 403:
                raise ScraperException(f"Forbidden (403): {url}")
        raise ScraperException(f"Failed to download URL: {url}. Error: {e}")

    soup = BeautifulSoup(response.content, 'html.parser')

    # A list of common selectors for job descriptions. This is a starting point.
    selectors = [
        {'id': 'job-description'},
        {'class': 'job-description'},
        {'id': 'job_description'},
        {'class': 'job_description'},
        {'class': 'job-details'},
        {'class': 'job-details-content'},
    ]

    description_element = None
    for selector in selectors:
        description_element = soup.find(None, attrs=selector)
        if description_element:
            break

    if description_element:
        return description_element.get_text(separator='\n', strip=True)
    else:
        # As a fallback, return the body text. This is not ideal.
        body_text = soup.body.get_text(separator='\n', strip=True) if soup.body else ""
        if len(body_text) > 50: # Arbitrary length to check if we got something useful
            return body_text
        else:
            raise ScraperException(f"Could not find job description at URL: {url}")
