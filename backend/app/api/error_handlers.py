"""Manejo centralizado de errores HTTP.

Los routers lanzan excepciones de dominio; este módulo las traduce a
respuestas JSON con el sobre unificado `{ "error": { code, message, field } }`.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.exceptions import DomainError


def _error_payload(code: str, message: str, field: str | None = None) -> dict:
    return {"error": {"code": code, "message": message, "field": field}}


def register_error_handlers(app: FastAPI) -> None:
    """Registra los manejadores de excepciones a nivel de aplicación."""

    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content=_error_payload(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        first_error = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(part) for part in first_error.get("loc", [])[1:]) or None
        message = first_error.get("msg", "Cuerpo de solicitud inválido")
        return JSONResponse(
            status_code=422,
            content=_error_payload("VALIDATION_ERROR", message, field),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        _: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload("HTTP_ERROR", str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=_error_payload("INTERNAL_ERROR", "Ocurrió un error inesperado"),
        )
