"""
Selective Repeat Sliding Window Protocol.
"""

from typing import List, Tuple
from protocols.base import BaseProtocol, FrameStatus


class SelectiveRepeatProtocol(BaseProtocol):
    def __init__(self, num_frames: int, window_size: int, timeout: float):
        super().__init__(num_frames=num_frames, window_size=window_size, timeout=timeout)

    def name(self) -> str:
        return "Selective Repeat"

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
        # Receiver window is [rcv_base, rcv_base + window_size - 1]
        if self.rcv_base <= frame_index < self.rcv_base + self.window_size:
            self.received_frames.add(frame_index)
            self.buffered_frames.add(frame_index)
            
            # Slide rcv_base if possible
            while self.rcv_base in self.buffered_frames:
                self.rcv_base += 1
                
            return True, frame_index, f"Frame {frame_index} accepted into buffer. Sending individual ACK {frame_index}"
        elif frame_index < self.rcv_base:
            # Already accepted frame, re-send ACK
            return False, frame_index, f"Duplicate Frame {frame_index} received. Re-sending ACK {frame_index}"
        else:
            # Outside receiver window
            return False, -1, f"Frame {frame_index} outside receiver window [{self.rcv_base}..{self.rcv_base + self.window_size - 1}]. Ignored."

    def handle_ack_arrival(self, ack_num: int) -> List[int]:
        if ack_num >= 0 and ack_num < self.num_frames:
            self.acked_frames.add(ack_num)
            # Slide send_base past all contiguous acked frames
            while self.send_base in self.acked_frames:
                self.send_base += 1
            return [ack_num]
        return []

    def handle_timeout(self, frame_index: int) -> List[int]:
        # Selective Repeat retransmits ONLY the timed out frame if not yet acked
        if frame_index not in self.acked_frames and frame_index < self.num_frames:
            return [frame_index]
        return []
