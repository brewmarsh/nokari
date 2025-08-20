import os
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
