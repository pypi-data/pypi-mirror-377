# cSIM SDK

A Python SDK for integrating cSIM's TOTP (Time-based One-Time Password) authorization system into your applications.

## Overview

The cSIM SDK provides a simple and secure way to implement phone number verification using TOTP in your python applications. It offers a clean API for requesting and validating TOTP authorizations, with built-in TypeScript type definitions for improved development experience.

### Key Features

- TOTP-based phone number verification
- Python types support with full type definitions
- Asynchronous API
- Built-in exception handling
- aiohttp HTTP client
- Minimal dependencies

## System Requirements

- Python 3.11 or higher 

## Installation

Install the package using pip:

```bash
pip install chainsim-sdk-python
```

Or using uv:

```bash
uv add chainsim-sdk-python
```

## Configuration

To use the SDK, you'll need:
- A Provider ID from cSIM
- An API Key from cSIM

Get your own credentials - https://t.me/chainsim_partnerships;

ChainSIM demo application - https://chainsimdemo.xyz

Create a new client instance with your credentials:

```python
from chainsim_sdk import CSimClient
from chainsim_sdk.client_types import (
    CSimClientConstructor
)
from chainsim_sdk.constants import MAINNET_API_URL

main_client = CSimClient(
    params=CSimClientConstructor(
        api_url=MAINNET_API_URL,
        provider_id='your-provider-id',
        api_key='your-api-key',
    )
)
```

## Usage

### Basic Example

```python
import asyncio

from chainsim_sdk import CSimClient
from chainsim_sdk.client_types import (
    CSimClientConstructor,
    RequestTotpAuthorizationParams,
    ValidateTotpAuthorizationParams,
)
from chainsim_sdk.constants import MAINNET_API_URL



async def main():
    # Init CSimClient client
    main_client = CSimClient(
        params=CSimClientConstructor(
            api_url=MAINNET_API_URL,
            provider_id='your-provider-id',
            api_key='your-api-key',
        )
    )

    async with main_client as client:
        # Request totp auth
        await client.request_totp_authorization(RequestTotpAuthorizationParams(
            phone_number="00000000000"
        ))

        # Validate totp auth
        # response = await client.validate_totp_authorization(ValidateTotpAuthorizationParams(
        #     phone_number="00000000000",
        #     code="000000"
        # ))
        # print(response)



if __name__ == '__main__':
    # Run main function in asyncio event loop
    asyncio.run(main())
```

### Advanced Usage

Handle validation results and errors:

```python
import asyncio

import chainsim_sdk.exceptions
from chainsim_sdk import CSimClient
from chainsim_sdk.client_types import (
    CSimClientConstructor,
    ValidateTotpAuthorizationParams,
)
from chainsim_sdk.constants import MAINNET_API_URL


async def main():
    main_client = CSimClient(
        params=CSimClientConstructor(
            api_url=MAINNET_API_URL,
            provider_id='your-provider-id',
            api_key='your-api-key',
        )
    )

    async with main_client as client:
        try:
            response = await client.validate_totp_authorization(ValidateTotpAuthorizationParams(
                    phone_number="00000000000",
                    code="000000"
                ))
            print(response)
        except chainsim_sdk.exceptions.BadRequestException as e:
            print(e.message)
        except chainsim_sdk.exceptions.UnauthorizedException as e:
            print('Please, authorize again')
        except chainsim_sdk.exceptions.ChainsimSDKException as e:
            print(f'Error message: {e.message}')

if __name__ == '__main__':
    asyncio.run(main())
```

## API Documentation

### CSimClient

#### Constructor

```python
def __init__(self, params: CSimClientConstructor) -> None:
    self._params = params
    self._session: Optional[aiohttp.ClientSession] = None
```

Configuration options:
- `provider_id` (string): Your cSIM provider ID
- `api_key` (string): Your cSIM API key
- `api_url` (string): Actual api url with slash in the end, e.g. `https://api.chainsim.io/api/v1/bridge/`

#### Methods

##### request_totp_authorization

```python
@dataclass
class RequestTotpAuthorizationParams:
    phone_number: str

async def request_totp_authorization(self, params: RequestTotpAuthorizationParams) -> None: ...
```

Parameters:
- `phone_number` (string): The phone number to verify

##### validate_totp_authorization

```python

@dataclass
class RequestTotpAuthorizationParams:
    phone_number: str

@dataclass
class ValidateTotpAuthorizationParams(RequestTotpAuthorizationParams):
    code: str

async def validate_totp_authorization(
        self,
        params: ValidateTotpAuthorizationParams
) -> ValidateTotpAuthorizationResult | None: ...
```

Parameters:
- `phone_number` (string): The phone number being verified
- `code` (string): The TOTP code received by the user

Returns:
- `number`: Object containing the phone number details
  - `number` (string): The verified phone number
  - `contract_address` (string): Associated contract address
- `user`: Object containing user details
  - `address` (string): User's address

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your Provider ID and API Key are correct
   - Ensure you're using the latest SDK version
   - Check if your API key has the necessary permissions

2. **Invalid Phone Numbers**
   - Ensure phone numbers are in E.164 format (e.g., +1234567890)
   - Include the country code
   - Remove any special characters or spaces

3. **TOTP Validation Failures**
   - Verify the code hasn't expired
   - Ensure the code matches exactly what was received
   - Check if the phone number matches the one used in the request

4. **SSL Verification failed**
   - Could be caused by aiohttp library
   - Try: `pip install pip-system-certs`

### Error Handling

The SDK uses custom exceptions for different error scenarios:

```python
try:
    # SDK operations
except chainsim_sdk.exceptions.BadRequestException as e:
    # Handle invalid request params
except chainsim_sdk.exceptions.UnauthorizedException as e:
    # Handle authentification issues
except chainsim_sdk.exceptions.ChainsimSDKException as e:
    # Handle other cSIM-specific errors
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your PR:
- Includes tests for new functionality
- Updates documentation as needed
- Follows the existing code style
- Includes a clear description of the changes

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:
- Visit our website: [https://chainsim.io](https://chainsim.io)
- Check our documentation
- Contact our support team: https://t.me/chainsim_partnerships

For bug reports and feature requests, please open an issue on our GitHub repository.

Chief maintainer: [Kirill Sermyagin](https://github.com/abcen7)