"""
Salesforce OAuth Token Generator
"""

import os
import httpx
from pydantic import BaseModel
from dotenv import load_dotenv
from ..sfauth.sf_token_exchange import SalesforceTokenGenerator

DC_TOKEN_ENDPOINT = '/services/a360/token'


class DCTokenResponse(BaseModel):
    access_token: str
    instance_url: str


class DataCloudTokenGenerator:
    """ Fetches Data Cloud OAuth Access token"""
    def __init__(self, load_env: bool = True, timeout: int = 30):
        """
        Initialize the Data Cloud Token Generator

        Args:
            load_env: Auto load env. variables (default: True)
            timeout: Request timeout in seconds (default: 30)
        """
        if load_env:
            load_dotenv()

        self.dc_token_response = None
        self.sf_inst_url = os.getenv('SALESFORCE_INSTANCE_URL').rstrip('/')
        self.dc_grant_type = os.getenv('DATA_CLOUD_TOKEN_GRANT_TYPE')
        self.subject_token_type = os.getenv('DATA_CLOUD_SUBJECT_TOKEN_TYPE')
        self.timeout = timeout
        self.sf_token_generator = SalesforceTokenGenerator()

        # Initialize HTTP client with common headers
        self.client = httpx.Client(
            timeout=timeout,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

    def get_dc_token(self):
        """
        Generates a Salesforce OAuth Token and then exchange that for a DC Access Token
        """
        if self.dc_token_response:
            return self.dc_token_response['access_token']

        sf_token = self.sf_token_generator.get_sf_token()
        url = f"{self.sf_inst_url if self.sf_inst_url else sf_token.instance_url}{DC_TOKEN_ENDPOINT}"

        payload = {
            "grant_type": self.dc_grant_type,
            "subject_token": sf_token.access_token,
            "subject_token_type": self.subject_token_type
        }

        try:
            response = self.client.post(url, data=payload)
            response.raise_for_status()
            json = response.json()
            self.dc_token_response = DCTokenResponse(access_token=json["access_token"],
                                                     instance_url=json["instance_url"])
            return self.dc_token_response

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            raise httpx.HTTPStatusError(error_msg, request=e.request, response=e.response)
        except httpx.RequestError as e:
            raise httpx.RequestError(f"Network error: {str(e)}")

    def _validate_environment_variables(self):
        """Validate that all required environment variables are set"""
        required_vars = {
            'SALESFORCE_INSTANCE_URL': self.sf_inst_url
        }

        missing_vars = [var for var, value in required_vars.items() if not value]

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")