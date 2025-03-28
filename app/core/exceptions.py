from http import HTTPStatus


class APIException(Exception):
    status_code: int
    msg: str
    detail: str
    ex: Exception

    def __init__(
            self,
            *,
            status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
            msg: str = None,
            detail: str = None,
            ex: Exception = None,
    ):
        self.status_code = status_code
        self.msg = msg
        self.detail = detail
        self.ex = ex
        super().__init__(ex)


class UnKnownException(APIException):
    def __init__(self, custom_msg: str = None, ex: Exception = None):
        default_msg = HTTPStatus.INTERNAL_SERVER_ERROR.description
        detail_msg = f"{custom_msg}" if custom_msg else default_msg

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            msg=HTTPStatus.INTERNAL_SERVER_ERROR.description,
            detail=detail_msg,
            ex=ex,
        )


class UnauthorizedException(APIException):
    def __init__(self, custom_msg: str = None, ex: Exception = None):
        default_msg = HTTPStatus.UNAUTHORIZED.description
        detail_msg = f"{custom_msg}" if custom_msg else default_msg

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            msg=f"Authorization Required",
            detail=detail_msg,
            ex=ex,
        )


class TokenExpiredException(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            msg=f"Token Expired",
            detail=f"Token Expired",
            ex=ex,
        )


class TokenDecodeException(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            msg=f"Token has been compromised.",
            detail=f"Token has been compromised.",
            ex=ex,
        )


class NotFoundException(APIException):
    def __init__(self, custom_msg: str = None, ex: Exception = None):
        default_msg = HTTPStatus.NOT_FOUND.description
        detail_msg = f"{custom_msg}" if custom_msg else default_msg

        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            msg=HTTPStatus.NOT_FOUND.description,
            detail=detail_msg,
            ex=ex,
        )


class BadRequestException(APIException):
    def __init__(self, custom_msg: str = None, ex: Exception = None):
        default_msg = HTTPStatus.BAD_REQUEST.description
        detail_msg = f"{custom_msg}" if custom_msg else default_msg

        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            msg=HTTPStatus.BAD_REQUEST.description,
            detail=detail_msg,
            ex=ex,
        )


class ForbiddenException(APIException):
    def __init__(self, custom_msg: str = None, ex: Exception = None):
        default_msg = HTTPStatus.FORBIDDEN.description
        detail_msg = f"{custom_msg}" if custom_msg else default_msg

        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            msg=HTTPStatus.FORBIDDEN.description,
            detail=detail_msg,
            ex=ex,
        )


class UnprocessableEntity(APIException):
    def __init__(self, custom_msg: str = None, ex: Exception = None):
        default_msg = HTTPStatus.UNPROCESSABLE_ENTITY.description
        detail_msg = f"{custom_msg}" if custom_msg else default_msg

        super().__init__(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            msg=HTTPStatus.UNPROCESSABLE_ENTITY.description,
            detail=detail_msg,
            ex=ex,
        )


class DuplicateValueException(APIException):
    def __init__(self, custom_msg: str = None, ex: Exception = None):
        default_msg = HTTPStatus.CONFLICT
        detail_msg = f"{custom_msg}" if custom_msg else default_msg

        super().__init__(
            status_code=HTTPStatus.CONFLICT,
            msg=HTTPStatus.CONFLICT.description,
            detail=detail_msg,
            ex=ex,
        )


class DatabaseException(APIException):
    def __init__(self, custom_msg: str = None, ex: Exception = None):
        default_msg = HTTPStatus.INTERNAL_SERVER_ERROR
        detail_msg = f"{custom_msg}" if custom_msg else default_msg

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            msg=HTTPStatus.INTERNAL_SERVER_ERROR.description,
            detail=detail_msg,
            ex=ex,
        )


class ValidationException(APIException):
    def __init__(self, custom_msg: str = None, ex: Exception = None):
        default_msg = HTTPStatus.BAD_REQUEST
        detail_msg = f"{custom_msg}" if custom_msg else default_msg

        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            msg=HTTPStatus.BAD_REQUEST.description,
            detail=detail_msg,
            ex=ex,
        )
