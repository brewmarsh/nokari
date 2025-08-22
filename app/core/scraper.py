import os
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from datetime import datetime, timezone

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

            jobs.append({
                'title': title,
                'link': item.get('link'),
                'company': pagemap.get('cse_thumbnail', [{}])[0].get('src', '') or metatags.get('og:site_name', ''),
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
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        if e.response and e.response.status_code == 404:
            raise ScraperException(f"URL not found (404): {url}")
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
