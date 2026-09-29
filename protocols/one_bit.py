"""
One-Bit / Alternating Bit Sliding Window Protocol.
"""

from typing import List, Tuple
from protocols.base import BaseProtocol, FrameStatus


class OneBitProtocol(BaseProtocol):
    def __init__(self, num_frames: int, timeout: float):
        super().__init__(num_frames=num_frames, window_size=1, timeout=timeout)

    def name(self) -> str:
        return "One-Bit Sliding Window"

    def reset(self):
        self.send_base = 0
        self.next_seq_num = 0
        self.rcv_base = 0
        self.frame_states = {i: FrameStatus.UNSENT for i in range(self.num_frames)}
        self.frame_attempts = {i: 0 for i in range(self.num_frames)}
        self.acked_frames.clear()
        self.received_frames.clear()
        self.buffered_frames.clear()

    def get_sendable_frames(self) -> List[int]:
        if self.send_base < self.num_frames and self.next_seq_num == self.send_base:
            frame_to_send = self.next_seq_num
            self.next_seq_num += 1
            return [frame_to_send]
        return []

    def handle_frame_arrival(self, frame_index: int) -> Tuple[bool, int, str]:
        if frame_index == self.rcv_base:
            self.received_frames.add(frame_index)
            self.rcv_base += 1
            return True, frame_index, f"Frame {frame_index} (Seq {frame_index % 2}) accepted. Sending ACK {frame_index}"
        else:
            ack_to_send = self.rcv_base - 1
            if ack_to_send < 0:
                ack_to_send = frame_index
            return False, ack_to_send, f"Duplicate Frame {frame_index} received. Re-sending ACK {ack_to_send}"

    def handle_ack_arrival(self, ack_num: int) -> List[int]:
        if ack_num == self.send_base:
            self.acked_frames.add(ack_num)
            self.send_base += 1
            return [ack_num]
        return []

    def handle_timeout(self, frame_index: int) -> List[int]:
        if frame_index == self.send_base and frame_index not in self.acked_frames:
            return [frame_index]
        return []
