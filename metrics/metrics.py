"""
Simulation metrics calculation and reporting module.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class SimulationMetrics:
    protocol_name: str
    window_size: int
    num_frames: int
    transmission_delay: float
    ack_delay: float
    packet_loss_pct: float
    ack_loss_pct: float
    timeout: float
    
    total_transmissions: int = 0
    retransmissions: int = 0
    packets_lost: int = 0
    unique_packets_lost: int = 0
    acks_sent: int = 0
    acks_lost: int = 0
    acks_received: int = 0
    total_time_ms: float = 0.0
    throughput_fps: float = 0.0
    efficiency_pct: float = 0.0

    def calculate(self):
        """Calculate derived metrics throughput and efficiency."""
        # Total time in seconds
        time_sec = self.total_time_ms / 1000.0 if self.total_time_ms > 0 else 1.0
        
        # Frame Throughput = Delivered frames / Total Time (sec)
        self.throughput_fps = round(self.num_frames / time_sec, 2)
        
        # Efficiency % = (Useful Transmissions / Total Transmissions) * 100
        if self.total_transmissions > 0:
            self.efficiency_pct = round((self.num_frames / self.total_transmissions) * 100.0, 2)
        else:
            self.efficiency_pct = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def summary_text(self) -> str:
        return (
            "========================================\n"
            "        SIMULATION RESULTS\n"
            "========================================\n\n"
            f"Protocol              : {self.protocol_name}\n"
            f"Window Size           : {self.window_size}\n"
            f"Original Frames       : {self.num_frames}\n"
            f"Total Transmissions   : {self.total_transmissions}\n"
            f"Retransmissions       : {self.retransmissions}\n"
            f"Packets Lost (Total)  : {self.packets_lost}\n"
            f"Unique Packets Lost   : {self.unique_packets_lost}\n"
            f"ACKs Received         : {self.acks_received}\n"
            f"Total Time            : {self.total_time_ms:.1f} ms\n"
            f"Frame Throughput      : {self.throughput_fps:.2f} frames/sec\n"
            f"Efficiency            : {self.efficiency_pct:.2f}%\n"
        )
