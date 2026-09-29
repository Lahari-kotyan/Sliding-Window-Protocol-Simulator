"""
Tkinter visual canvas for network packet animation and window state rendering.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
from simulation.simulator import AnimationSnapshot
from protocols.base import FrameStatus


class NetworkAnimationCanvas(tk.Frame):
    def __init__(self, parent, width=800, height=360):
        super().__init__(parent, bg="#1e1e2e")
        self.canvas_width = width
        self.canvas_height = height

        self.canvas = tk.Canvas(
            self,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#181825",
            highlightthickness=1,
            highlightbackground="#313244",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.snapshots: List[AnimationSnapshot] = []
        self.current_step = 0
        self.num_frames = 10
        self.window_size = 4
        self.protocol_name = "Go-Back-N"

        self.color_map = {
            FrameStatus.UNSENT: "#45475a",
            FrameStatus.IN_TRANSIT: "#89b4fa",
            FrameStatus.RECEIVED: "#f9e2af",
            FrameStatus.ACKED: "#a6e3a1",
            FrameStatus.LOST: "#f38ba8",
            FrameStatus.TIMED_OUT: "#fab387",
            FrameStatus.RETRANSMITTED: "#cba6f7",
        }

        self.draw_initial_layout()

    def set_data(self, snapshots: List[AnimationSnapshot], num_frames: int, window_size: int, protocol_name: str):
        self.snapshots = snapshots
        self.num_frames = num_frames
        self.window_size = window_size
        self.protocol_name = protocol_name
        self.current_step = 0
        self.render_step(0)

    def draw_initial_layout(self):
        self.canvas.delete("all")

        # Sender & Receiver Node Lines
        sender_y = 70
        receiver_y = 270

        # Background channel area
        self.canvas.create_rectangle(40, sender_y - 20, self.canvas_width - 40, sender_y + 35, fill="#1e1e2e", outline="#313244")
        self.canvas.create_rectangle(40, receiver_y - 20, self.canvas_width - 40, receiver_y + 35, fill="#1e1e2e", outline="#313244")

        # Node Labels
        self.canvas.create_text(80, sender_y - 35, text="SENDER", fill="#cdd6f4", font=("Segoe UI", 11, "bold"))
        self.canvas.create_text(80, receiver_y - 35, text="RECEIVER", fill="#cdd6f4", font=("Segoe UI", 11, "bold"))

        # Channel connection arrows
        self.canvas.create_text(self.canvas_width / 2, 170, text="◄─ NETWORK CHANNEL ─►", fill="#585b70", font=("Segoe UI", 9, "bold"))

        # Legend
        self.draw_legend()

    def draw_legend(self):
        legend_y = self.canvas_height - 25
        start_x = 50
        spacing = 100

        items = [
            ("Unsent", "#45475a"),
            ("In Transit", "#89b4fa"),
            ("Received", "#f9e2af"),
            ("ACKed", "#a6e3a1"),
            ("Lost (X)", "#f38ba8"),
            ("Timed Out", "#fab387"),
        ]

        for i, (label, color) in enumerate(items):
            x = start_x + i * spacing
            self.canvas.create_rectangle(x, legend_y - 6, x + 12, legend_y + 6, fill=color, outline="#cdd6f4")
            self.canvas.create_text(x + 20, legend_y, text=label, fill="#a6adc8", font=("Segoe UI", 8), anchor="w")

    def render_step(self, step_idx: int):
        self.canvas.delete("all")
        self.draw_initial_layout()

        if not self.snapshots or step_idx >= len(self.snapshots):
            return

        snap = self.snapshots[step_idx]
        self.current_step = step_idx

        # Time header
        self.canvas.create_text(
            self.canvas_width - 120,
            30,
            text=f"Simulated Time: {snap.timestamp:.0f} ms",
            fill="#f9e2af",
            font=("Segoe UI", 11, "bold"),
        )

        sender_y = 70
        receiver_y = 270
        slot_width = min(60, (self.canvas_width - 120) // max(self.num_frames, 1))
        start_x = 140

        # Draw Sender Frame Slots
        for i in range(self.num_frames):
            x1 = start_x + i * slot_width
            x2 = x1 + slot_width - 5
            status = snap.frame_states.get(i, FrameStatus.UNSENT)
            color = self.color_map.get(status, "#45475a")

            self.canvas.create_rectangle(x1, sender_y - 12, x2, sender_y + 20, fill=color, outline="#cdd6f4", width=1.5)
            self.canvas.create_text((x1 + x2) / 2, sender_y + 4, text=f"F{i}", fill="#11111b", font=("Segoe UI", 9, "bold"))

        # Draw Sender Window Box
        if self.protocol_name != "One-Bit Sliding Window":
            win_x1 = start_x + snap.send_base * slot_width - 3
            win_x2 = start_x + min(snap.send_base + self.window_size, self.num_frames) * slot_width - 2
            if snap.send_base < self.num_frames:
                self.canvas.create_rectangle(win_x1, sender_y - 16, win_x2, sender_y + 24, outline="#f5e0dc", width=2, dash=(4, 2))
                self.canvas.create_text(win_x1 + 10, sender_y - 25, text=f"Sender Window [{snap.send_base}..{min(snap.send_base + self.window_size - 1, self.num_frames - 1)}]", fill="#f5e0dc", font=("Segoe UI", 8, "bold"), anchor="w")
        else:
            # One Bit Window
            win_x1 = start_x + snap.send_base * slot_width - 3
            win_x2 = start_x + min(snap.send_base + 1, self.num_frames) * slot_width - 2
            if snap.send_base < self.num_frames:
                self.canvas.create_rectangle(win_x1, sender_y - 16, win_x2, sender_y + 24, outline="#f5e0dc", width=2, dash=(4, 2))

        # Draw Receiver Frame Slots
        for i in range(self.num_frames):
            x1 = start_x + i * slot_width
            x2 = x1 + slot_width - 5
            is_rx = i in snap.received_frames
            is_buf = i in snap.buffered_frames
            
            if is_rx:
                color = "#a6e3a1"
            elif is_buf:
                color = "#f9e2af"
            else:
                color = "#45475a"

            self.canvas.create_rectangle(x1, receiver_y - 12, x2, receiver_y + 20, fill=color, outline="#cdd6f4", width=1.5)
            self.canvas.create_text((x1 + x2) / 2, receiver_y + 4, text=f"F{i}", fill="#11111b", font=("Segoe UI", 9, "bold"))

        # Draw Receiver Base / Window
        rcv_x1 = start_x + snap.rcv_base * slot_width - 3
        if self.protocol_name == "Selective Repeat":
            rcv_x2 = start_x + min(snap.rcv_base + self.window_size, self.num_frames) * slot_width - 2
            if snap.rcv_base < self.num_frames:
                self.canvas.create_rectangle(rcv_x1, receiver_y - 16, rcv_x2, receiver_y + 24, outline="#94e2d5", width=2, dash=(4, 2))
                self.canvas.create_text(rcv_x1 + 10, receiver_y + 32, text=f"Receiver Window [{snap.rcv_base}..{min(snap.rcv_base + self.window_size - 1, self.num_frames - 1)}]", fill="#94e2d5", font=("Segoe UI", 8, "bold"), anchor="w")
        else:
            if snap.rcv_base < self.num_frames:
                self.canvas.create_text(rcv_x1 + (slot_width/2), receiver_y + 32, text=f"Expected: F{snap.rcv_base}", fill="#94e2d5", font=("Segoe UI", 8, "bold"))

        # Draw active flying packets / ACKs / Lost markers
        for packet in snap.active_transmissions:
            seq = packet["seq"]
            is_lost = packet.get("is_lost", False)
            pkt_type = packet.get("type", "FRAME")
            start_t = packet["start_time"]
            end_t = packet["end_time"]
            
            progress = 0.5
            if end_t > start_t:
                progress = min(1.0, max(0.0, (snap.timestamp - start_t) / (end_t - start_t)))

            center_x = start_x + seq * slot_width + (slot_width / 2) - 2.5

            if pkt_type == "FRAME":
                if is_lost:
                    # Traveled halfway down, then lost X
                    y = sender_y + progress * (receiver_y - sender_y) * 0.6
                    self.canvas.create_oval(center_x - 10, y - 10, center_x + 10, y + 10, fill="#f38ba8", outline="#ffffff", width=2)
                    self.canvas.create_text(center_x, y, text="X", fill="#ffffff", font=("Segoe UI", 12, "bold"))
                    self.canvas.create_text(center_x + 22, y, text=f"F{seq} LOST", fill="#f38ba8", font=("Segoe UI", 8, "bold"), anchor="w")
                else:
                    y = sender_y + progress * (receiver_y - sender_y)
                    self.canvas.create_rectangle(center_x - 14, y - 10, center_x + 14, y + 10, fill="#89b4fa", outline="#ffffff", width=1.5)
                    self.canvas.create_text(center_x, y, text=f"F{seq}", fill="#11111b", font=("Segoe UI", 8, "bold"))
            else: # ACK
                if is_lost:
                    y = receiver_y - progress * (receiver_y - sender_y) * 0.6
                    self.canvas.create_oval(center_x - 10, y - 10, center_x + 10, y + 10, fill="#fab387", outline="#ffffff", width=2)
                    self.canvas.create_text(center_x, y, text="X", fill="#ffffff", font=("Segoe UI", 12, "bold"))
                    self.canvas.create_text(center_x + 22, y, text=f"ACK{seq} LOST", fill="#fab387", font=("Segoe UI", 8, "bold"), anchor="w")
                else:
                    y = receiver_y - progress * (receiver_y - sender_y)
                    self.canvas.create_oval(center_x - 12, y - 12, center_x + 12, y + 12, fill="#a6e3a1", outline="#ffffff", width=1.5)
                    self.canvas.create_text(center_x, y, text=f"A{seq}", fill="#11111b", font=("Segoe UI", 8, "bold"))

        # Bottom log snippet
        self.canvas.create_text(40, self.canvas_height - 50, text=snap.log_message, fill="#cdd6f4", font=("Consolas", 10), anchor="w")
