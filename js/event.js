/**
 * Discrete Event Data Structure & Priority Queue
 */

const EventType = {
  FRAME_SEND: 'FRAME_SEND',
  FRAME_ARRIVE: 'FRAME_ARRIVE',
  ACK_SEND: 'ACK_SEND',
  ACK_ARRIVE: 'ACK_ARRIVE',
  TIMEOUT: 'TIMEOUT'
};

let eventCounter = 0;

class SimEvent {
  constructor(timestamp, type, frameSeq = -1, ackSeq = -1, attempt = 1, details = '') {
    this.timestamp = timestamp;
    this.id = ++eventCounter;
    this.type = type;
    this.frameSeq = frameSeq;
    this.ackSeq = ackSeq;
    this.attempt = attempt;
    this.isLost = false;
    this.details = details;
  }
}

class PriorityQueue {
  constructor() {
    this.elements = [];
  }

  enqueue(element) {
    this.elements.push(element);
    this.elements.sort((a, b) => {
      if (a.timestamp !== b.timestamp) {
        return a.timestamp - b.timestamp;
      }
      return a.id - b.id;
    });
  }

  dequeue() {
    return this.elements.shift();
  }

  isEmpty() {
    return this.elements.length === 0;
  }

  clear() {
    this.elements = [];
  }
}
