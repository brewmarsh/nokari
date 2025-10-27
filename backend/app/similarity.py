import json
from backend.app.dynamo_repo import DynamoRepo
from backend.app.ml import calculate_string_similarity

def find_similar_jobs_logic(job_id: str, all_jobs: list):
    """
    Placeholder logic for finding similar jobs.
    In a real implementation, this would involve more sophisticated ML models.
    """
    source_job = next((job for job in all_jobs if job["PK"] == f"JOB#{job_id}"), None)
    if not source_job:
        return []

    similarities = []
    for job in all_jobs:
        if job["PK"] != source_job["PK"]:
            similarity = calculate_string_similarity(
                source_job.get("description", ""),
                job.get("description", "")
            )
            if similarity > 0.1: # Arbitrary threshold
                similarities.append((job["PK"].split("#")[1], similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return [job_id for job_id, score in similarities[:5]] # Return top 5

def handler(event, context):
    """
    The AWS Lambda handler for the "find similar jobs" task.
    """
    dynamo_repo = DynamoRepo(table_name="NokariData")

    for record in event['Records']:
        message = json.loads(record['body'])
        job_id = message['job_id']
        task_id = message['task_id']

        # In a real app, you might query for jobs with similar titles/locations first
        # to narrow down the search space.
        all_jobs = dynamo_repo.search_jobs()

        similar_job_ids = find_similar_jobs_logic(job_id, all_jobs)

        dynamo_repo.put_similarity_result(task_id, similar_job_ids)
        print(f"Stored similarity results for task {task_id}")

    return {
        "statusCode": 200,
        "body": "Similarity search complete."
    }
