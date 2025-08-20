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

            # Try to find a date in the metatags
            posting_date = metatags.get('pubdate') or metatags.get('date') or metatags.get('publishdate')

            if posting_date:
                try:
                    # Attempt to parse the date. This is a best-effort approach and might need refinement
                    # based on the actual date formats encountered.
                    posting_date = datetime.strptime(posting_date, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    # If parsing fails, fall back to the current date
                    posting_date = datetime.now(timezone.utc).date()
            else:
                # If no date is found, use the current date
                posting_date = datetime.now(timezone.utc).date()

            jobs.append({
                'title': item.get('title'),
                'link': item.get('link'),
                'company': pagemap.get('cse_thumbnail', [{}])[0].get('src', '') or metatags.get('og:site_name', ''),
                'description': item.get('snippet'),
                'posting_date': posting_date,
            })
    return jobs
