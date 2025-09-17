from typing import Optional


class ChainsimSDKException(Exception):
    status = 500
    message = ""

    def __init__(
            self,
            message: str = "",
            exception: Optional[Exception] = None,
    ) -> None:
        if message:
            self.message = message
        self._exception = exception
        super().__init__(self.message)

    @property
    def exception(self) -> Optional[Exception]:
        return self._exception


class BadRequestException(ChainsimSDKException):
    def __init__(self, message: str = "") -> None:
        super().__init__(message=f"Bad Request: {message}")


class UnauthorizedException(ChainsimSDKException):
    def __init__(self) -> None:
        super().__init__(message='Unauthorized. Invalid Api Key or Provider Id')