/**
 * HTML5 Canvas Packet Animation Player
 */

class CanvasRenderer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    
    this.snapshots = [];
    this.currentStep = 0;
    this.numFrames = 10;
    this.windowSize = 4;
    this.protocolName = 'Go-Back-N';

    this.colorMap = {
      UNSENT: '#475569',
      IN_TRANSIT: '#60a5fa',
      RECEIVED: '#fde047',
      ACKED: '#4ade80',
      LOST: '#f87171',
      TIMED_OUT: '#fb923c',
      RETRANSMITTED: '#c084fc'
    };

    // Handle high DPI
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  resizeCanvas() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.width = rect.width || 800;
    this.height = 350;
    this.canvas.width = this.width;
    this.canvas.height = this.height;
    if (this.snapshots.length > 0) {
      this.renderStep(this.currentStep);
    } else {
      this.drawInitialLayout();
    }
  }

  setData(snapshots, numFrames, windowSize, protocolName) {
    this.snapshots = snapshots;
    this.numFrames = numFrames;
    this.windowSize = windowSize;
    this.protocolName = protocolName;
    this.currentStep = 0;
    this.renderStep(0);
  }

  drawInitialLayout() {
    this.ctx.clearRect(0, 0, this.width, this.height);
    
    const senderY = 70;
    const receiverY = 270;

    // Node bars
    this.ctx.fillStyle = 'rgba(30, 41, 59, 0.8)';
    this.ctx.fillRect(40, senderY - 20, this.width - 80, 55);
    this.ctx.fillRect(40, receiverY - 20, this.width - 80, 55);

    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    this.ctx.strokeRect(40, senderY - 20, this.width - 80, 55);
    this.ctx.strokeRect(40, receiverY - 20, this.width - 80, 55);

    // Node Labels
    this.ctx.fillStyle = '#f8fafc';
    this.ctx.font = 'bold 12px Inter';
    this.ctx.fillText('SENDER', 55, senderY - 30);
    this.ctx.fillText('RECEIVER', 55, receiverY - 30);

    // Channel line
    this.ctx.fillStyle = '#64748b';
    this.ctx.font = 'bold 10px Inter';
    this.ctx.textAlign = 'center';
    this.ctx.fillText('◄── NETWORK CHANNEL ──►', this.width / 2, 170);
    this.ctx.textAlign = 'left';

    this.drawLegend();
  }

  drawLegend() {
    const legendY = this.height - 20;
    const items = [
      ['Unsent', '#475569'],
      ['In Transit', '#60a5fa'],
      ['Received', '#fde047'],
      ['ACKed', '#4ade80'],
      ['Lost (X)', '#f87171'],
      ['Timed Out', '#fb923c']
    ];

    const spacing = 110;
    items.forEach(([label, color], i) => {
      const x = 50 + i * spacing;
      this.ctx.fillStyle = color;
      this.ctx.fillRect(x, legendY - 6, 12, 12);
      this.ctx.fillStyle = '#94a3b8';
      this.ctx.font = '11px Inter';
      this.ctx.fillText(label, x + 18, legendY + 4);
    });
  }

  renderStep(stepIdx) {
    if (!this.snapshots || stepIdx >= this.snapshots.length) return;

    this.ctx.clearRect(0, 0, this.width, this.height);
    this.drawInitialLayout();

    const snap = this.snapshots[stepIdx];
    this.currentStep = stepIdx;

    // Header Time
    this.ctx.fillStyle = '#fde047';
    this.ctx.font = 'bold 13px Inter';
    this.ctx.textAlign = 'right';
    this.ctx.fillText(`Simulated Time: ${Math.round(snap.timestamp)} ms`, this.width - 50, 30);
    this.ctx.textAlign = 'left';

    const senderY = 70;
    const receiverY = 270;
    const slotWidth = Math.min(55, Math.floor((this.width - 240) / Math.max(this.numFrames, 1)));
    const startX = 140;

    // Draw Sender Frame Slots
    for (let i = 0; i < this.numFrames; i++) {
      const x1 = startX + i * slotWidth;
      const status = snap.frameStates[i] || 'UNSENT';
      const color = this.colorMap[status] || '#475569';

      this.ctx.fillStyle = color;
      this.ctx.fillRect(x1, senderY - 10, slotWidth - 6, 32);
      this.ctx.strokeStyle = '#ffffff';
      this.ctx.lineWidth = 1;
      this.ctx.strokeRect(x1, senderY - 10, slotWidth - 6, 32);

      this.ctx.fillStyle = '#0f172a';
      this.ctx.font = 'bold 11px Inter';
      this.ctx.fillText(`F${i}`, x1 + (slotWidth - 6) / 2 - 7, senderY + 10);
    }

    // Sender Window Outline
    const winX1 = startX + snap.sendBase * slotWidth - 3;
    const winWidth = (this.protocolName === 'One-Bit Sliding Window' ? 1 : Math.min(this.windowSize, this.numFrames - snap.sendBase)) * slotWidth - 2;
    if (snap.sendBase < this.numFrames) {
      this.ctx.strokeStyle = '#f472b6';
      this.ctx.lineWidth = 2;
      this.ctx.setLineDash([4, 2]);
      this.ctx.strokeRect(winX1, senderY - 14, winWidth, 40);
      this.ctx.setLineDash([]);
      this.ctx.fillStyle = '#f472b6';
      this.ctx.font = 'bold 10px Inter';
      this.ctx.fillText(`Sender Window`, winX1, senderY - 18);
    }

    // Draw Receiver Frame Slots
    for (let i = 0; i < this.numFrames; i++) {
      const x1 = startX + i * slotWidth;
      const isRx = snap.receivedFrames.includes(i);
      const isBuf = snap.bufferedFrames.includes(i);

      let color = '#475569';
      if (isRx) color = '#4ade80';
      else if (isBuf) color = '#fde047';

      this.ctx.fillStyle = color;
      this.ctx.fillRect(x1, receiverY - 10, slotWidth - 6, 32);
      this.ctx.strokeStyle = '#ffffff';
      this.ctx.lineWidth = 1;
      this.ctx.strokeRect(x1, receiverY - 10, slotWidth - 6, 32);

      this.ctx.fillStyle = '#0f172a';
      this.ctx.font = 'bold 11px Inter';
      this.ctx.fillText(`F${i}`, x1 + (slotWidth - 6) / 2 - 7, receiverY + 10);
    }

    // Receiver Window/Expected
    const rcvX1 = startX + snap.rcvBase * slotWidth - 3;
    if (this.protocolName === 'Selective Repeat' && snap.rcvBase < this.numFrames) {
      const rcvWinWidth = Math.min(this.windowSize, this.numFrames - snap.rcvBase) * slotWidth - 2;
      this.ctx.strokeStyle = '#2dd4bf';
      this.ctx.lineWidth = 2;
      this.ctx.setLineDash([4, 2]);
      this.ctx.strokeRect(rcvX1, receiverY - 14, rcvWinWidth, 40);
      this.ctx.setLineDash([]);
    }

    // Draw Active Flying Packets / ACKs
    for (const packet of snap.activeTransmissions) {
      const seq = packet.seq;
      const isLost = packet.isLost;
      const pktType = packet.type;
      const startT = packet.startTime;
      const endT = packet.endTime;

      let progress = 0.5;
      if (endT > startT) {
        progress = Math.min(1.0, Math.max(0.0, (snap.timestamp - startT) / (endT - startT)));
      }

      const centerX = startX + seq * slotWidth + (slotWidth / 2) - 3;

      if (pktType === 'FRAME') {
        if (isLost) {
          const y = senderY + progress * (receiverY - senderY) * 0.6;
          this.ctx.fillStyle = '#ef4444';
          this.ctx.beginPath();
          this.ctx.arc(centerX, y, 11, 0, Math.PI * 2);
          this.ctx.fill();
          this.ctx.fillStyle = '#ffffff';
          this.ctx.font = 'bold 12px Inter';
          this.ctx.fillText('X', centerX - 4, y + 4);
        } else {
          const y = senderY + progress * (receiverY - senderY);
          this.ctx.fillStyle = '#3b82f6';
          this.ctx.fillRect(centerX - 14, y - 10, 28, 20);
          this.ctx.fillStyle = '#ffffff';
          this.ctx.font = 'bold 10px Inter';
          this.ctx.fillText(`F${seq}`, centerX - 8, y + 4);
        }
      } else { // ACK
        if (isLost) {
          const y = receiverY - progress * (receiverY - senderY) * 0.6;
          this.ctx.fillStyle = '#f97316';
          this.ctx.beginPath();
          this.ctx.arc(centerX, y, 11, 0, Math.PI * 2);
          this.ctx.fill();
          this.ctx.fillStyle = '#ffffff';
          this.ctx.font = 'bold 12px Inter';
          this.ctx.fillText('X', centerX - 4, y + 4);
        } else {
          const y = receiverY - progress * (receiverY - senderY);
          this.ctx.fillStyle = '#10b981';
          this.ctx.beginPath();
          this.ctx.arc(centerX, y, 12, 0, Math.PI * 2);
          this.ctx.fill();
          this.ctx.fillStyle = '#ffffff';
          this.ctx.font = 'bold 10px Inter';
          this.ctx.fillText(`A${seq}`, centerX - 7, y + 4);
        }
      }
    }
  }
}
