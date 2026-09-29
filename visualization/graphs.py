"""
Matplotlib graph generation for protocol visual comparison and loss sensitivity analysis.
"""

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Dict, List, Tuple
from metrics.metrics import SimulationMetrics
from protocols.one_bit import OneBitProtocol
from protocols.go_back_n import GoBackNProtocol
from protocols.selective_repeat import SelectiveRepeatProtocol
from simulation.network import NetworkChannel
from simulation.simulator import Simulator


def create_comparison_figure(metrics_dict: Dict[str, SimulationMetrics]) -> Figure:
    """
    Creates a 2x2 grid Matplotlib Figure comparing metrics across protocols.
    """
    fig = Figure(figsize=(9, 6), dpi=100)
    fig.patch.set_facecolor('#ffffff')

    protocols = list(metrics_dict.keys())
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    transmissions = [metrics_dict[p].total_transmissions for p in protocols]
    retransmissions = [metrics_dict[p].retransmissions for p in protocols]
    throughputs = [metrics_dict[p].throughput_fps for p in protocols]
    efficiencies = [metrics_dict[p].efficiency_pct for p in protocols]
    total_times = [metrics_dict[p].total_time_ms for p in protocols]

    # Subplot 1: Transmissions & Retransmissions
    ax1 = fig.add_subplot(221)
    x = range(len(protocols))
    width = 0.35
    rects1 = ax1.bar([i - width/2 for i in x], transmissions, width, label='Total Trans', color='#3498db')
    rects2 = ax1.bar([i + width/2 for i in x], retransmissions, width, label='Retransmissions', color='#e74c3c')
    ax1.set_title('Transmissions & Retransmissions', fontsize=10, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(protocols, fontsize=8)
    ax1.legend(fontsize=8)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Subplot 2: Throughput
    ax2 = fig.add_subplot(222)
    bars2 = ax2.bar(protocols, throughputs, color=colors, width=0.5)
    ax2.set_title('Frame Throughput (frames/sec)', fontsize=10, fontweight='bold')
    ax2.set_ylabel('frames/sec', fontsize=8)
    ax2.grid(True, linestyle='--', alpha=0.5)
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval / 2.0, f"{yval:.2f}", ha='center', va='bottom', color='white', fontweight='bold', fontsize=9)

    # Subplot 3: Efficiency %
    ax3 = fig.add_subplot(223)
    bars3 = ax3.bar(protocols, efficiencies, color=colors, width=0.5)
    ax3.set_title('Protocol Efficiency (%)', fontsize=10, fontweight='bold')
    ax3.set_ylabel('Efficiency %', fontsize=8)
    ax3.set_ylim(0, 105)
    ax3.grid(True, linestyle='--', alpha=0.5)
    for bar in bars3:
        yval = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2.0, yval / 2.0, f"{yval:.1f}%", ha='center', va='bottom', color='white', fontweight='bold', fontsize=9)

    # Subplot 4: Total Time (ms)
    ax4 = fig.add_subplot(224)
    bars4 = ax4.bar(protocols, total_times, color=colors, width=0.5)
    ax4.set_title('Total Transmission Time (ms)', fontsize=10, fontweight='bold')
    ax4.set_ylabel('ms', fontsize=8)
    ax4.grid(True, linestyle='--', alpha=0.5)
    for bar in bars4:
        yval = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2.0, yval / 2.0, f"{yval:.0f} ms", ha='center', va='bottom', color='white', fontweight='bold', fontsize=8)

    fig.tight_layout(pad=2.0)
    return fig


def create_loss_sensitivity_figure(
    window_size: int,
    num_frames: int,
    trans_delay: float,
    ack_delay: float,
    ack_loss_pct: float,
    timeout: float,
    seed: int = 42,
    loss_rates: List[float] = [0, 10, 20, 30, 40, 50],
) -> Figure:
    """
    Generates sensitivity curves for Throughput & Retransmissions vs Packet Loss %.
    """
    fig = Figure(figsize=(9, 4), dpi=100)
    fig.patch.set_facecolor('#ffffff')

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    protocols_config = [
        ("One-Bit SW", lambda n, w, t: OneBitProtocol(n, t)),
        ("Go-Back-N", lambda n, w, t: GoBackNProtocol(n, w, t)),
        ("Selective Repeat", lambda n, w, t: SelectiveRepeatProtocol(n, w, t)),
    ]

    colors = {"One-Bit SW": "#e74c3c", "Go-Back-N": "#e67e22", "Selective Repeat": "#2ecc71"}

    for name, factory in protocols_config:
        throughputs = []
        retransmissions_list = []
        
        for loss in loss_rates:
            proto = factory(num_frames, window_size, timeout)
            net = NetworkChannel(trans_delay, ack_delay, loss, ack_loss_pct, seed=seed)
            sim = Simulator(proto, net)
            m = sim.run()
            throughputs.append(m.throughput_fps)
            retransmissions_list.append(m.retransmissions)

        ax1.plot(loss_rates, throughputs, marker='o', label=name, color=colors[name], linewidth=2)
        ax2.plot(loss_rates, retransmissions_list, marker='s', label=name, color=colors[name], linewidth=2)

    ax1.set_title('Throughput vs Packet Loss %', fontsize=10, fontweight='bold')
    ax1.set_xlabel('Packet Loss %', fontsize=8)
    ax1.set_ylabel('Frame Throughput (fps)', fontsize=8)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(fontsize=8)

    ax2.set_title('Retransmissions vs Packet Loss %', fontsize=10, fontweight='bold')
    ax2.set_xlabel('Packet Loss %', fontsize=8)
    ax2.set_ylabel('Total Retransmissions', fontsize=8)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(fontsize=8)

    fig.tight_layout(pad=2.0)
    return fig
