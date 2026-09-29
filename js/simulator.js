/**
 * Discrete Event Simulation Engine & Snapshot Recorder for JS
 */

class SimulationMetrics {
  constructor(protocolName, windowSize, numFrames, transDelay, ackDelay, pktLossPct, ackLossPct, timeout) {
    this.protocolName = protocolName;
    this.windowSize = windowSize;
    this.numFrames = numFrames;
    this.transDelay = transDelay;
    this.ackDelay = ackDelay;
    this.pktLossPct = pktLossPct;
    this.ackLossPct = ackLossPct;
    this.timeout = timeout;

    this.totalTransmissions = 0;
    this.retransmissions = 0;
    this.packetsLost = 0;
    this.uniquePacketsLost = 0;
    this.acksSent = 0;
    this.acksLost = 0;
    this.acksReceived = 0;
    this.totalTimeMs = 0;
    this.throughputFps = 0;
    this.efficiencyPct = 0;
  }

  calculate() {
    const timeSec = this.totalTimeMs > 0 ? this.totalTimeMs / 1000.0 : 1.0;
    this.throughputFps = parseFloat((this.numFrames / timeSec).toFixed(2));
    if (this.totalTransmissions > 0) {
      this.efficiencyPct = parseFloat(((this.numFrames / this.totalTransmissions) * 100.0).toFixed(2));
    } else {
      this.efficiencyPct = 0;
    }
  }
}

class Simulator {
  constructor(protocol, network, maxTimeMs = 120000) {
    this.protocol = protocol;
    this.network = network;
    this.maxTimeMs = maxTimeMs;
    this.pq = new PriorityQueue();
    this.currentTime = 0.0;

    this.snapshots = [];
    this.logs = [];
    this.metrics = null;
  }

  run() {
    this.protocol.reset();
    this.network.resetRng();
    this.pq.clear();
    this.snapshots = [];
    this.logs = [];
    this.currentTime = 0.0;

    const metrics = new SimulationMetrics(
      this.protocol.name(),
      this.protocol.windowSize,
      this.protocol.numFrames,
      this.network.transDelay,
      this.network.ackDelay,
      this.network.packetLossRate * 100.0,
      this.network.ackLossRate * 100.0,
      this.protocol.timeout
    );

    const uniqueLostSet = new Set();
    let activeInFlight = [];

    const initialFrames = this.protocol.getSendableFrames();
    for (const f of initialFrames) {
      this._scheduleFrameSend(f, 0.0, 1);
    }

    this._recordSnapshot(
      new SimEvent(0.0, EventType.FRAME_SEND, -1, -1, 1, 'Simulation Started'),
      'Simulation Started',
      activeInFlight
    );

    while (!this.pq.isEmpty() && this.currentTime <= this.maxTimeMs) {
      if (this.protocol.ackedFrames.size >= this.protocol.numFrames) {
        break;
      }

      const ev = this.pq.dequeue();
      this.currentTime = ev.timestamp;
      let logMsg = '';

      if (ev.type === EventType.FRAME_SEND) {
        const frame = ev.frameSeq;
        const attempt = ev.attempt;
        metrics.totalTransmissions++;
        this.protocol.frameAttempts[frame] = attempt;

        if (attempt > 1) metrics.retransmissions++;

        const isLost = this.network.isFrameLost();
        ev.isLost = isLost;

        if (isLost) {
          metrics.packetsLost++;
          uniqueLostSet.add(frame);
          this.protocol.frameStates[frame] = FrameStatus.LOST;
          logMsg = `[${Math.round(this.currentTime)} ms] Frame ${frame} LOST (Attempt #${attempt})`;
          this.logs.push(logMsg);

          const timeoutEv = new SimEvent(
            this.currentTime + this.protocol.timeout,
            EventType.TIMEOUT,
            frame,
            -1,
            attempt,
            `Timeout for Frame ${frame}`
          );
          this.pq.enqueue(timeoutEv);

          activeInFlight.push({
            id: `F-${frame}-${attempt}`,
            type: 'FRAME',
            seq: frame,
            startTime: this.currentTime,
            endTime: this.currentTime + this.network.transDelay,
            isLost: true
          });
        } else {
          this.protocol.frameStates[frame] = FrameStatus.IN_TRANSIT;
          logMsg = `[${Math.round(this.currentTime)} ms] Sending Frame ${frame} (Attempt #${attempt})`;
          this.logs.push(logMsg);

          const arrTime = this.network.getFrameArrivalTime(this.currentTime);
          const arrEv = new SimEvent(
            arrTime,
            EventType.FRAME_ARRIVE,
            frame,
            -1,
            attempt,
            `Frame ${frame} Arrived`
          );
          this.pq.enqueue(arrEv);

          const timeoutEv = new SimEvent(
            this.currentTime + this.protocol.timeout,
            EventType.TIMEOUT,
            frame,
            -1,
            attempt,
            `Timeout for Frame ${frame}`
          );
          this.pq.enqueue(timeoutEv);

          activeInFlight.push({
            id: `F-${frame}-${attempt}`,
            type: 'FRAME',
            seq: frame,
            startTime: this.currentTime,
            endTime: arrTime,
            isLost: false
          });
        }
      } else if (ev.type === EventType.FRAME_ARRIVE) {
        const frame = ev.frameSeq;
        const rxResult = this.protocol.handleFrameArrival(frame);

        if (rxResult.accepted) {
          this.protocol.frameStates[frame] = FrameStatus.RECEIVED;
        }

        logMsg = `[${Math.round(this.currentTime)} ms] ${rxResult.msg}`;
        this.logs.push(logMsg);

        if (rxResult.ackNum >= 0) {
          metrics.acksSent++;
          const isAckLost = this.network.isAckLost();

          if (isAckLost) {
            metrics.acksLost++;
            this.logs.push(`[${Math.round(this.currentTime)} ms] ACK ${rxResult.ackNum} LOST in channel`);

            activeInFlight.push({
              id: `ACK-${rxResult.ackNum}-${ev.id}`,
              type: 'ACK',
              seq: rxResult.ackNum,
              startTime: this.currentTime,
              endTime: this.currentTime + this.network.ackDelay,
              isLost: true
            });
          } else {
            const ackArrTime = this.network.getAckArrivalTime(this.currentTime);
            const ackEv = new SimEvent(
              ackArrTime,
              EventType.ACK_ARRIVE,
              frame,
              rxResult.ackNum,
              1,
              `ACK ${rxResult.ackNum} Arrived`
            );
            this.pq.enqueue(ackEv);

            activeInFlight.push({
              id: `ACK-${rxResult.ackNum}-${ev.id}`,
              type: 'ACK',
              seq: rxResult.ackNum,
              startTime: this.currentTime,
              endTime: ackArrTime,
              isLost: false
            });
          }
        }
      } else if (ev.type === EventType.ACK_ARRIVE) {
        const ackNum = ev.ackSeq;
        metrics.acksReceived++;
        const newlyAcked = this.protocol.handleAckArrival(ackNum);

        for (const ackedF of newlyAcked) {
          this.protocol.frameStates[ackedF] = FrameStatus.ACKED;
        }

        logMsg = `[${Math.round(this.currentTime)} ms] ACK ${ackNum} received at sender`;
        this.logs.push(logMsg);

        const newSendable = this.protocol.getSendableFrames();
        for (const f of newSendable) {
          this._scheduleFrameSend(f, this.currentTime, 1);
        }
      } else if (ev.type === EventType.TIMEOUT) {
        const frame = ev.frameSeq;
        const retransmitFrames = this.protocol.handleTimeout(frame);

        if (retransmitFrames && retransmitFrames.length > 0) {
          logMsg = `[${Math.round(this.currentTime)} ms] Timeout for Frame ${frame}! Retransmitting: ${retransmitFrames.join(', ')}`;
          this.logs.push(logMsg);

          for (const rf of retransmitFrames) {
            this.protocol.frameStates[rf] = FrameStatus.TIMED_OUT;
            const attempt = (this.protocol.frameAttempts[rf] || 1) + 1;
            this._scheduleFrameSend(rf, this.currentTime, attempt);
          }
        } else {
          logMsg = `[${Math.round(this.currentTime)} ms] Timeout for Frame ${frame} ignored (already ACKed)`;
        }
      }

      activeInFlight = activeInFlight.filter(item => item.endTime >= this.currentTime);
      this._recordSnapshot(ev, logMsg, activeInFlight);
    }

    metrics.totalTimeMs = this.currentTime;
    metrics.uniquePacketsLost = uniqueLostSet.size;
    metrics.calculate();
    this.metrics = metrics;

    this._recordSnapshot(
      new SimEvent(this.currentTime, EventType.ACK_ARRIVE, -1, -1, 1, 'Simulation Completed'),
      `[${Math.round(this.currentTime)} ms] Simulation Completed Successfully`,
      []
    );

    return metrics;
  }

  _scheduleFrameSend(frameSeq, time, attempt = 1) {
    const sendEv = new SimEvent(time, EventType.FRAME_SEND, frameSeq, -1, attempt, `Sending Frame ${frameSeq}`);
    this.pq.enqueue(sendEv);
  }

  _recordSnapshot(event, logMsg, activeInFlight) {
    this.snapshots.push({
      timestamp: this.currentTime,
      event: event,
      sendBase: this.protocol.sendBase,
      nextSeqNum: this.protocol.nextSeqNum,
      rcvBase: this.protocol.rcvBase,
      frameStates: Object.assign({}, this.protocol.frameStates),
      ackedFrames: Array.from(this.protocol.ackedFrames),
      receivedFrames: Array.from(this.protocol.receivedFrames),
      bufferedFrames: Array.from(this.protocol.bufferedFrames),
      activeTransmissions: JSON.parse(JSON.stringify(activeInFlight)),
      logMessage: logMsg
    });
  }
}
