"""
Salesforce OAuth Token Generator.

Exchanges a JWT for a Salesforce bearer access token over the JWT bearer flow.

Requires the following env. vars (refer main readme)
SALESFORCE_INSTANCE_URL
SALESFORCE_TOKEN_GRANT_TYPE
"""

import os
import logging
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_exception,
    before_sleep_log,
    after_log
)
from .jwt_token_creator import SalesforceJWTTokenCreator

TOKEN_ENDPOINT = '/services/oauth2/token'
DEFAULT_SF_GRANT_TYPE = 'urn:ietf:params:oauth:grant-type:jwt-bearer'

logger = logging.getLogger(__name__)

class SFTokenResponse(BaseModel):
    access_token: str
    scope: str
    instance_url: str
    id: str
    token_type: str
    api_instance_url: str

def is_retryable_http_error(exception):
    if isinstance(exception, httpx.HTTPStatusError):
        status_code = exception.response.status_code
        return status_code >= 500 or status_code in [408, 429]
    return False

class SalesforceTokenGenerator:
    """
    Fetches SF OAuth Access token over the JWT Bearer flow
    """

    def __init__(self, load_env: bool = True, timeout: int = 30):
        if load_env:
            load_dotenv()

        self.sf_token_response = None
        self.sf_inst_url = os.getenv('SALESFORCE_INSTANCE_URL').rstrip('/')
        self.sf_grant_type = os.getenv('SALESFORCE_TOKEN_GRANT_TYPE', default=DEFAULT_SF_GRANT_TYPE)
        self.timeout = timeout
        self.jwt_creator = SalesforceJWTTokenCreator()

        self.client = httpx.Client(
            timeout=httpx.Timeout(timeout, connect=10.0),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )

    def get_sf_token(self) -> SFTokenResponse:
        """
        Generates a local JWT bearer token and then exchanges that for an access token
        :return:
            SFTokenResponse
        """
        # @todo add expiration validation
        if self.sf_token_response:
            return self.sf_token_response

        self.sf_token_response = self._fetch()
        return self.sf_token_response

    @retry(
        stop=stop_after_attempt(4), # initial attempt + 3 retries
        wait=wait_exponential(multiplier=1, min=1, max=60),
        retry=(
            retry_if_exception_type(httpx.RequestError) |
            retry_if_exception(is_retryable_http_error)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.DEBUG),
        reraise=True
    )
    def _fetch(self):
        url = f"{self.sf_inst_url}{TOKEN_ENDPOINT}"
        payload = {
            "grant_type": self.sf_grant_type,
            "assertion": self.jwt_creator.generate_jwt()
        }

        logger.debug(f"Attempting to fetch Salesforce Access token: {url}")

        try:
            response = self.client.post(url, data=payload)
            response.raise_for_status()

            token_response = SFTokenResponse(**response.json())
            logger.info("Successfully obtained Salesforce access token")
            return token_response
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            error_txt = e.response.text

            logger.error(f"Http Error {status_code}: {error_txt[:200]}")

            if status_code < 500 and status_code not in [408, 429]:
                raise httpx.HTTPStatusError(
                    f"Non retryable http error {status_code}: {error_txt}",
                    request=e.request,
                    response=e.response
                )
            raise
        except httpx.RequestError as e:
            logger.warning(f"Networking error: {str(e)}")
            raise