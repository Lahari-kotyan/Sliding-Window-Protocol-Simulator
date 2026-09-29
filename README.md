# Sliding Window Protocol Simulator

An interactive Computer Networks simulation tool for visualizing and analyzing reliable data transmission using **One-Bit Sliding Window, Go-Back-N, and Selective Repeat** protocols.

The simulator allows users to experiment with different window sizes, packet-loss conditions, retransmissions, acknowledgements, and network parameters while observing protocol behavior and performance metrics.

---

## 📌 Overview

The **Sliding Window Protocol Simulator** is a Python-based desktop application designed to provide an interactive understanding of sliding window protocols used in computer networks.

Instead of relying only on theoretical diagrams, the simulator provides a visual environment where users can observe:

- Frame transmission
- Acknowledgement handling
- Packet loss
- Retransmissions
- Sliding window movement
- Timeout behavior
- Protocol efficiency
- Throughput and transmission statistics

The project is intended for **Computer Networks learning, demonstrations, laboratory assignments, and protocol analysis**.

---

## 🚀 Features

### Supported Protocols

- **One-Bit Sliding Window**
- **Go-Back-N ARQ**
- **Selective Repeat ARQ**

### Network Simulation

- Configurable window size
- Configurable number of frames
- Packet/frame loss simulation
- ACK loss simulation
- Retransmission handling
- Timeout simulation
- Variable network conditions

### Performance Analysis

The simulator provides performance information such as:

- Total transmissions
- Retransmissions
- Packets lost
- Unique packets lost
- ACKs received
- Total simulation time
- Frame throughput
- Protocol efficiency

### Interactive GUI

- User-friendly graphical interface
- Real-time protocol visualization
- Simulation controls
- Network configuration
- Performance results
- Protocol comparison

---

## 🖥️ Application Preview

The simulator provides a graphical interface for configuring network conditions and observing the behavior of different sliding window protocols.

---

## 🛠️ Technologies Used

- **Python**
- **Tkinter**
- **Matplotlib**
- **NumPy**
- **Pandas**
- **PyInstaller**

---

## 📂 Project Structure

```text
Sliding-Window-Protocol-Simulator/
│
├── gui/
│   ├── main_window.py
│   └── ...
│
├── protocols/
│   ├── one_bit_sliding_window.py
│   ├── go_back_n.py
│   ├── selective_repeat.py
│   └── ...
│
├── simulation/
│   └── ...
│
├── main.py
├── requirements.txt
├── README.md
└── LICENSE
