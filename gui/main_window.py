"""
Main GUI application window for Computer Networks Sliding Window Simulator.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, List

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from protocols.one_bit import OneBitProtocol
from protocols.go_back_n import GoBackNProtocol
from protocols.selective_repeat import SelectiveRepeatProtocol
from simulation.network import NetworkChannel
from simulation.simulator import Simulator, AnimationSnapshot
from metrics.metrics import SimulationMetrics
from gui.animation import NetworkAnimationCanvas
from gui.results import ResultsPanel
from visualization.graphs import create_comparison_figure, create_loss_sensitivity_figure


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Computer Networks Sliding Window Protocol Simulator")
        self.geometry("1100x780")
        self.minsize(980, 680)

        # Simulation state
        self.simulator: Optional[Simulator] = None
        self.snapshots: List[AnimationSnapshot] = []
        self.current_step = 0
        self.is_playing = False
        self.anim_job = None
        self.speed_ms = 300  # Delay between steps in ms

        self.setup_styles()
        self.create_layout()

        # Bind notebook tab change listener
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Auto-run initial comparison on startup after main loop initializes
        self.after(100, self.compare_protocols)

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Configure custom colors
        style.configure(".", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 9))
        style.configure("TFrame", background="#1e1e2e")
        style.configure("TLabelframe", background="#1e1e2e", foreground="#cdd6f4", bordercolor="#313244")
        style.configure("TLabelframe.Label", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4")
        style.configure("TButton", background="#313244", foreground="#cdd6f4", font=("Segoe UI", 9, "bold"), borderwidth=0)
        style.map("TButton", background=[("active", "#45475a")])
        style.configure("Accent.TButton", background="#89b4fa", foreground="#11111b", font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#b4befe")])
        style.configure("TNotebook", background="#1e1e2e", borderwidth=0)
        style.configure("TNotebook.Tab", background="#313244", foreground="#cdd6f4", padding=[10, 5], font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#89b4fa")], foreground=[("selected", "#11111b")])

    def create_layout(self):
        main_container = ttk.Frame(self, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Top Control Frame (Parameters & Buttons)
        top_frame = ttk.Frame(main_container)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Parameters Panel
        param_lf = ttk.LabelFrame(top_frame, text="Simulation Parameters", padding=10)
        param_lf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Grid inputs
        # Row 0: Protocol
        ttk.Label(param_lf, text="Protocol:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.protocol_var = tk.StringVar(value="Go-Back-N")
        proto_combo = ttk.Combobox(
            param_lf,
            textvariable=self.protocol_var,
            values=["One-Bit Sliding Window", "Go-Back-N", "Selective Repeat"],
            state="readonly",
            width=22,
        )
        proto_combo.grid(row=0, column=1, sticky="w", padx=5, pady=4)
        proto_combo.bind("<<ComboboxSelected>>", self.on_protocol_changed)

        # Row 0: Window Size
        ttk.Label(param_lf, text="Window Size (N):").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.win_size_var = tk.StringVar(value="4")
        self.win_size_entry = ttk.Entry(param_lf, textvariable=self.win_size_var, width=8)
        self.win_size_entry.grid(row=0, column=3, sticky="w", padx=5, pady=4)

        # Row 0: Number of Frames
        ttk.Label(param_lf, text="Total Frames:").grid(row=0, column=4, sticky="w", padx=5, pady=4)
        self.num_frames_var = tk.StringVar(value="10")
        ttk.Entry(param_lf, textvariable=self.num_frames_var, width=8).grid(row=0, column=5, sticky="w", padx=5, pady=4)

        # Row 1: Delays
        ttk.Label(param_lf, text="Trans Delay (ms):").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.trans_delay_var = tk.StringVar(value="100")
        ttk.Entry(param_lf, textvariable=self.trans_delay_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(param_lf, text="ACK Delay (ms):").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.ack_delay_var = tk.StringVar(value="50")
        ttk.Entry(param_lf, textvariable=self.ack_delay_var, width=8).grid(row=1, column=3, sticky="w", padx=5, pady=4)

        ttk.Label(param_lf, text="Timeout (ms):").grid(row=1, column=4, sticky="w", padx=5, pady=4)
        self.timeout_var = tk.StringVar(value="300")
        ttk.Entry(param_lf, textvariable=self.timeout_var, width=8).grid(row=1, column=5, sticky="w", padx=5, pady=4)

        # Row 2: Loss & Seed
        ttk.Label(param_lf, text="Packet Loss (%):").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.pkt_loss_var = tk.StringVar(value="10")
        ttk.Entry(param_lf, textvariable=self.pkt_loss_var, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(param_lf, text="ACK Loss (%):").grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.ack_loss_var = tk.StringVar(value="5")
        ttk.Entry(param_lf, textvariable=self.ack_loss_var, width=8).grid(row=2, column=3, sticky="w", padx=5, pady=4)

        ttk.Label(param_lf, text="Random Seed:").grid(row=2, column=4, sticky="w", padx=5, pady=4)
        self.seed_var = tk.StringVar(value="42")
        ttk.Entry(param_lf, textvariable=self.seed_var, width=8).grid(row=2, column=5, sticky="w", padx=5, pady=4)

        # Control Buttons Panel
        ctrl_lf = ttk.LabelFrame(top_frame, text="Controls", padding=10)
        ctrl_lf.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.start_btn = ttk.Button(ctrl_lf, text="▶ START SIMULATION", style="Accent.TButton", command=self.start_simulation)
        self.start_btn.grid(row=0, column=0, columnspan=2, sticky="ew", pady=2)

        self.pause_btn = ttk.Button(ctrl_lf, text="⏸ Pause", command=self.pause_animation, state="disabled")
        self.pause_btn.grid(row=1, column=0, padx=2, pady=2)

        self.resume_btn = ttk.Button(ctrl_lf, text="▶ Resume", command=self.resume_animation, state="disabled")
        self.resume_btn.grid(row=1, column=1, padx=2, pady=2)

        self.reset_btn = ttk.Button(ctrl_lf, text="↺ Reset", command=self.reset_simulation)
        self.reset_btn.grid(row=2, column=0, padx=2, pady=2)

        self.stop_btn = ttk.Button(ctrl_lf, text="⏹ Stop", command=self.stop_simulation, state="disabled")
        self.stop_btn.grid(row=2, column=1, padx=2, pady=2)

        self.compare_btn = ttk.Button(ctrl_lf, text="📊 COMPARE ALL PROTOCOLS", command=self.compare_protocols)
        self.compare_btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 2))

        # Speed slider
        speed_frame = ttk.Frame(ctrl_lf)
        speed_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=4)
        ttk.Label(speed_frame, text="Speed:", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=2)
        self.speed_slider = ttk.Scale(speed_frame, from_=10, to=800, orient=tk.HORIZONTAL, command=self.on_speed_changed)
        self.speed_slider.set(300)
        self.speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Notebook Tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Animation Canvas & Live Logs
        self.tab_sim = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sim, text="Interactive Simulation")

        self.anim_canvas = NetworkAnimationCanvas(self.tab_sim, width=950, height=340)
        self.anim_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Live Log Frame
        log_lf = ttk.LabelFrame(self.tab_sim, text="Live Simulation Log", padding=5)
        log_lf.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_text = tk.Text(
            log_lf,
            wrap=tk.WORD,
            height=8,
            font=("Consolas", 9),
            bg="#181825",
            fg="#a6adc8",
            insertbackground="#ffffff",
        )
        log_scroll = ttk.Scrollbar(log_lf, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Tab 2: Results Dashboard
        self.tab_results = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_results, text="Results Dashboard")
        self.results_panel = ResultsPanel(self.tab_results)
        self.results_panel.pack(fill=tk.BOTH, expand=True)

        # Tab 3: Comparison & Graphs
        self.tab_compare = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_compare, text="Protocol Comparison & Graphs")

        # Tab 3 Toolbar
        tab3_bar = ttk.Frame(self.tab_compare, padding=5)
        tab3_bar.pack(fill=tk.X)

        btn_bar = ttk.Button(tab3_bar, text="📊 Bar Chart Comparison", command=self.compare_protocols)
        btn_bar.pack(side=tk.LEFT, padx=5)

        btn_sens = ttk.Button(tab3_bar, text="📈 Packet Loss Sensitivity Curves", command=self.show_loss_sensitivity)
        btn_sens.pack(side=tk.LEFT, padx=5)

        self.graph_container = ttk.Frame(self.tab_compare)
        self.graph_container.pack(fill=tk.BOTH, expand=True)
        self.canvas_widget = None

        # Tab 4: Protocol Information & Educational Guide
        self.tab_info = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_info, text="Protocol Guide & Theory")
        self.create_info_tab()

    def on_tab_changed(self, event=None):
        selected_tab = self.notebook.select()
        if selected_tab == str(self.tab_compare) and self.canvas_widget is None:
            self.compare_protocols()

    def on_protocol_changed(self, event=None):
        proto = self.protocol_var.get()
        if proto == "One-Bit Sliding Window":
            self.win_size_var.set("1")
            self.win_size_entry.config(state="disabled")
        else:
            self.win_size_entry.config(state="normal")
            if self.win_size_var.get() == "1":
                self.win_size_var.set("4")

    def validate_inputs(self) -> Optional[Dict[str, Any]]:
        try:
            proto_name = self.protocol_var.get()
            win_size = int(self.win_size_var.get())
            num_frames = int(self.num_frames_var.get())
            trans_delay = float(self.trans_delay_var.get())
            ack_delay = float(self.ack_delay_var.get())
            timeout = float(self.timeout_var.get())
            pkt_loss = float(self.pkt_loss_var.get())
            ack_loss = float(self.ack_loss_var.get())
            
            seed_str = self.seed_var.get().strip()
            seed = int(seed_str) if seed_str else None

            if proto_name == "One-Bit Sliding Window":
                win_size = 1

            if win_size < 1:
                raise ValueError("Window Size must be at least 1.")
            if num_frames < 1:
                raise ValueError("Number of Frames must be at least 1.")
            if trans_delay <= 0 or ack_delay <= 0 or timeout <= 0:
                raise ValueError("Delays and Timeout must be strictly positive numbers.")
            if not (0.0 <= pkt_loss <= 100.0) or not (0.0 <= ack_loss <= 100.0):
                raise ValueError("Packet and ACK Loss percentages must be between 0 and 100.")
            if timeout <= (trans_delay + ack_delay):
                messagebox.showwarning(
                    "Aggressive Timeout Warning",
                    f"Timeout ({timeout} ms) is less than Round-Trip Time ({trans_delay + ack_delay} ms).\n"
                    "This will trigger premature timeouts!",
                )

            return {
                "proto_name": proto_name,
                "win_size": win_size,
                "num_frames": num_frames,
                "trans_delay": trans_delay,
                "ack_delay": ack_delay,
                "timeout": timeout,
                "pkt_loss": pkt_loss,
                "ack_loss": ack_loss,
                "seed": seed,
            }
        except ValueError as ve:
            messagebox.showerror("Invalid Parameters", str(ve))
            return None

    def start_simulation(self):
        params = self.validate_inputs()
        if not params:
            return

        self.stop_simulation()

        # Build protocol instance
        if params["proto_name"] == "One-Bit Sliding Window":
            protocol = OneBitProtocol(params["num_frames"], params["timeout"])
        elif params["proto_name"] == "Go-Back-N":
            protocol = GoBackNProtocol(params["num_frames"], params["win_size"], params["timeout"])
        else:
            protocol = SelectiveRepeatProtocol(params["num_frames"], params["win_size"], params["timeout"])

        network = NetworkChannel(
            transmission_delay=params["trans_delay"],
            ack_delay=params["ack_delay"],
            packet_loss_pct=params["pkt_loss"],
            ack_loss_pct=params["ack_loss"],
            seed=params["seed"],
        )

        self.simulator = Simulator(protocol, network)
        metrics = self.simulator.run()
        self.snapshots = self.simulator.snapshots

        # Update Live Log Box
        self.log_text.delete("1.0", tk.END)
        for log in self.simulator.logs:
            self.log_text.insert(tk.END, log + "\n")
        self.log_text.see(tk.END)

        # Update Results Tab
        self.results_panel.display_metrics(metrics)

        # Prepare animation
        self.anim_canvas.set_data(
            self.snapshots,
            params["num_frames"],
            params["win_size"],
            params["proto_name"],
        )
        self.current_step = 0
        self.is_playing = True

        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        self.notebook.select(self.tab_sim)
        self.schedule_next_frame()

    def schedule_next_frame(self):
        if self.is_playing and self.snapshots and self.current_step < len(self.snapshots):
            self.anim_canvas.render_step(self.current_step)
            self.current_step += 1
            if self.current_step < len(self.snapshots):
                self.anim_job = self.after(self.speed_ms, self.schedule_next_frame)
            else:
                self.is_playing = False
                self.start_btn.config(state="normal")
                self.pause_btn.config(state="disabled")
                self.resume_btn.config(state="disabled")
                self.stop_btn.config(state="disabled")

    def pause_animation(self):
        self.is_playing = False
        if self.anim_job:
            self.after_cancel(self.anim_job)
            self.anim_job = None
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="normal")

    def resume_animation(self):
        if self.snapshots and self.current_step < len(self.snapshots):
            self.is_playing = True
            self.pause_btn.config(state="normal")
            self.resume_btn.config(state="disabled")
            self.schedule_next_frame()

    def reset_simulation(self):
        self.stop_simulation()
        self.anim_canvas.render_step(0)
        self.log_text.delete("1.0", tk.END)
        self.current_step = 0
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")

    def stop_simulation(self):
        self.is_playing = False
        if self.anim_job:
            self.after_cancel(self.anim_job)
            self.anim_job = None
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")

    def on_speed_changed(self, val):
        raw = float(val)
        self.speed_ms = int(810 - raw)

    def compare_protocols(self):
        params = self.validate_inputs()
        if not params:
            return

        self.stop_simulation()

        protocols_dict = {
            "One-Bit Sliding Window": OneBitProtocol(params["num_frames"], params["timeout"]),
            "Go-Back-N": GoBackNProtocol(params["num_frames"], params["win_size"], params["timeout"]),
            "Selective Repeat": SelectiveRepeatProtocol(params["num_frames"], params["win_size"], params["timeout"]),
        }

        metrics_results: Dict[str, SimulationMetrics] = {}

        for p_name, proto in protocols_dict.items():
            net = NetworkChannel(
                transmission_delay=params["trans_delay"],
                ack_delay=params["ack_delay"],
                packet_loss_pct=params["pkt_loss"],
                ack_loss_pct=params["ack_loss"],
                seed=params["seed"],
            )
            sim = Simulator(proto, net)
            m = sim.run()
            metrics_results[p_name] = m

        # Display comparison in Results tab
        self.results_panel.display_comparison_metrics(metrics_results)

        # Clear existing canvas widget if any
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
            self.canvas_widget = None

        # Build figure
        fig = create_comparison_figure(metrics_results)

        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.graph_container)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_loss_sensitivity(self):
        params = self.validate_inputs()
        if not params:
            return

        self.stop_simulation()

        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
            self.canvas_widget = None

        fig = create_loss_sensitivity_figure(
            window_size=params["win_size"],
            num_frames=params["num_frames"],
            trans_delay=params["trans_delay"],
            ack_delay=params["ack_delay"],
            ack_loss_pct=params["ack_loss"],
            timeout=params["timeout"],
            seed=params["seed"] if params["seed"] is not None else 42,
        )

        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.graph_container)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.notebook.select(self.tab_compare)

    def create_info_tab(self):
        info_text = tk.Text(
            self.tab_info,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#181825",
            fg="#cdd6f4",
            padx=15,
            pady=15,
        )
        scroll = ttk.Scrollbar(self.tab_info, command=info_text.yview)
        info_text.config(yscrollcommand=scroll.set)

        info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        content = (
            "COMPUTER NETWORKS SLIDING WINDOW PROTOCOLS: EDUCATIONAL GUIDE\n"
            "===============================================================\n\n"
            "1. ONE-BIT SLIDING WINDOW (Alternating Bit Protocol)\n"
            "-----------------------------------------------------\n"
            "• Concept: Sliding window protocol with a window size of N = 1.\n"
            "• Sender Behavior: Sends one frame at a time and waits for an ACK before sending the next.\n"
            "• Sequence Numbers: Alternates strictly between 0 and 1.\n"
            "• Retransmission: If a frame or ACK is lost, the sender timer times out and retransmits the single frame.\n"
            "• Efficiency: Low link utilization on high-delay networks (Stop-and-Wait behavior).\n\n"
            "2. GO-BACK-N (GBN) PROTOCOL\n"
            "---------------------------\n"
            "• Concept: Sender can send up to N unacknowledged frames (Window Size N).\n"
            "• Cumulative ACKs: Receiver sends ACK n acknowledging frame n and ALL preceding frames.\n"
            "• Receiver Behavior: Accepts frames ONLY strictly in-order. Discards out-of-order frames.\n"
            "• Sender Timer: Single timer for the oldest unacknowledged frame (send_base).\n"
            "• Retransmission: On timeout, sender retransmits ALL outstanding unacknowledged frames starting from send_base.\n\n"
            "3. SELECTIVE REPEAT (SR) PROTOCOL\n"
            "---------------------------------\n"
            "• Concept: Sender can send up to N frames; Receiver maintains a window of size N to buffer out-of-order frames.\n"
            "• Individual ACKs: Receiver acknowledges EACH correctly received frame individually.\n"
            "• Receiver Buffering: Out-of-order frames within the receiver window are buffered until missing frames arrive.\n"
            "• Individual Timers: Sender maintains an independent timer for EACH transmitted frame.\n"
            "• Selective Retransmission: On timeout for a specific frame, sender retransmits ONLY that missing frame.\n\n"
            "4. METRIC FORMULAS FOR ACADEMIC PRESENTATION\n"
            "--------------------------------------------\n"
            "• Frame Throughput (frames/sec) = Successfully Delivered Frames / Total Simulation Time (seconds)\n"
            "• Protocol Efficiency (%) = (Original Unique Frames / Total Transmissions) × 100%\n"
            "• Retransmission Overhead = Total Transmissions - Original Frames\n\n"
            "PROTOCOL COMPARISON MATRIX\n"
            "--------------------------\n"
            "Feature                | One-Bit SW       | Go-Back-N        | Selective Repeat\n"
            "-----------------------+------------------+------------------+------------------\n"
            "Sender Window Size     | 1                | N                | N\n"
            "Receiver Window Size   | 1                | 1                | N\n"
            "ACK Mechanism          | Individual (0/1) | Cumulative       | Individual\n"
            "Out-of-Order Handling  | Discard          | Discard          | Buffer in RAM\n"
            "Retransmission Scope   | 1 Frame          | Entire Window N  | Lost Frame Only\n"
            "Timer Count            | 1 Timer          | 1 Timer (Base)   | N Timers\n"
        )
        info_text.insert(tk.END, content)
        info_text.config(state="disabled")
