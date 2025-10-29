import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import json
import pytest
from unittest.mock import patch, MagicMock
from backend.app import similarity


@patch("backend.app.similarity.DynamoRepo")
def test_similarity_handler(MockDynamoRepo):
    mock_repo_instance = MockDynamoRepo.return_value
    mock_repo_instance.search_jobs.return_value = [
        {"PK": "JOB#job1", "description": "python developer"},
        {"PK": "JOB#job2", "description": "java developer"},
        {"PK": "JOB#job3", "description": "senior python engineer"},
    ]

    event = {
        "Records": [{"body": json.dumps({"job_id": "job1", "task_id": "task123"})}]
    }
    context = {}

    result = similarity.handler(event, context)

    assert result["statusCode"] == 200
    # The similarity logic correctly identifies both 'job2' (due to 'developer') and 'job3' (due to 'python')
    # as similar, and sorts 'job2' first because its similarity score is higher.
    mock_repo_instance.put_similarity_result.assert_called_once_with(
        "task123", ["job2", "job3"]
    )
