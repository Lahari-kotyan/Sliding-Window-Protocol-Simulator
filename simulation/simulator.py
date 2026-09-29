"""
Event-driven simulation engine for Sliding Window Protocols.
"""

import heapq
from typing import List, Dict, Any, Optional
from protocols.base import BaseProtocol, FrameStatus
from simulation.event import Event, EventType
from simulation.network import NetworkChannel
from metrics.metrics import SimulationMetrics


class AnimationSnapshot:
    """Snapshot of simulation state at a specific time for visual animation."""

    def __init__(
        self,
        timestamp: float,
        event: Event,
        send_base: int,
        next_seq_num: int,
        rcv_base: int,
        frame_states: Dict[int, str],
        acked_frames: List[int],
        received_frames: List[int],
        buffered_frames: List[int],
        active_transmissions: List[Dict[str, Any]],
        log_message: str,
    ):
        self.timestamp = timestamp
        self.event = event
        self.send_base = send_base
        self.next_seq_num = next_seq_num
        self.rcv_base = rcv_base
        self.frame_states = dict(frame_states)
        self.acked_frames = list(acked_frames)
        self.received_frames = list(received_frames)
        self.buffered_frames = list(buffered_frames)
        self.active_transmissions = list(active_transmissions)
        self.log_message = log_message


class Simulator:
    def __init__(self, protocol: BaseProtocol, network: NetworkChannel, max_time_ms: float = 120000.0):
        self.protocol = protocol
        self.network = network
        self.max_time_ms = max_time_ms
        self.event_queue: List[Event] = []
        self.current_time = 0.0
        
        self.snapshots: List[AnimationSnapshot] = []
        self.logs: List[str] = []
        self.metrics: Optional[SimulationMetrics] = None

    def _schedule(self, event: Event):
        heapq.heappush(self.event_queue, event)

    def run(self) -> SimulationMetrics:
        """Run the full discrete event simulation deterministically."""
        self.protocol.reset()
        self.network.reset_rng()
        self.event_queue.clear()
        self.snapshots.clear()
        self.logs.clear()
        self.current_time = 0.0

        # Initialize metrics tracking
        metrics = SimulationMetrics(
            protocol_name=self.protocol.name(),
            window_size=self.protocol.window_size,
            num_frames=self.protocol.num_frames,
            transmission_delay=self.network.transmission_delay,
            ack_delay=self.network.ack_delay,
            packet_loss_pct=self.network.packet_loss_rate * 100.0,
            ack_loss_pct=self.network.ack_loss_rate * 100.0,
            timeout=self.protocol.timeout,
        )

        unique_lost_set = set()
        active_in_flight: List[Dict[str, Any]] = []

        # Initial frames to send
        initial_frames = self.protocol.get_sendable_frames()
        for f in initial_frames:
            self._schedule_frame_send(f, 0.0, metrics)

        # Record initial state snapshot
        self._record_snapshot(
            Event(0.0, EventType.FRAME_SEND, details="Simulation Started"),
            "Simulation Started",
            active_in_flight,
        )

        # Discrete Event Loop
        while self.event_queue and self.current_time <= self.max_time_ms:
            if len(self.protocol.acked_frames) >= self.protocol.num_frames:
                # All frames successfully delivered and acknowledged!
                break

            event = heapq.heappop(self.event_queue)
            self.current_time = event.timestamp

            log_str = ""

            if event.event_type == EventType.FRAME_SEND:
                # Frame transmission logic
                frame = event.frame_seq
                attempt = event.attempt
                metrics.total_transmissions += 1
                self.protocol.frame_attempts[frame] = attempt

                if attempt > 1:
                    metrics.retransmissions += 1

                is_lost = self.network.is_frame_lost()
                event.is_lost = is_lost

                if is_lost:
                    metrics.packets_lost += 1
                    unique_lost_set.add(frame)
                    self.protocol.frame_states[frame] = FrameStatus.LOST
                    log_str = f"[{self.current_time:.0f} ms] Frame {frame} LOST (Attempt #{attempt})"
                    self.logs.append(log_str)
                    
                    # Schedule timeout for lost frame
                    timeout_ev = Event(
                        timestamp=self.current_time + self.protocol.timeout,
                        event_type=EventType.TIMEOUT,
                        frame_seq=frame,
                        attempt=attempt,
                        details=f"Timeout for Frame {frame}",
                    )
                    self._schedule(timeout_ev)

                    # Visual in-flight entry for animation
                    active_in_flight.append({
                        "id": f"F-{frame}-{attempt}",
                        "type": "FRAME",
                        "seq": frame,
                        "start_time": self.current_time,
                        "end_time": self.current_time + self.network.transmission_delay,
                        "is_lost": True,
                        "progress": 0.0,
                    })
                else:
                    self.protocol.frame_states[frame] = FrameStatus.IN_TRANSIT
                    log_str = f"[{self.current_time:.0f} ms] Sending Frame {frame} (Attempt #{attempt})"
                    self.logs.append(log_str)

                    # Schedule Frame Arrival at Receiver
                    arr_time = self.network.get_frame_arrival_time(self.current_time)
                    arr_ev = Event(
                        timestamp=arr_time,
                        event_type=EventType.FRAME_ARRIVE,
                        frame_seq=frame,
                        attempt=attempt,
                        details=f"Frame {frame} Arrived",
                    )
                    self._schedule(arr_ev)

                    # Schedule Timeout at Sender
                    timeout_ev = Event(
                        timestamp=self.current_time + self.protocol.timeout,
                        event_type=EventType.TIMEOUT,
                        frame_seq=frame,
                        attempt=attempt,
                        details=f"Timeout for Frame {frame}",
                    )
                    self._schedule(timeout_ev)

                    active_in_flight.append({
                        "id": f"F-{frame}-{attempt}",
                        "type": "FRAME",
                        "seq": frame,
                        "start_time": self.current_time,
                        "end_time": arr_time,
                        "is_lost": False,
                        "progress": 0.0,
                    })

            elif event.event_type == EventType.FRAME_ARRIVE:
                frame = event.frame_seq
                accepted, ack_num, rx_msg = self.protocol.handle_frame_arrival(frame)
                
                if accepted:
                    self.protocol.frame_states[frame] = FrameStatus.RECEIVED

                log_str = f"[{self.current_time:.0f} ms] {rx_msg}"
                self.logs.append(log_str)

                # Send ACK back if valid ack_num
                if ack_num >= 0:
                    metrics.acks_sent += 1
                    is_ack_lost = self.network.is_ack_lost()
                    
                    if is_ack_lost:
                        metrics.acks_lost += 1
                        ack_log = f"[{self.current_time:.0f} ms] ACK {ack_num} LOST in channel"
                        self.logs.append(ack_log)
                        
                        active_in_flight.append({
                            "id": f"ACK-{ack_num}-{event.event_counter}",
                            "type": "ACK",
                            "seq": ack_num,
                            "start_time": self.current_time,
                            "end_time": self.current_time + self.network.ack_delay,
                            "is_lost": True,
                            "progress": 0.0,
                        })
                    else:
                        ack_arr_time = self.network.get_ack_arrival_time(self.current_time)
                        ack_ev = Event(
                            timestamp=ack_arr_time,
                            event_type=EventType.ACK_ARRIVE,
                            ack_seq=ack_num,
                            frame_seq=frame,
                            details=f"ACK {ack_num} Arrived",
                        )
                        self._schedule(ack_ev)

                        active_in_flight.append({
                            "id": f"ACK-{ack_num}-{event.event_counter}",
                            "type": "ACK",
                            "seq": ack_num,
                            "start_time": self.current_time,
                            "end_time": ack_arr_time,
                            "is_lost": False,
                            "progress": 0.0,
                        })

            elif event.event_type == EventType.ACK_ARRIVE:
                ack_num = event.ack_seq
                metrics.acks_received += 1
                newly_acked = self.protocol.handle_ack_arrival(ack_num)
                
                for acked_f in newly_acked:
                    self.protocol.frame_states[acked_f] = FrameStatus.ACKED

                log_str = f"[{self.current_time:.0f} ms] ACK {ack_num} received at sender"
                self.logs.append(log_str)

                # Check if new frames can now be transmitted
                new_sendable = self.protocol.get_sendable_frames()
                for f in new_sendable:
                    self._schedule_frame_send(f, self.current_time, metrics)

            elif event.event_type == EventType.TIMEOUT:
                frame = event.frame_seq
                # Check if timeout is still relevant
                retransmit_frames = self.protocol.handle_timeout(frame)
                
                if retransmit_frames:
                    log_str = f"[{self.current_time:.0f} ms] Timeout for Frame {frame}! Retransmitting: {retransmit_frames}"
                    self.logs.append(log_str)
                    
                    for rf in retransmit_frames:
                        self.protocol.frame_states[rf] = FrameStatus.TIMED_OUT
                        attempt = self.protocol.frame_attempts[rf] + 1
                        self._schedule_frame_send(rf, self.current_time, metrics, attempt=attempt)
                else:
                    log_str = f"[{self.current_time:.0f} ms] Timeout for Frame {frame} ignored (already ACKed)"

            # Filter completed in-flight items
            active_in_flight = [item for item in active_in_flight if item["end_time"] >= self.current_time]
            self._record_snapshot(event, log_str, active_in_flight)

        # Finalize metrics
        metrics.total_time_ms = self.current_time
        metrics.unique_packets_lost = len(unique_lost_set)
        metrics.calculate()
        self.metrics = metrics

        # Record final completion snapshot
        self._record_snapshot(
            Event(self.current_time, EventType.ACK_ARRIVE, details="Simulation Completed"),
            f"[{self.current_time:.0f} ms] Simulation Completed Successfully",
            [],
        )

        return metrics

    def _schedule_frame_send(self, frame_seq: int, time: float, metrics: SimulationMetrics, attempt: int = 1):
        send_ev = Event(
            timestamp=time,
            event_type=EventType.FRAME_SEND,
            frame_seq=frame_seq,
            attempt=attempt,
            details=f"Sending Frame {frame_seq}",
        )
        self._schedule(send_ev)

    def _record_snapshot(self, event: Event, log_msg: str, active_in_flight: List[Dict[str, Any]]):
        snap = AnimationSnapshot(
            timestamp=self.current_time,
            event=event,
            send_base=self.protocol.send_base,
            next_seq_num=self.protocol.next_seq_num,
            rcv_base=self.protocol.rcv_base,
            frame_states=self.protocol.frame_states,
            acked_frames=list(self.protocol.acked_frames),
            received_frames=list(self.protocol.received_frames),
            buffered_frames=list(self.protocol.buffered_frames),
            active_transmissions=list(active_in_flight),
            log_message=log_msg,
        )
        self.snapshots.append(snap)
