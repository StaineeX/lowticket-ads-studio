from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class AuditEvent:
    operation_id: str
    event: str
    result: str
    details: str
    timestamp: datetime


@dataclass
class AuditLog:
    events: list[AuditEvent] = field(default_factory=list)

    def record(self, operation_id: str, event: str, result: str, details: str) -> None:
        self.events.append(
            AuditEvent(
                operation_id=operation_id,
                event=event,
                result=result,
                details=details,
                timestamp=datetime.now(timezone.utc),
            )
        )
