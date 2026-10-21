"""Request, response, and domain models for support tickets."""

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class TicketStatus(StrEnum):
    """Lifecycle states a ticket can be given in the base API."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class TicketCreate(BaseModel):
    """Payload for creating a ticket."""

    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=2000)

    @field_validator("title", "description")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped


class TicketUpdate(BaseModel):
    """Payload for changing a ticket's status."""

    status: TicketStatus


class Ticket(BaseModel):
    """Ticket returned by the API."""

    id: int
    title: str
    description: str
    status: TicketStatus


class ErrorResponse(BaseModel):
    """Predictable error body. The detail is a message, never a traceback."""

    detail: str
