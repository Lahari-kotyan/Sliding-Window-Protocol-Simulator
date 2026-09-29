/**
 * Protocol State Machines: One-Bit SW, Go-Back-N, Selective Repeat
 */

const FrameStatus = {
  UNSENT: 'UNSENT',
  IN_TRANSIT: 'IN_TRANSIT',
  RECEIVED: 'RECEIVED',
  ACKED: 'ACKED',
  LOST: 'LOST',
  TIMED_OUT: 'TIMED_OUT',
  RETRANSMITTED: 'RETRANSMITTED'
};

class BaseProtocol {
  constructor(numFrames, windowSize, timeout) {
    this.numFrames = numFrames;
    this.windowSize = windowSize;
    this.timeout = timeout;
    
    this.sendBase = 0;
    this.nextSeqNum = 0;
    this.rcvBase = 0;
    
    this.frameStates = {};
    this.frameAttempts = {};
    for (let i = 0; i < numFrames; i++) {
      this.frameStates[i] = FrameStatus.UNSENT;
      this.frameAttempts[i] = 0;
    }
    
    this.ackedFrames = new Set();
    this.receivedFrames = new Set();
    this.bufferedFrames = new Set();
  }

  reset() {
    this.sendBase = 0;
    this.nextSeqNum = 0;
    this.rcvBase = 0;
    this.ackedFrames.clear();
    this.receivedFrames.clear();
    this.bufferedFrames.clear();
    for (let i = 0; i < this.numFrames; i++) {
      this.frameStates[i] = FrameStatus.UNSENT;
      this.frameAttempts[i] = 0;
    }
  }
}

class OneBitProtocol extends BaseProtocol {
  constructor(numFrames, timeout) {
    super(numFrames, 1, timeout);
  }

  name() { return 'One-Bit Sliding Window'; }

  getSendableFrames() {
    if (this.sendBase < this.numFrames && this.nextSeqNum === this.sendBase) {
      const f = this.nextSeqNum;
      this.nextSeqNum++;
      return [f];
    }
    return [];
  }

  handleFrameArrival(frameIndex) {
    if (frameIndex === this.rcvBase) {
      this.receivedFrames.add(frameIndex);
      this.rcvBase++;
      return { accepted: true, ackNum: frameIndex, msg: `Frame ${frameIndex} (Seq ${frameIndex % 2}) accepted. Sending ACK ${frameIndex}` };
    } else {
      let ackToSend = this.rcvBase - 1;
      if (ackToSend < 0) ackToSend = frameIndex;
      return { accepted: false, ackNum: ackToSend, msg: `Duplicate Frame ${frameIndex} received. Re-sending ACK ${ackToSend}` };
    }
  }

  handleAckArrival(ackNum) {
    if (ackNum === this.sendBase) {
      this.ackedFrames.add(ackNum);
      this.sendBase++;
      return [ackNum];
    }
    return [];
  }

  handleTimeout(frameIndex) {
    if (frameIndex === this.sendBase && !this.ackedFrames.has(frameIndex)) {
      return [frameIndex];
    }
    return [];
  }
}

class GoBackNProtocol extends BaseProtocol {
  constructor(numFrames, windowSize, timeout) {
    super(numFrames, windowSize, timeout);
  }

  name() { return 'Go-Back-N'; }

  getSendableFrames() {
    const sendable = [];
    while (this.nextSeqNum < this.sendBase + this.windowSize && this.nextSeqNum < this.numFrames) {
      sendable.push(this.nextSeqNum);
      this.nextSeqNum++;
    }
    return sendable;
  }

  handleFrameArrival(frameIndex) {
    if (frameIndex === this.rcvBase) {
      this.receivedFrames.add(frameIndex);
      this.rcvBase++;
      return { accepted: true, ackNum: frameIndex, msg: `Frame ${frameIndex} accepted in-order. Sending cumulative ACK ${frameIndex}` };
    } else {
      const ackToSend = this.rcvBase - 1;
      return { accepted: false, ackNum: ackToSend, msg: `Frame ${frameIndex} out-of-order (expected ${this.rcvBase}). Re-sending cumulative ACK ${ackToSend}` };
    }
  }

  handleAckArrival(ackNum) {
    if (ackNum >= this.sendBase) {
      const newlyAcked = [];
      for (let f = this.sendBase; f <= ackNum; f++) {
        if (!this.ackedFrames.has(f)) {
          this.ackedFrames.add(f);
          newlyAcked.push(f);
        }
      }
      this.sendBase = ackNum + 1;
      return newlyAcked;
    }
    return [];
  }

  handleTimeout(frameIndex) {
    if (frameIndex === this.sendBase && !this.ackedFrames.has(this.sendBase) && this.sendBase < this.nextSeqNum) {
      const res = [];
      for (let f = this.sendBase; f < this.nextSeqNum; f++) {
        res.push(f);
      }
      return res;
    }
    return [];
  }
}

class SelectiveRepeatProtocol extends BaseProtocol {
  constructor(numFrames, windowSize, timeout) {
    super(numFrames, windowSize, timeout);
  }

  name() { return 'Selective Repeat'; }

  getSendableFrames() {
    const sendable = [];
    while (this.nextSeqNum < this.sendBase + this.windowSize && this.nextSeqNum < this.numFrames) {
      sendable.push(this.nextSeqNum);
      this.nextSeqNum++;
    }
    return sendable;
  }

  handleFrameArrival(frameIndex) {
    if (frameIndex >= this.rcvBase && frameIndex < this.rcvBase + this.windowSize) {
      this.receivedFrames.add(frameIndex);
      this.bufferedFrames.add(frameIndex);

      while (this.bufferedFrames.has(this.rcvBase)) {
        this.rcvBase++;
      }
      return { accepted: true, ackNum: frameIndex, msg: `Frame ${frameIndex} accepted into buffer. Sending individual ACK ${frameIndex}` };
    } else if (frameIndex < this.rcvBase) {
      return { accepted: false, ackNum: frameIndex, msg: `Duplicate Frame ${frameIndex} received. Re-sending ACK ${frameIndex}` };
    } else {
      return { accepted: false, ackNum: -1, msg: `Frame ${frameIndex} outside receiver window. Ignored.` };
    }
  }

  handleAckArrival(ackNum) {
    if (ackNum >= 0 && ackNum < this.numFrames) {
      this.ackedFrames.add(ackNum);
      while (this.ackedFrames.has(this.sendBase)) {
        this.sendBase++;
      }
      return [ackNum];
    }
    return [];
  }

  handleTimeout(frameIndex) {
    if (!this.ackedFrames.has(frameIndex) && frameIndex < this.numFrames) {
      return [frameIndex];
    }
    return [];
  }
}
