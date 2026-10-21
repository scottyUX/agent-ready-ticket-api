"""HTTP behavior for creating, reading, listing, and updating tickets."""

from fastapi import APIRouter, HTTPException, status

from app.models import ErrorResponse, Ticket, TicketCreate, TicketUpdate
from app.repository import ticket_repository

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post(
    "",
    response_model=Ticket,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse}},
)
def create_ticket(payload: TicketCreate) -> Ticket:
    return ticket_repository.create(payload)


@router.get("", response_model=list[Ticket])
def list_tickets() -> list[Ticket]:
    return ticket_repository.list_tickets()


@router.get(
    "/{ticket_id}",
    response_model=Ticket,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def get_ticket(ticket_id: int) -> Ticket:
    ticket = ticket_repository.get(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )
    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=Ticket,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def update_ticket_status(ticket_id: int, payload: TicketUpdate) -> Ticket:
    ticket = ticket_repository.update_status(ticket_id, payload.status)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )
    return ticket
