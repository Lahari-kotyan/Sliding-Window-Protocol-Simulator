"""
Event definition for discrete-event network simulation.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, Optional


class EventType(Enum):
    FRAME_SEND = "FRAME_SEND"
    FRAME_ARRIVE = "FRAME_ARRIVE"
    ACK_SEND = "ACK_SEND"
    ACK_ARRIVE = "ACK_ARRIVE"
    TIMEOUT = "TIMEOUT"


_event_counter = 0

@dataclass(order=True)
class Event:
    timestamp: float
    event_counter: int = field(init=False, repr=False)
    event_type: EventType = field(compare=False)
    frame_seq: int = field(compare=False, default=-1)
    ack_seq: int = field(compare=False, default=-1)
    attempt: int = field(compare=False, default=1)
    is_lost: bool = field(compare=False, default=False)
    details: str = field(compare=False, default="")
    extra_data: Optional[dict] = field(compare=False, default=None)

    def __post_init__(self):
        global _event_counter
        _event_counter += 1
        self.event_counter = _event_counter
