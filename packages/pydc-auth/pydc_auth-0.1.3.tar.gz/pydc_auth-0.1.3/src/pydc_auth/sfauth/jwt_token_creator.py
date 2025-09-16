"""
JWT Token creator for Salesforce OAuth JWT bearer flow

Requires a connected to be setup in the corresponding org.

Requires a local private key ".key" file to cryptographically sign the token.

Requires the following env. vars:
SALESFORCE_APP_SUBJECT: log-in username
SALESFORCE_APP_PRIVATE_KEY: location of the local private key file
SALESFORCE_APP_CONSUMER_KEY: the consumer key of the connected app
SALESFORCE_ORGANIZATION_ID: 18-char Salesforce org-id
"""

import os
import jwt
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv

TOKEN_EXPIRATION_MINUTES = 5

class SalesforceJWTTokenCreator:
    """creates JWT tokens for Salesforce OAuth JWT bearer flow"""

    def __init__(self, load_env: bool = True):
        """
        :param load_env:
        """
        if load_env:
            load_dotenv()

        self.token = None
        self.app_subject = os.getenv('SALESFORCE_APP_SUBJECT')
        self.organization_id = os.getenv('SALESFORCE_ORGANIZATION_ID')
        self.private_key_path = os.getenv('SALESFORCE_APP_PRIVATE_KEY')
        self.consumer_key = os.getenv('SALESFORCE_APP_CONSUMER_KEY')

        # validate required env. vars
        self._validate_env_vars()

        # load private key
        self.private_key = self._load_private_key()

    def generate_jwt(self,
                     audience: str = "https://login.salesforce.com") -> str:
        """
        generates a signed JWT for the OAuth jwt bearer flow

        :param audience:

        :return:
            str: JWT

        :raises:
            Exception: if there's any error when generating the token
        """
        if self.token and self._token_valid():
            return self.token

        current_time = int(time.time())

        payload = {
            'jti': str(uuid.uuid4()),
            'iss': self.consumer_key,
            'sub': self.app_subject,
            'aud': audience,
            'exp': current_time + (TOKEN_EXPIRATION_MINUTES * 60),
            'iat':current_time
        }

        try:
            token = jwt.encode(
                payload=payload,
                key=self.private_key,
                algorithm='RS256'
            )
            self.token = token
            return token
        except Exception as e:
            raise Exception(f"Exception when generating token: {str(e)}")

    def _validate_env_vars(self):
        requires_vars = {
            'SALESFORCE_APP_SUBJECT': self.app_subject,
            'SALESFORCE_APP_PRIVATE_KEY': self.private_key_path,
            'SALESFORCE_APP_CONSUMER_KEY': self.consumer_key,
            'SALESFORCE_ORGANIZATION_ID': self.organization_id
        }

        missing_vars = [var for var, value in requires_vars.items() if not value]

        if missing_vars:
            raise ValueError(f"Missing required env. vars: {', '.join(missing_vars)}")

    def _load_private_key(self) -> str:
        try:
            private_key_file = Path(self.private_key_path)

            if not private_key_file.exists():
                raise FileNotFoundError(f"Private key file not found: {self.private_key_path}")

            with open(private_key_file, 'r') as f:
                private_key = f.read()

            if not private_key.strip():
                raise ValueError(f"Private key file is empty: {self.private_key_path}")

            return private_key
        except Exception as e:
            raise Exception(f"Error {e} loading private key: {self.private_key_path}")


    def _token_valid(self) -> bool:
        pass