import ssl
from abc import abstractmethod, ABC
from types import TracebackType
from typing import Self

import aiohttp

from ..schemes import ValidateTotpAuthorizationResult
from ..client_types import (
    RequestTotpAuthorizationParams,
    CSimClientConstructor,
    ValidateTotpAuthorizationParams,
)


class ICSimClient(ABC):

    @abstractmethod
    def __init__(self, params: CSimClientConstructor) -> None: ...

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...


    @abstractmethod
    async def request_totp_authorization(self, params: RequestTotpAuthorizationParams) -> None: ...

    @abstractmethod
    async def validate_totp_authorization(
            self,
            params: ValidateTotpAuthorizationParams
    ) -> ValidateTotpAuthorizationResult | None: ...

    @abstractmethod
    async def _validate_response(self, response: aiohttp.ClientResponse) -> None: ...

    @abstractmethod
    def _make_ssl_context(self) -> ssl.SSLContext: ...