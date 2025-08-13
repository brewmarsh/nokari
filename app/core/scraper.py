import os
from googleapiclient.discovery import build

def scrape_jobs(query, domain):
    api_key = os.environ.get('GOOGLE_API_KEY')
    search_engine_id = os.environ.get('CUSTOM_SEARCH_ENGINE_ID')

    if not api_key or not search_engine_id:
        print("GOOGLE_API_KEY and CUSTOM_SEARCH_ENGINE_ID must be set in the environment.")
        return []

    service = build("customsearch", "v1", developerKey=api_key)

    search_query = f'{query} site:{domain}'

    try:
        result = service.cse().list(
            q=search_query,
            cx=search_engine_id,
            num=10,  # Number of results to return
        ).execute()

        jobs = []
        if 'items' in result:
            for item in result['items']:
                jobs.append({
                    'title': item.get('title'),
                    'link': item.get('link'),
                    'company': item.get('pagemap', {}).get('metatags', [{}])[0].get('og:site_name', ''),
                    'description': item.get('snippet'),
                })
        return jobs
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
