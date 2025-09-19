# app/core/auth.py
# Third-party imports
from fastmcp.server.dependencies import get_http_headers

from app.services.constants import CLOUD_IAM_ENDPOINT, CPD_IAM_ENDPOINT
from app.shared.exceptions.base import ExternalAPIError

# Application-specific imports
from app.core.settings import settings
from app.shared.utils.http_client import get_http_client

from async_lru import alru_cache

INVALID_ENV_MODE = "ENV_MODE is either not provided in env or not one of SaaS or CPD"


async def get_access_token() -> str | None:
    """
    Resolve Authorization header from HTTP request headers or STDIO fallback.
    Returns a full 'Bearer ...' string or None if nothing available.
    If apikey is provided instead, calls relevant apis for SaaS or CPD
    to get the bearer token
    """
    headers = get_http_headers()  # {} if not over HTTP / no active request
    auth = headers.get("authorization", "")

    if not auth:
        api_key_header = headers.get("x-api-key", "")
        if api_key_header:
            auth = await get_bearer_token_from_apikey(
                api_key_header, headers.get("username", "")
            )

    if not auth and settings.server_transport == "stdio":
        if settings.stdio_auth_token:
            auth = settings.stdio_auth_token
            if not auth.lower().startswith("bearer "):
                auth = f"Bearer {auth}"
        elif settings.stdio_apikey:
            apikey = settings.stdio_apikey
            username = settings.stdio_username
            auth = await get_bearer_token_from_apikey(apikey, username)

    return auth or None


def get_iam_url() -> str:
    if settings.env_mode == "SaaS":
        return settings.cloud_iam_url + CLOUD_IAM_ENDPOINT
    elif settings.env_mode == "CPD":
        return settings.base_url + CPD_IAM_ENDPOINT
    else:
        raise ExternalAPIError(
            INVALID_ENV_MODE
        )


def get_request_body(api_key: str, username: str) -> dict:
    if settings.env_mode == "SaaS":
        return {
            "apikey": api_key,
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        }
    elif settings.env_mode == "CPD":
        if not username:
            raise ExternalAPIError(
                "For CPD, USERNAME has to be provided in the header if running the server under "
                "http mode else in env if running in stdio mode"
            )
        return {"api_key": api_key, "username": username}
    else:
        raise ExternalAPIError(
            
        )


def get_header():
    if settings.env_mode == "SaaS":
        return {"Content-Type": "application/x-www-form-urlencoded"}
    elif settings.env_mode == "CPD":
        return {"Content-Type": "application/json"}
    else:
        raise ExternalAPIError(
            INVALID_ENV_MODE
        )


@alru_cache(maxsize=100, ttl=3540)
async def get_bearer_token_from_apikey(api_key: str, username: str) -> str:
    headers = get_header()
    req_body = get_request_body(api_key, username)
    iam_url = get_iam_url()

    client = get_http_client()

    try:
        if settings.env_mode == "SaaS":
            response = await client.post(
                iam_url,
                headers=headers,
                data=req_body,
                content_type="application/x-www-form-urlencoded",
            )
            token = response.get("access_token", "")
            return "Bearer " + token
        else:
            response = await client.post(iam_url, headers=headers, data=req_body)
            token = response.get("token", "")
            return "Bearer " + token

    except ExternalAPIError:
        # This will catch HTTP errors (4xx, 5xx) that were raised by raise_for_status()
        raise
    except Exception as e:
        raise ExternalAPIError(f"Failed to get bearer token: {str(e)}")


@alru_cache(maxsize=100, ttl=3540)
async def get_dph_catalog_id_from_token(bearer_token) -> str:
    headers = get_header()
    headers.update({"Authorization": bearer_token})

    client = get_http_client()

    try:
        response = await client.get(
            f"{settings.base_url}/v2/catalogs/ibm-default-hub", headers=headers
        )
        return response.get("metadata", {}).get("guid", "")

    except ExternalAPIError:
        # This will catch HTTP errors (4xx, 5xx) that were raised by raise_for_status()
        raise
    except Exception as e:
        raise ExternalAPIError(f"Failed to get bearer token: {str(e)}")
