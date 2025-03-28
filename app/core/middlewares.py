import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import APIException
from app.utils.date_utils import Datetime
from app.utils.logger import api_logger


class AccessControlMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(
            self,
            request: Request,
            call_next: Callable
    ) -> Response:
        request.state.req_time = Datetime.datetime()
        request.state.start = time.time()
        request.state.inspect = None
        request.state.user = None

        request.state.ip = self._get_client_ip(request)

        try:
            response = await call_next(request)
            await api_logger(request=request, response=response)
        except Exception as e:
            print(f"Exception {e}")
            response = await self._handle_exception(request, e)

        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0]
        return request.client.host

    @staticmethod
    async def _handle_exception(
            request: Request,
            error: Exception
    ) -> JSONResponse:
        if not isinstance(error, APIException):
            error = APIException(ex=error, detail=str(error))

        error_dict = {
            "status": error.status_code,
            "msg": error.msg,
            "detail": error.detail,
            "code": error.status_code,
        }
        response = JSONResponse(
            status_code=error.status_code,
            content=error_dict
        )
        await api_logger(request=request, error=error)
        return response
