import ssl
from dataclasses import asdict
from types import TracebackType
from typing import Any, Optional

import aiohttp

from typing import Self

import certifi

from .exceptions import (
    ChainsimSDKException,
    BadRequestException,
    UnauthorizedException,
)
from .schemes import (
    RequestTotpAuthorizationScheme,
    RequestValidateTotpAuthorizationScheme,
    ValidateTotpAuthorizationResponse,
    ValidateTotpAuthorizationResult,
)
from .interfaces import ICSimClient
from .client_types import (
    CSimClientConstructor,
    RequestTotpAuthorizationParams,
    ValidateTotpAuthorizationParams,
)
from .constants import (
    HEADER_PROVIDER_ID,
    BEARER_AUTH_METHOD,
    HEADER_AUTHORIZATION,
    MainNetApiV1Endpoints,
)


class CSimClient(ICSimClient):
    def __init__(self, params: CSimClientConstructor) -> None:
        self._params = params
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> Self:
        timeout_val = getattr(self._params, "timeout", None)
        timeout = aiohttp.ClientTimeout(total=timeout_val) if timeout_val else None

        ssl_context = self._params.ssl_context or self._make_ssl_context()

        connector = aiohttp.TCPConnector(ssl=ssl_context)

        self._session = aiohttp.ClientSession(
            base_url=self._params.api_url,
            headers={
                HEADER_PROVIDER_ID: self._params.provider_id,
                HEADER_AUTHORIZATION: f"{BEARER_AUTH_METHOD} {self._params.api_key}",
            },
            timeout=timeout,
            connector=connector
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    def _make_ssl_context(self) -> ssl.SSLContext:
        return ssl.create_default_context(cafile=certifi.where())

    def _ensure_session(self) -> aiohttp.ClientSession:
        if not self._session or self._session.closed:
            raise ChainsimSDKException(
                "Client session is not initialized. Use `async with CSimClient(...)`."
            )
        return self._session

    async def _validate_response(self, response: aiohttp.ClientResponse) -> None:
        if response.status == 400:
            raise BadRequestException(await response.text())
        if response.status in {401, 403}:
            raise UnauthorizedException()
        if response.status >= 400:
            raise ChainsimSDKException(
                f"API error {response.status}: {await response.text()}"
            )

    async def _post_json(self, url: str, payload: dict[str, Any]) -> Any:
        session = self._ensure_session()
        try:
            async with session.post(url, json=payload) as response:
                await self._validate_response(response)
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return await response.json()
                return await response.text()
        except aiohttp.ClientError as e:
            raise ChainsimSDKException("Network error") from e

    async def request_totp_authorization(
        self, params: RequestTotpAuthorizationParams
    ) -> None:
        await self._post_json(
            MainNetApiV1Endpoints.REQUEST,
            asdict(RequestTotpAuthorizationScheme(csim_number=params.phone_number)),
        )

    async def validate_totp_authorization(
        self, params: ValidateTotpAuthorizationParams
    ) -> ValidateTotpAuthorizationResult:
        data = await self._post_json(
            MainNetApiV1Endpoints.VALIDATE,
            asdict(
                RequestValidateTotpAuthorizationScheme(
                    csim_number=params.phone_number,
                    totp_code=params.code,
                )
            ),
        )
        if isinstance(data, str):
            raise ChainsimSDKException("Unexpected response from API (expected JSON).")
        return ValidateTotpAuthorizationResponse(**data).result
