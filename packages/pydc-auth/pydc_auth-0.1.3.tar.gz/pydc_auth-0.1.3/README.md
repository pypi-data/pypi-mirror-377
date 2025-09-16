# pydc-auth

Auth helpers for **Salesforce** and **Salesforce Data Cloud (A360)**:

- Build a signed **JWT** for the OAuth 2.0 **JWT Bearer** flow  
- Exchange that JWT for a **Salesforce access token**  
- Exchange the Salesforce token for a **Data Cloud access token** (`/services/a360/token`)

> **Python 3.12+** • Uses `httpx`, `PyJWT`, `pydantic`, `tenacity`, `python-dotenv`  
> Import name: **`pydc_auth`** (underscore) • Distribution name: **`pydc-auth`** (hyphen)

---

## Installation

**From PyPI:**
```bash
pip install pydc-auth
```

## Quick Start
```python
from pydc_auth import DataCloudTokenGenerator

dc = DataCloudTokenGenerator()
dc_token = dc.get_dc_token()  # pydantic model with .access_token and .instance_url

print("DC instance:", dc_token.instance_url)
print("Bearer:", dc_token.access_token[:24], "…")
```
## Configuration (Environment Variables)
The following environment are required by the library. Set as environment variables or in a `.env` file (loaded by `python-dotenv`).

### Required Variables for base JWT Creation:
| Variable                      | Purpose                                           |
| ----------------------------- | ------------------------------------------------- |
| `SALESFORCE_APP_SUBJECT`      | Username of the integration user (JWT `sub`)      |
| `SALESFORCE_APP_PRIVATE_KEY`  | **Filesystem path** to your private key (PEM)     |
| `SALESFORCE_APP_CONSUMER_KEY` | Connected App **Consumer Key** (JWT `iss`)        |
| `SALESFORCE_ORGANIZATION_ID`  | Org ID (read by code; not included in JWT claims) |

### Required Variables for Salesforce Token Exchange:
| Variable                      | Purpose                                                                                  |
| ----------------------------- | ---------------------------------------------------------------------------------------- |
| `SALESFORCE_INSTANCE_URL`     | e.g., `https://login.salesforce.com` (or `https://test.salesforce.com`)                  |
| `SALESFORCE_TOKEN_GRANT_TYPE` | OAuth grant type (defaults to JWT Bearer: `urn:ietf:params:oauth:grant-type:jwt-bearer`) |

### Required Variables for Data Cloud Token Exchange:
| Variable                        | Purpose                                                                                |
| ------------------------------- | -------------------------------------------------------------------------------------- |
| `SALESFORCE_INSTANCE_URL`       | Used to construct the Data Cloud token URL (falls back to the SF token’s instance URL) |
| `DATA_CLOUD_TOKEN_GRANT_TYPE`   | Token exchange grant type (set per your org/API configuration)                         |
| `DATA_CLOUD_SUBJECT_TOKEN_TYPE` | Subject token type for exchange (set per your org/API configuration)                   |

### Example `.env`:
```bash
# JWT
SALESFORCE_APP_SUBJECT="integration.user@example.com"
SALESFORCE_APP_PRIVATE_KEY="/secure/path/private.key"
SALESFORCE_APP_CONSUMER_KEY="3MVG9..."
SALESFORCE_ORGANIZATION_ID="00D..."

# SF token exchange
SALESFORCE_INSTANCE_URL="https://login.salesforce.com"
# SALESFORCE_TOKEN_GRANT_TYPE="urn:ietf:params:oauth:grant-type:jwt-bearer"  # default

# DC token exchange (values vary by org/config)
DATA_CLOUD_TOKEN_GRANT_TYPE="urn:ietf:params:oauth:grant-type:token-exchange"
DATA_CLOUD_SUBJECT_TOKEN_TYPE="urn:ietf:params:oauth:token-type:access_token"
```

## API Surface (minimal)
All return types are pydantic models unless noted.
### `DataCloudTokenGenerator`:
``
get_dc_token() -> DCTokenResponse
Uses SalesforceTokenGenerator to get an org token, then exchanges at …/services/a360/token.
``
