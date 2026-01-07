from typing import Dict, Any

def enrich_job_with_flags(job: Dict[str, Any]) -> None:
    """
    Enriches a job dictionary with boolean flags for remote, hybrid, and onsite
    based on the 'locations' list and 'searchable_locations' field.
    Modifies the dictionary in place.
    """
    job_locs = job.get("locations", [])
    is_remote = False
    is_hybrid = False
    is_onsite = False

    # Check structured locations
    for loc in job_locs:
            if isinstance(loc, dict):
                l_type = loc.get("type", "").lower()
                if "remote" in l_type:
                    is_remote = True
                if "hybrid" in l_type:
                    is_hybrid = True
                if "onsite" in l_type:
                    is_onsite = True

    # Fallback to searchable_locations
    if not (is_remote or is_hybrid or is_onsite):
            searchable = job.get("searchable_locations", [])
            if "remote" in searchable:
                is_remote = True
            if "hybrid" in searchable:
                is_hybrid = True
            if "onsite" in searchable:
                is_onsite = True

    job["remote"] = is_remote
    job["hybrid"] = is_hybrid
    job["onsite"] = is_onsite
