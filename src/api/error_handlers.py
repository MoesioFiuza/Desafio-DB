from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.domain.exceptions.domain_errors import DomainError
from src.shared.request_context import request_id_ctx


def _field_path_pt_br(error: dict[str, Any]) -> str:
    loc = [str(x) for x in error.get("loc", ())]
    if loc and loc[0] in ("body", "query"):
        loc = loc[1:]
    return ".".join(loc) if loc else "requisição"


def _format_request_validation_message(exc: RequestValidationError) -> str:
    lines: list[str] = []
    for err in exc.errors():
        field = _field_path_pt_br(err)
        err_type = err.get("type", "")
        if err_type == "extra_forbidden":
            lines.append(f'O campo "{field}" não é permitido nesta requisição.')
        elif err_type == "missing":
            lines.append(f'O campo "{field}" é obrigatório.')
        elif err_type == "string_too_short":
            lines.append(f'O campo "{field}" é mais curto que o mínimo permitido.')
        elif err_type == "string_too_long":
            lines.append(f'O campo "{field}" excede o tamanho máximo permitido.')
        elif err_type in ("greater_than_equal", "less_than_equal", "greater_than", "less_than"):
            lines.append(f'O valor do campo "{field}" está fora do intervalo permitido.')
        elif err_type == "bool_parsing":
            lines.append(f'O campo "{field}" deve ser verdadeiro ou falso.')
        elif err_type in ("int_parsing", "float_parsing", "decimal_parsing"):
            lines.append(f'O campo "{field}" deve ser um número válido.')
        elif err_type == "date_from_datetime_parsing":
            lines.append(f'O campo "{field}" deve ser uma data válida.')
        else:
            lines.append(f'O campo "{field}" é inválido.')

    if not lines:
        return "Os dados enviados são inválidos. Verifique os campos e tente novamente."
    return "Não foi possível validar a requisição. " + " ".join(lines)


def _error_payload(code: str, message: str) -> dict[str, object]:
    return {
        "success": False,
        "code": code,
        "message": message,
        "trace_id": request_id_ctx.get(),
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error_payload(code=exc.code, message=str(exc)),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_payload(
                code="request_validation_error",
                message=_format_request_validation_message(exc),
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(
                code="unexpected_error",
                message="Ocorreu um erro interno. Tente novamente mais tarde.",
            ),
        )
