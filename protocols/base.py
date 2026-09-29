"""
Base protocol state and abstract representation for sliding window protocols.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Set, Optional


class FrameStatus:
    UNSENT = "UNSENT"
    IN_TRANSIT = "IN_TRANSIT"
    RECEIVED = "RECEIVED"
    ACKED = "ACKED"
    LOST = "LOST"
    TIMED_OUT = "TIMED_OUT"
    RETRANSMITTED = "RETRANSMITTED"


class BaseProtocol(ABC):
    def __init__(self, num_frames: int, window_size: int, timeout: float):
        self.num_frames = num_frames
        self.window_size = window_size
        self.timeout = timeout
        
        # State variables
        self.send_base = 0
        self.next_seq_num = 0
        self.rcv_base = 0
        
        # Tracking states for frames
        self.frame_states: Dict[int, str] = {i: FrameStatus.UNSENT for i in range(num_frames)}
        self.frame_attempts: Dict[int, int] = {i: 0 for i in range(num_frames)}
        self.acked_frames: Set[int] = set()
        self.received_frames: Set[int] = set()
        self.buffered_frames: Set[int] = set()

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def reset(self):
        pass
