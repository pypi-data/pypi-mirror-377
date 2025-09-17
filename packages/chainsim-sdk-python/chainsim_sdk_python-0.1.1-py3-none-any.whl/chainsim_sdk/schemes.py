from dataclasses import dataclass

from .client_types import Number, User


@dataclass
class RequestTotpAuthorizationScheme:
    csim_number: str

@dataclass
class RequestValidateTotpAuthorizationScheme:
    csim_number: str
    totp_code: str


@dataclass
class ValidateTotpAuthorizationResult:
    number: Number
    user: User

@dataclass
class ValidateTotpAuthorizationResponse:
    success: bool
    result: ValidateTotpAuthorizationResult
