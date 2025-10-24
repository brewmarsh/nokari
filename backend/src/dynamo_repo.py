import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any

class DynamoRepo:
    """
    A repository for interacting with the DynamoDB table.
    This class abstracts the boto3 calls and provides a clean interface for the application logic.

    The DynamoDB table uses a single-table design with composite keys:
    - PK (Partition Key): The primary identifier for an entity (e.g., 'USER#<uuid>', 'JOB#<job_id>').
    - SK (Sort Key): Used for sorting and defining relationships (e.g., 'METADATA', 'DETAILS').

    Entities:
    - User:
        - PK: USER#<user_id>
        - SK: METADATA
    - Job:
        - PK: JOB#<job_id>
        - SK: DETAILS
    - Resume:
        - PK: USER#<user_id>
        - SK: RESUME#<resume_id>
    - Domain:
        - PK: DOMAIN#<domain_name>
        - SK: METADATA

    GSIs (Global Secondary Indexes):
    - GSI1 (for querying users by email):
        - GSI1PK: USEREMAIL#<email>
        - GSI1SK: METADATA
    - GSI2 (for querying jobs by location and title):
        - GSI2PK: JOBLOCATION#<location>
        - GSI2SK: JOBTITLE#<title>
    - GSI3 (for querying jobs by matching status):
        - GSI3PK: JOBSTATUS#<status>
        - GSI3SK: JOB#<job_id>
    """

    def __init__(self, table_name: str, region_name: str = "us-east-1"):
        self.table_name = table_name
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.table = self.dynamodb.Table(self.table_name)

    def put_user(self, user_id: str, user_data: Dict[str, Any]):
        try:
            self.table.put_item(
                Item={
                    "PK": f"USER#{user_id}",
                    "SK": "METADATA",
                    **user_data,
                }
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            raise

    def get_user(self, user_id: str):
        try:
            response = self.table.get_item(
                Key={"PK": f"USER#{user_id}", "SK": "METADATA"}
            )
            return response.get("Item")
        except ClientError as e:
            print(e.response["Error"]["Message"])
            raise

    def get_user_by_email(self, email: str):
        # This will require a GSI on the email attribute.
        try:
            response = self.table.query(
                IndexName="GSI1",
                KeyConditionExpression="GSI1PK = :email",
                ExpressionAttributeValues={":email": f"USEREMAIL#{email}"},
            )
            return response.get("Items")
        except ClientError as e:
            print(e.response["Error"]["Message"])
            raise

    def put_job_posting(self, job_id: str, job_data: Dict[str, Any]):
        try:
            self.table.put_item(
                Item={
                    "PK": f"JOB#{job_id}",
                    "SK": "DETAILS",
                    **job_data,
                }
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            raise

    def get_job_posting(self, job_id: str):
        try:
            response = self.table.get_item(
                Key={"PK": f"JOB#{job_id}", "SK": "DETAILS"}
            )
            return response.get("Item")
        except ClientError as e:
            print(e.response["Error"]["Message"])
            raise

    # Add other methods for interacting with DynamoDB here.
