import boto3
import os
from botocore.exceptions import ClientError

class CognitoRepo:
    """
    A repository for interacting with AWS Cognito.
    """

    def __init__(self):
        self.client = boto3.client("cognito-idp", region_name=os.environ.get("COGNITO_REGION", "us-east-1"))
        self.user_pool_id = os.environ.get("COGNITO_USER_POOL_ID")
        self.client_id = os.environ.get("COGNITO_AUDIENCE")

    def sign_up(self, email: str, password: str) -> bool:
        """
        Signs up a new user in the Cognito User Pool.
        """
        if not self.user_pool_id or not self.client_id:
            raise ValueError("Cognito User Pool ID and Client ID must be set.")

        try:
            self.client.sign_up(
                ClientId=self.client_id,
                Username=email,
                Password=password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    }
                ]
            )
            return True
        except ClientError as e:
            print(f"Cognito sign-up failed: {e.response['Error']['Message']}")
            raise
