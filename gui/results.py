"""
Results Dashboard panel and CSV export handler.
"""

import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Optional
from metrics.metrics import SimulationMetrics


class ResultsPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.metrics_data: List[SimulationMetrics] = []

        self.create_widgets()

    def create_widgets(self):
        # Header title
        header_lbl = ttk.Label(self, text="Simulation Results Dashboard", font=("Segoe UI", 14, "bold"))
        header_lbl.pack(anchor="w", pady=(0, 10))

        # Text Summary Box
        self.text_frame = ttk.LabelFrame(self, text="Detailed Metric Report", padding=10)
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.report_text = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#181825",
            fg="#cdd6f4",
            insertbackground="#ffffff",
            height=14,
        )
        scrollbar = ttk.Scrollbar(self.text_frame, command=self.report_text.yview)
        self.report_text.config(yscrollcommand=scrollbar.set)
        
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Export Button Frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10)

        export_btn = ttk.Button(btn_frame, text="Export Results to CSV", command=self.export_csv)
        export_btn.pack(side=tk.LEFT, padx=5)

    def display_metrics(self, metrics: SimulationMetrics):
        self.metrics_data = [metrics]
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, metrics.summary_text())

    def display_comparison_metrics(self, metrics_dict: Dict[str, SimulationMetrics]):
        self.metrics_data = list(metrics_dict.values())
        self.report_text.delete("1.0", tk.END)

        header = (
            "=========================================================================\n"
            "                      PROTOCOL COMPARISON DASHBOARD                      \n"
            "=========================================================================\n\n"
            f"{'Metric':<25} | {'One-Bit SW':<15} | {'Go-Back-N':<15} | {'Selective Repeat':<15}\n"
            "-------------------------------------------------------------------------\n"
        )
        self.report_text.insert(tk.END, header)

        def get_val(p_name, attr, fmt="{}"):
            m = metrics_dict.get(p_name)
            if not m:
                return "N/A"
            v = getattr(m, attr)
            return fmt.format(v)

        rows = [
            ("Window Size", "window_size", "{}"),
            ("Total Transmissions", "total_transmissions", "{}"),
            ("Retransmissions", "retransmissions", "{}"),
            ("Packets Lost (Total)", "packets_lost", "{}"),
            ("Unique Packets Lost", "unique_packets_lost", "{}"),
            ("ACKs Received", "acks_received", "{}"),
            ("Total Time (ms)", "total_time_ms", "{:.1f}"),
            ("Throughput (fps)", "throughput_fps", "{:.2f}"),
            ("Efficiency (%)", "efficiency_pct", "{:.2f}%"),
        ]

        for label, attr, fmt in rows:
            ob = get_val("One-Bit Sliding Window", attr, fmt)
            gbn = get_val("Go-Back-N", attr, fmt)
            sr = get_val("Selective Repeat", attr, fmt)
            line = f"{label:<25} | {ob:<15} | {gbn:<15} | {sr:<15}\n"
            self.report_text.insert(tk.END, line)

        self.report_text.insert(tk.END, "-------------------------------------------------------------------------\n")

    def export_csv(self):
        if not self.metrics_data:
            messagebox.showwarning("No Data", "No simulation results available to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Simulation Results to CSV",
        )
        if not file_path:
            return

        fieldnames = [
            "Protocol",
            "Window Size",
            "Number of Frames",
            "Transmission Delay",
            "ACK Delay",
            "Packet Loss",
            "ACK Loss",
            "Timeout",
            "Total Transmissions",
            "Retransmissions",
            "Packets Lost",
            "ACKs Received",
            "Total Transmission Time",
            "Throughput",
            "Efficiency",
        ]

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for m in self.metrics_data:
                    writer.writerow({
                        "Protocol": m.protocol_name,
                        "Window Size": m.window_size,
                        "Number of Frames": m.num_frames,
                        "Transmission Delay": m.transmission_delay,
                        "ACK Delay": m.ack_delay,
                        "Packet Loss": f"{m.packet_loss_pct:.1f}%",
                        "ACK Loss": f"{m.ack_loss_pct:.1f}%",
                        "Timeout": m.timeout,
                        "Total Transmissions": m.total_transmissions,
                        "Retransmissions": m.retransmissions,
                        "Packets Lost": m.packets_lost,
                        "ACKs Received": m.acks_received,
                        "Total Transmission Time": m.total_time_ms,
                        "Throughput": m.throughput_fps,
                        "Efficiency": f"{m.efficiency_pct:.2f}%",
                    })
            messagebox.showinfo("Export Successful", f"Results successfully exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred while writing CSV:\n{str(e)}")
