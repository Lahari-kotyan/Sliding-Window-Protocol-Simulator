"""
Go-Back-N Sliding Window Protocol.
"""

from typing import List, Tuple
from protocols.base import BaseProtocol, FrameStatus


class GoBackNProtocol(BaseProtocol):
    def __init__(self, num_frames: int, window_size: int, timeout: float):
        super().__init__(num_frames=num_frames, window_size=window_size, timeout=timeout)

    def name(self) -> str:
        return "Go-Back-N"

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
        sendable = []
        while self.next_seq_num < self.send_base + self.window_size and self.next_seq_num < self.num_frames:
            sendable.append(self.next_seq_num)
            self.next_seq_num += 1
        return sendable

    def handle_frame_arrival(self, frame_index: int) -> Tuple[bool, int, str]:
        if frame_index == self.rcv_base:
            self.received_frames.add(frame_index)
            self.rcv_base += 1
            return True, frame_index, f"Frame {frame_index} accepted in-order. Sending cumulative ACK {frame_index}"
        else:
            ack_to_send = self.rcv_base - 1
            return False, ack_to_send, f"Frame {frame_index} out-of-order (expected {self.rcv_base}). Re-sending cumulative ACK {ack_to_send}"

    def handle_ack_arrival(self, ack_num: int) -> List[int]:
        if ack_num >= self.send_base:
            newly_acked = []
            for f in range(self.send_base, ack_num + 1):
                if f not in self.acked_frames:
                    self.acked_frames.add(f)
                    newly_acked.append(f)
            self.send_base = ack_num + 1
            return newly_acked
        return []

    def handle_timeout(self, frame_index: int) -> List[int]:
        # GBN retransmits all frames in window starting from send_base, ONLY if frame_index is still the send_base
        if frame_index == self.send_base and self.send_base not in self.acked_frames and self.send_base < self.next_seq_num:
            return list(range(self.send_base, self.next_seq_num))
        return []
