/**
 * Network Channel Model with seedable PRNG
 */

class SeededRandom {
  constructor(seed) {
    this.seed = seed !== null && seed !== undefined ? seed % 2147483647 : null;
    if (this.seed <= 0 && this.seed !== null) this.seed += 2147483646;
  }

  next() {
    if (this.seed === null) {
      return Math.random();
    }
    this.seed = (this.seed * 16807) % 2147483647;
    return (this.seed - 1) / 2147483646;
  }
}

class NetworkChannel {
  constructor(transDelay = 100, ackDelay = 50, packetLossPct = 10, ackLossPct = 5, seed = null) {
    this.transDelay = parseFloat(transDelay);
    this.ackDelay = parseFloat(ackDelay);
    this.packetLossRate = parseFloat(packetLossPct) / 100.0;
    this.ackLossRate = parseFloat(ackLossPct) / 100.0;
    this.seed = seed;
    this.rng = new SeededRandom(seed);
  }

  resetRng(seed = null) {
    if (seed !== null) this.seed = seed;
    this.rng = new SeededRandom(this.seed);
  }

  isFrameLost() {
    return this.rng.next() < this.packetLossRate;
  }

  isAckLost() {
    return this.rng.next() < this.ackLossRate;
  }

  getFrameArrivalTime(sendTime) {
    return sendTime + this.transDelay;
  }

  getAckArrivalTime(sendTime) {
    return sendTime + this.ackDelay;
  }
}
