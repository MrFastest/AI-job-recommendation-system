import requests

APP_ID = "YOUR_APP_ID"
APP_KEY = "YOUR_APP_KEY"

BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def fetch_jobs(query, country="in", results=20):
    url = f"{BASE_URL}/{country}/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results,
        "what": query,
        "content-type": "application/json"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return []

    data = response.json()

    jobs = []

    for job in data.get("results", []):
        jobs.append({
            "title": job.get("title", ""),
            "company": job.get("company", {}).get("display_name", "Unknown"),
            "location": job.get("location", {}).get("display_name", ""),
            "description": job.get("description", ""),
            "url": job.get("redirect_url", "")
        })

    return jobs