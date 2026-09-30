# Sliding Window Protocol Simulator

**An interactive Computer Networks simulation tool for visualizing and analyzing reliable data transmission using One-Bit Sliding Window, Go-Back-N, and Selective Repeat protocols.**

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-informational)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557c)
![NumPy](https://img.shields.io/badge/NumPy-Computation-013243?logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-See%20LICENSE-blue)

---

## 📖 Overview

The **Sliding Window Protocol Simulator** is a Python-based desktop application that provides an interactive way to understand the sliding window protocols used for reliable data transmission in computer networks.

Rather than relying solely on theoretical diagrams, the simulator offers a visual environment in which users can observe:

- Frame transmission
- Acknowledgement (ACK) handling
- Packet loss
- Retransmissions
- Sliding window movement
- Timeout behavior
- Protocol efficiency
- Throughput and transmission statistics

The project is intended for **Computer Networks learning, classroom demonstrations, laboratory assignments, and protocol analysis**.

---

## 🖼️ Screenshots / Demo

<!-- Add screenshots/GIF here -->

---

## ✨ Key Features

- **Three protocol implementations:** One-Bit Sliding Window, Go-Back-N ARQ, and Selective Repeat ARQ
- **Configurable simulation parameters:** window size and number of frames
- **Network impairment simulation:** packet/frame loss and ACK loss
- **Reliability mechanisms:** retransmission handling and timeout simulation
- **Variable network conditions** for observing protocol behavior under different scenarios
- **Real-time protocol visualization** with simulation controls
- **Performance results** presented after each simulation
- **Protocol comparison** to evaluate behavior and efficiency across protocols
- **User-friendly graphical interface** built with Tkinter

---

## 📡 Supported Protocols

### One-Bit Sliding Window
A stop-and-wait style sliding window protocol with a window size of one. The sender transmits a single frame and waits for its acknowledgement before sending the next, using a one-bit sequence number to distinguish new frames from duplicates.

### Go-Back-N ARQ
The sender may transmit multiple frames within a window without waiting for individual ACKs. The receiver accepts frames only in order. When a frame is lost or a timeout occurs, the sender retransmits the lost frame and all subsequent outstanding frames in the window.

### Selective Repeat ARQ
The sender may transmit multiple frames within a window, and the receiver accepts and buffers out-of-order frames. Only the frames that are lost or time out are retransmitted, which reduces unnecessary retransmissions compared to Go-Back-N.

---

## 📊 Performance Metrics

The simulator reports the following metrics for each run:

| Metric | Description |
|---|---|
| **Total Transmissions** | Total number of frame transmissions, including retransmissions |
| **Retransmissions** | Number of frames sent again after loss or timeout |
| **Packets Lost** | Total number of packets lost during the simulation |
| **Unique Packets Lost** | Number of distinct packets that experienced loss |
| **ACKs Received** | Number of acknowledgements successfully received by the sender |
| **Total Simulation Time** | Total time taken to complete the simulation |
| **Frame Throughput** | Rate of frame delivery during the simulation |
| **Protocol Efficiency** | Measure of how effectively the protocol used its transmissions |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **Tkinter** | Graphical user interface |
| **Matplotlib** | Visualization |
| **NumPy** | Numerical computation |
| **Pandas** | Data handling and results analysis |
| **PyInstaller** | Packaging the application |

---

## 📁 Project Structure

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
```

| Directory / File | Role |
|---|---|
| `gui/` | Graphical user interface components |
| `protocols/` | Implementations of the supported protocols |
| `simulation/` | Simulation logic |
| `main.py` | Application entry point |
| `requirements.txt` | Python dependencies |
| `LICENSE` | Project license |

---

## ⚙️ Installation

**Prerequisites:** Python 3 installed on your system.

1. **Clone the repository**

```bash
   git clone <your-repository-url>
   cd Sliding-Window-Protocol-Simulator
```

2. **(Optional) Create and activate a virtual environment**

```bash
   python -m venv venv
```

   - Windows: `venv\Scripts\activate`
   - macOS / Linux: `source venv/bin/activate`

3. **Install dependencies**

```bash
   pip install -r requirements.txt
```

4. **Run the application**

```bash
   python main.py
```

---

## 🚀 Usage

1. Launch the application using `main.py`.
2. Select the protocol you want to simulate: One-Bit Sliding Window, Go-Back-N ARQ, or Selective Repeat ARQ.
3. Configure the network and simulation parameters, such as window size, number of frames, and loss conditions.
4. Start the simulation and observe frame transmission, ACK handling, timeouts, retransmissions, and window movement in real time.
5. Review the performance results once the simulation completes.
6. Compare protocol behavior and efficiency under the same or varying network conditions.

---

## 🔄 How It Works

1. **Configuration:** The user selects a protocol and sets parameters such as window size, number of frames, and loss conditions.
2. **Transmission:** The sender transmits frames according to the rules of the selected protocol and its current window.
3. **Network behavior:** The simulated network may lose frames or ACKs based on the configured conditions.
4. **Acknowledgement and timeout handling:** The sender processes received ACKs and slides the window forward. If an ACK does not arrive in time, a timeout occurs.
5. **Retransmission:** Lost or unacknowledged frames are retransmitted according to the protocol's strategy.
6. **Visualization:** Transmission events and window movement are displayed in the graphical interface.
7. **Metrics:** Once the simulation completes, performance statistics are calculated and presented.

---

## 🎓 Learning Objectives

This project helps build an understanding of:

- Reliable data transfer over unreliable channels
- Sliding window flow control
- ARQ (Automatic Repeat reQuest) mechanisms
- Acknowledgement and timeout-based error recovery
- Differences between One-Bit Sliding Window, Go-Back-N, and Selective Repeat
- Impact of packet loss and ACK loss on retransmissions
- Effect of window size on throughput and efficiency
- Trade-offs between protocol complexity and performance

---

## 💡 Use Cases

- Learning and revising Computer Networks concepts
- Classroom and laboratory demonstrations
- Computer Networks lab assignments
- Protocol behavior and performance analysis
- Comparing ARQ protocols under different network conditions

---

## 🔮 Future Enhancements

> The following are **possible future improvements** and are **not part of the current implementation**.

- Exporting simulation results
- Additional protocol variants or scenarios
- Expanded analysis and comparison visualizations
- More detailed network condition modeling

---

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.
