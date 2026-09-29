"""
Network channel simulation with probabilistic loss and delays.
"""

import random
from typing import Optional


class NetworkChannel:
    def __init__(
        self,
        transmission_delay: float = 100.0,
        ack_delay: float = 50.0,
        packet_loss_pct: float = 10.0,
        ack_loss_pct: float = 5.0,
        seed: Optional[int] = None,
    ):
        self.transmission_delay = float(transmission_delay)
        self.ack_delay = float(ack_delay)
        self.packet_loss_rate = float(packet_loss_pct) / 100.0
        self.ack_loss_rate = float(ack_loss_pct) / 100.0
        self.seed = seed
        self.rng = random.Random(seed)

    def reset_rng(self, seed: Optional[int] = None):
        if seed is not None:
            self.seed = seed
        self.rng = random.Random(self.seed)

    def is_frame_lost(self) -> bool:
        return self.rng.random() < self.packet_loss_rate

    def is_ack_lost(self) -> bool:
        return self.rng.random() < self.ack_loss_rate

    def get_frame_arrival_time(self, send_time: float) -> float:
        return send_time + self.transmission_delay

    def get_ack_arrival_time(self, send_time: float) -> float:
        return send_time + self.ack_delay
