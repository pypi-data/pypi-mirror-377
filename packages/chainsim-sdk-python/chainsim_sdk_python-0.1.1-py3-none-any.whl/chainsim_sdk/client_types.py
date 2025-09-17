import ssl
from dataclasses import dataclass
from typing import Optional


@dataclass
class CSimClientConfig:
    provider_id: str
    api_key: str


@dataclass
class CSimClientConstructor(CSimClientConfig):
    api_url: str
    ssl_context: Optional[ssl.SSLContext] = None


@dataclass
class RequestTotpAuthorizationParams:
    phone_number: str

@dataclass
class ValidateTotpAuthorizationParams(RequestTotpAuthorizationParams):
    code: str

@dataclass
class Number:
    number: str
    contract_address: str

@dataclass
class User:
    address: str


