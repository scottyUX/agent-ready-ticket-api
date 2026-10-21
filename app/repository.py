"""In-memory storage for support tickets."""

from app.models import Ticket, TicketCreate, TicketStatus


class TicketRepository:
    """Store tickets in a process-local dictionary."""

    def __init__(self) -> None:
        self._tickets: dict[int, Ticket] = {}
        self._next_id = 1

    def reset(self) -> None:
        """Remove every ticket and start ids at 1 again."""
        self._tickets = {}
        self._next_id = 1

    def create(self, data: TicketCreate) -> Ticket:
        ticket = Ticket(
            id=self._next_id,
            title=data.title,
            description=data.description,
            status=TicketStatus.OPEN,
        )
        self._tickets[ticket.id] = ticket
        self._next_id += 1
        return ticket

    def list_tickets(self) -> list[Ticket]:
        return list(self._tickets.values())

    def get(self, ticket_id: int) -> Ticket | None:
        return self._tickets.get(ticket_id)

    def update_status(self, ticket_id: int, status: TicketStatus) -> Ticket | None:
        """Store a new status for an existing ticket.

        Every TicketStatus value is accepted, including a change away from
        resolved. docs/TASKS.md task 4 is the exercise that narrows this.
        """
        current = self._tickets.get(ticket_id)
        if current is None:
            return None
        updated = current.model_copy(update={"status": status})
        self._tickets[ticket_id] = updated
        return updated


ticket_repository = TicketRepository()
