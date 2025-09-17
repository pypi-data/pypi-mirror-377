from enum import StrEnum
from typing import Final

MAINNET_API_URL: Final[str] = 'https://api.chainsim.io/api/v1/bridge/'

HEADER_PROVIDER_ID: Final[str] = 'x-provider-id'
HEADER_AUTHORIZATION: Final[str] = 'authorization'

BEARER_AUTH_METHOD: Final[str] = 'Bearer'

class MainNetApiV1Endpoints(StrEnum):
    REQUEST = "request"
    VALIDATE = "validate"