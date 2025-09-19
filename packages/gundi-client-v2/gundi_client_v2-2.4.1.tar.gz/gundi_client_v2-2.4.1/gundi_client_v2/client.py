import logging
import json
import httpx

from datetime import datetime, timezone, timedelta
from httpx import (
    AsyncClient,
    AsyncHTTPTransport,
    Timeout,
)
from pydantic import parse_obj_as
from typing import List
from gundi_core.schemas import (
    OAuthToken,
)
from gundi_core.schemas.v2 import Connection, Route, Integration, GundiTrace, IntegrationType
from . import settings, errors
from . import auth


logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)


class GundiDataSenderClient:
    def __init__(self, integration_api_key: str = None, **kwargs):
        self.gundi_version = "v2"
        self.sensors_api_endpoint = (
            f"{kwargs.get('sensors_api_base_url', settings.SENSORS_API_BASE_URL)}/{self.gundi_version}"
        )
        self._api_key = integration_api_key

    async def post_observations(self, data: List[dict]) -> dict:
        return await self._post_data(data=data, endpoint="observations")

    async def post_events(self, data: List[dict]) -> dict:
        return await self._post_data(data=data, endpoint="events")

    async def post_messages(self, data: List[dict]) -> dict:
        return await self._post_data(data=data, endpoint="messages")

    async def update_event(self, event_id: str, data: dict) -> dict:
        return await self._update_data(data=data, endpoint=f"events/{event_id}")

    async def post_event_attachments(self, event_id: str, attachments: List[tuple]) -> dict:
        return await self._post_data(attachments=attachments, endpoint=f"events/{event_id}/attachments")

    async def _post_data(self, data: List[dict] = None, endpoint: str = None, attachments: List[tuple] = None) -> dict:
        apikey = self._api_key

        logger.info(
            f' -- Posting to routing services --',
            extra={"integration_api_key": apikey}
        )

        url = f"{self.sensors_api_endpoint}/{endpoint}/"

        request = dict(
            url=url,
            headers={"apikey": apikey}
        )

        if data:
            clean_batch = [json.loads(json.dumps(r, default=str)) for r in data]
            request["json"] = clean_batch

        if attachments:
            request["files"] = [
                ('file', (filename, image_binary)) for filename, image_binary in attachments
            ]

        logger.debug(
            f" -- sending {endpoint}. --",
            extra={
                "length": len(data or attachments),
                "api": url,
            },
        )

        async with httpx.AsyncClient(timeout=120) as session:
            client_response = await session.post(**request)

        client_response.raise_for_status()

        return client_response.json()

    async def _update_data(self, data: dict = None, endpoint: str = None) -> dict:
        apikey = self._api_key

        logger.info(
            f' -- Updating data... --',
            extra={"integration_api_key": apikey}
        )

        url = f"{self.sensors_api_endpoint}/{endpoint}/"

        request = dict(
            url=url,
            headers={"apikey": apikey}
        )

        clean_batch = json.loads(json.dumps(data, default=str))
        request["json"] = clean_batch

        logger.debug(
            f" -- sending {endpoint}. --",
            extra={
                "length": len(clean_batch),
                "api": url,
            },
        )

        async with httpx.AsyncClient(timeout=120) as session:
            client_response = await session.patch(**request)

        client_response.raise_for_status()

        return client_response.json()


class GundiClient:
    DEFAULT_CONNECT_TIMEOUT_SECONDS = 3.1
    DEFAULT_DATA_TIMEOUT_SECONDS = 20
    DEFAULT_CONNECTION_RETRIES = 5

    def __init__(self, **kwargs):
        # API settings
        self.gundi_version = "v2"
        self.base_url = kwargs.get("base_url", settings.GUNDI_API_BASE_URL)
        self.api_base_path = f"{self.base_url}/{self.gundi_version}"
        self.connections_endpoint = f"{self.api_base_path}/connections"
        self.integrations_endpoint = f"{self.api_base_path}/integrations"
        self.source_states_endpoint = f"{self.api_base_path}/sources/states"
        self.sources_endpoint = f"{self.api_base_path}/sources"
        self.routes_endpoint = f"{self.api_base_path}/routes"
        self.traces_endpoint = f"{self.api_base_path}/traces"

        # Authentication settings
        self.ssl_verify = kwargs.get("use_ssl", settings.GUNDI_API_SSL_VERIFY)
        self.client_id = kwargs.get("keycloak_client_id", settings.KEYCLOAK_CLIENT_ID)
        self.client_secret = kwargs.get("keycloak_client_secret", settings.KEYCLOAK_CLIENT_SECRET)
        self.oauth_token_url = kwargs.get("oauth_token_url", settings.OAUTH_TOKEN_URL)
        self.audience = kwargs.get("keycloak_audience", settings.KEYCLOAK_AUDIENCE)
        self.cached_token = None
        self.cached_token_expires_at = datetime.min.replace(tzinfo=timezone.utc)

        # Retries and timeouts settings
        self.max_retries = kwargs.get('max_http_retries', self.DEFAULT_CONNECTION_RETRIES)
        transport = AsyncHTTPTransport(retries=self.max_retries, verify=self.ssl_verify)
        connect_timeout = kwargs.get('connect_timeout', self.DEFAULT_CONNECT_TIMEOUT_SECONDS)
        data_timeout = kwargs.get('data_timeout', self.DEFAULT_DATA_TIMEOUT_SECONDS)
        timeout = Timeout(data_timeout, connect=connect_timeout, pool=connect_timeout)

        # Session
        self._session = AsyncClient(transport=transport, timeout=timeout)

    async def close(self):
        await self._session.aclose()

    # Support using this client as an async context manager.
    async def __aenter__(self):
        await self._session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._session.__aexit__()

    async def _get(self, url, params=None, headers=None, **kwargs):
        headers = headers or {}
        auth_headers = await self.get_auth_header()
        response = await self._session.get(
            url,
            params=params,
            headers={**auth_headers, **headers},
            **kwargs,
        )
        # Force refresh the token and retry if we get redirected to the login page
        if response.status_code == 302 and "auth/realms" in response.headers.get("location", ""):
            headers = await self.get_auth_header(force_refresh_token=True)
            response = await self._session.get(
                url,
                params=params,
                headers=headers,
                **kwargs,
            )
        return response

    async def _post(self, url, data: dict = None, params=None, headers=None, **kwargs):
        headers = headers or {}
        auth_headers = await self.get_auth_header()
        response = await self._session.post(
            url,
            json=data,
            params=params,
            headers={**auth_headers, **headers},
            **kwargs,
        )
        # Force refresh the token and retry if we get redirected to the login page
        if response.status_code == 302 and "auth/realms" in response.headers.get("location", ""):
            headers = await self.get_auth_header(force_refresh_token=True)
            await self._session.post(
                url,
                json=json,
                params=params,
                headers={**auth_headers, **headers},
                **kwargs,
            )
        return response

    async def _refresh_token(self):
        token = await auth.get_access_token(
            session=self._session,
            oauth_token_url=self.oauth_token_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            audience=self.audience
        )
        self.cached_token_expires_at = datetime.now(tz=timezone.utc) + timedelta(
            seconds=token.expires_in - 15
        )  # fudge factor
        self.cached_token = token
        return token

    async def get_access_token(self, force_refresh_token=False) -> OAuthToken:
        if force_refresh_token or not self.cached_token or self.cached_token_expires_at < datetime.now(tz=timezone.utc):
            return await self._refresh_token()
        return self.cached_token

    async def get_auth_header(self, force_refresh_token=False) -> dict:
        token_object = await self.get_access_token(force_refresh_token=force_refresh_token)
        return {
            "authorization": f"{token_object.token_type} {token_object.access_token}"
        }

    async def get_connection_details(self, integration_id):
        url = f"{self.connections_endpoint}/{integration_id}/"
        response = await self._get(url)
        # ToDo: Add custom exceptions to handle errors
        response.raise_for_status()
        data = response.json()
        return Connection.parse_obj(data)

    async def get_route_details(self, route_id):
        url = f"{self.routes_endpoint}/{route_id}/"
        response = await self._get(url)
        # ToDo: Add custom exceptions to handle errors
        response.raise_for_status()
        data = response.json()
        return Route.parse_obj(data)

    async def get_integration_details(self, integration_id):
        url = f"{self.integrations_endpoint}/{integration_id}/"
        response = await self._get(url)
        # ToDo: Add custom exceptions to handle errors
        response.raise_for_status()
        data = response.json()
        return Integration.parse_obj(data)

    async def get_integration_api_key(self, integration_id):
        url = f"{self.integrations_endpoint}/{integration_id}/api-key/"
        response = await self._get(url)
        # ToDo: Add custom exceptions to handle errors
        response.raise_for_status()
        data = response.json()
        return data.get("api_key")

    async def get_traces(self, params: dict):
        url = f"{self.traces_endpoint}/"
        response = await self._get(url, params=params)
        # ToDo: Add custom exceptions to handle errors
        response.raise_for_status()
        data = response.json()["results"]
        return parse_obj_as(List[GundiTrace], data)

    async def register_integration_type(self, data: dict):
        url = f"{self.integrations_endpoint}/types/"
        response = await self._post(
            url,
            data=data,
        )
        # ToDo: Add custom exceptions to handle errors
        response.raise_for_status()
        data = response.json()
        return IntegrationType.parse_obj(data)
