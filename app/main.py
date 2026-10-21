"""Create and configure the FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.tickets import router as tickets_router

_VALUE_ERROR_PREFIX = "Value error, "


def validation_error_detail(exc: RequestValidationError) -> str:
    """Turn a validation error into a single client-facing message."""
    parts: list[str] = []
    for error in exc.errors():
        location = [
            str(item)
            for item in error.get("loc", [])
            if item not in {"body", "query", "path"}
        ]
        message = str(error.get("msg", "Invalid request."))
        if message.startswith(_VALUE_ERROR_PREFIX):
            message = message.removeprefix(_VALUE_ERROR_PREFIX)
        if location:
            parts.append(f"{'.'.join(location)}: {message}")
        else:
            parts.append(message)
    if not parts:
        return "Request validation failed."
    return "; ".join(parts)


def create_app() -> FastAPI:
    """Build the application with ticket routes and predictable errors."""
    app = FastAPI(
        title="Support Ticket API",
        version="0.1.0",
        summary="Create, list, read, and update support tickets.",
    )
    app.include_router(tickets_router)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": validation_error_detail(exc)},
        )

    return app


app = create_app()
