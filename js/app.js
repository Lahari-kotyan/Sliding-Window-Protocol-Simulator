/**
 * Main Web Application Driver & Event Listeners
 */

let canvasRenderer;
let currentSimulator = null;
let currentSnapshots = [];
let currentStepIdx = 0;
let isPlaying = false;
let animTimer = null;
let animSpeedMs = 300;
let lastComparisonMetrics = null;

document.addEventListener('DOMContentLoaded', () => {
  canvasRenderer = new CanvasRenderer('simCanvas');

  setupEventListeners();
  runDefaultSimulation();
  runComparison();
});

function setupEventListeners() {
  // Protocol dropdown change
  document.getElementById('protocolSelect').addEventListener('change', (e) => {
    const winInput = document.getElementById('windowSize');
    if (e.target.value === 'One-Bit Sliding Window') {
      winInput.value = 1;
      winInput.disabled = true;
    } else {
      winInput.disabled = false;
      if (winInput.value == 1) winInput.value = 4;
    }
  });

  // Buttons
  document.getElementById('btnStart').addEventListener('click', startSimulation);
  document.getElementById('btnPause').addEventListener('click', pauseAnimation);
  document.getElementById('btnResume').addEventListener('click', resumeAnimation);
  document.getElementById('btnReset').addEventListener('click', resetSimulation);
  document.getElementById('btnCompare').addEventListener('click', runComparison);
  document.getElementById('btnExportCsv').addEventListener('click', exportCSV);

  // Speed slider
  document.getElementById('speedSlider').addEventListener('input', (e) => {
    animSpeedMs = 810 - parseInt(e.target.value);
  });

  // Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      
      btn.classList.add('active');
      const tabId = btn.getAttribute('data-tab');
      document.getElementById(tabId).classList.add('active');

      if (tabId === 'tabCompare' && (!comparisonChartInstance || !sensitivityChartInstance)) {
        runComparison();
      }
    });
  });
}

function getParams() {
  return {
    protoName: document.getElementById('protocolSelect').value,
    winSize: parseInt(document.getElementById('windowSize').value) || 4,
    numFrames: parseInt(document.getElementById('numFrames').value) || 10,
    transDelay: parseFloat(document.getElementById('transDelay').value) || 100,
    ackDelay: parseFloat(document.getElementById('ackDelay').value) || 50,
    pktLoss: parseFloat(document.getElementById('pktLoss').value) || 10,
    ackLoss: parseFloat(document.getElementById('ackLoss').value) || 5,
    timeout: parseFloat(document.getElementById('timeout').value) || 300,
    seed: document.getElementById('seedInput').value ? parseInt(document.getElementById('seedInput').value) : 42
  };
}

function runDefaultSimulation() {
  const params = getParams();
  let proto;
  if (params.protoName === 'One-Bit Sliding Window') {
    proto = new OneBitProtocol(params.numFrames, params.timeout);
  } else if (params.protoName === 'Go-Back-N') {
    proto = new GoBackNProtocol(params.numFrames, params.winSize, params.timeout);
  } else {
    proto = new SelectiveRepeatProtocol(params.numFrames, params.winSize, params.timeout);
  }

  const net = new NetworkChannel(params.transDelay, params.ackDelay, params.pktLoss, params.ackLoss, params.seed);
  currentSimulator = new Simulator(proto, net);
  const metrics = currentSimulator.run();
  currentSnapshots = currentSimulator.snapshots;

  updateLogBox(currentSimulator.logs);
  updateMetricsCards(metrics);
  canvasRenderer.setData(currentSnapshots, params.numFrames, params.winSize, params.protoName);
}

function startSimulation() {
  stopAnimation();
  runDefaultSimulation();
  
  const params = getParams();
  currentStepIdx = 0;
  isPlaying = true;
  
  document.getElementById('btnStart').disabled = true;
  document.getElementById('btnPause').disabled = false;
  document.getElementById('btnResume').disabled = true;

  scheduleNextFrame();
}

function scheduleNextFrame() {
  if (isPlaying && currentSnapshots && currentStepIdx < currentSnapshots.length) {
    canvasRenderer.renderStep(currentStepIdx);
    currentStepIdx++;
    if (currentStepIdx < currentSnapshots.length) {
      animTimer = setTimeout(scheduleNextFrame, animSpeedMs);
    } else {
      isPlaying = false;
      document.getElementById('btnStart').disabled = false;
      document.getElementById('btnPause').disabled = true;
      document.getElementById('btnResume').disabled = true;
    }
  }
}

function pauseAnimation() {
  isPlaying = false;
  if (animTimer) clearTimeout(animTimer);
  document.getElementById('btnPause').disabled = true;
  document.getElementById('btnResume').disabled = false;
}

function resumeAnimation() {
  if (currentSnapshots && currentStepIdx < currentSnapshots.length) {
    isPlaying = true;
    document.getElementById('btnPause').disabled = false;
    document.getElementById('btnResume').disabled = true;
    scheduleNextFrame();
  }
}

function stopAnimation() {
  isPlaying = false;
  if (animTimer) clearTimeout(animTimer);
  document.getElementById('btnStart').disabled = false;
  document.getElementById('btnPause').disabled = true;
  document.getElementById('btnResume').disabled = true;
}

function resetSimulation() {
  stopAnimation();
  currentStepIdx = 0;
  canvasRenderer.renderStep(0);
}

function updateLogBox(logs) {
  const consoleElem = document.getElementById('logConsole');
  consoleElem.innerHTML = logs.map(l => `<div>${l}</div>`).join('');
  consoleElem.scrollTop = consoleElem.scrollHeight;
}

function updateMetricsCards(m) {
  document.getElementById('mTotalTrans').innerText = m.totalTransmissions;
  document.getElementById('mRetrans').innerText = m.retransmissions;
  document.getElementById('mPktLost').innerText = m.packetsLost;
  document.getElementById('mAcksRx').innerText = m.acksReceived;
  document.getElementById('mTotalTime').innerText = `${Math.round(m.totalTimeMs)} ms`;
  document.getElementById('mThroughput').innerText = `${m.throughputFps} fps`;
  document.getElementById('mEfficiency').innerText = `${m.efficiencyPct}%`;
}

function runComparison() {
  const params = getParams();
  const protos = {
    'One-Bit SW': new OneBitProtocol(params.numFrames, params.timeout),
    'Go-Back-N': new GoBackNProtocol(params.numFrames, params.winSize, params.timeout),
    'Selective Repeat': new SelectiveRepeatProtocol(params.numFrames, params.winSize, params.timeout)
  };

  const results = {};
  for (const [name, proto] of Object.entries(protos)) {
    const net = new NetworkChannel(params.transDelay, params.ackDelay, params.pktLoss, params.ackLoss, params.seed);
    const sim = new Simulator(proto, net);
    results[name] = sim.run();
  }

  lastComparisonMetrics = results;

  // Update Table
  const tbody = document.getElementById('compTableBody');
  tbody.innerHTML = `
    <tr><td>Window Size</td><td>1</td><td>${params.winSize}</td><td>${params.winSize}</td></tr>
    <tr><td>Total Transmissions</td><td>${results['One-Bit SW'].totalTransmissions}</td><td>${results['Go-Back-N'].totalTransmissions}</td><td>${results['Selective Repeat'].totalTransmissions}</td></tr>
    <tr><td>Retransmissions</td><td>${results['One-Bit SW'].retransmissions}</td><td>${results['Go-Back-N'].retransmissions}</td><td>${results['Selective Repeat'].retransmissions}</td></tr>
    <tr><td>Packets Lost</td><td>${results['One-Bit SW'].packetsLost}</td><td>${results['Go-Back-N'].packetsLost}</td><td>${results['Selective Repeat'].packetsLost}</td></tr>
    <tr><td>ACKs Received</td><td>${results['One-Bit SW'].acksReceived}</td><td>${results['Go-Back-N'].acksReceived}</td><td>${results['Selective Repeat'].acksReceived}</td></tr>
    <tr><td>Total Time (ms)</td><td>${Math.round(results['One-Bit SW'].totalTimeMs)} ms</td><td>${Math.round(results['Go-Back-N'].totalTimeMs)} ms</td><td>${Math.round(results['Selective Repeat'].totalTimeMs)} ms</td></tr>
    <tr><td>Throughput (fps)</td><td>${results['One-Bit SW'].throughputFps}</td><td>${results['Go-Back-N'].throughputFps}</td><td>${results['Selective Repeat'].throughputFps}</td></tr>
    <tr><td>Efficiency (%)</td><td>${results['One-Bit SW'].efficiencyPct}%</td><td>${results['Go-Back-N'].efficiencyPct}%</td><td>${results['Selective Repeat'].efficiencyPct}%</td></tr>
  `;

  renderComparisonCharts(results);
  renderLossSensitivityChart(params);
}

function exportCSV() {
  if (!lastComparisonMetrics) {
    alert('No comparison data available to export.');
    return;
  }

  const headers = ['Protocol', 'Window Size', 'Total Transmissions', 'Retransmissions', 'Packets Lost', 'ACKs Received', 'Total Time (ms)', 'Throughput (fps)', 'Efficiency (%)'];
  const rows = Object.values(lastComparisonMetrics).map(m => [
    m.protocolName,
    m.windowSize,
    m.totalTransmissions,
    m.retransmissions,
    m.packetsLost,
    m.acksReceived,
    m.totalTimeMs,
    m.throughputFps,
    `${m.efficiencyPct}%`
  ]);

  let csvContent = 'data:text/csv;charset=utf-8,' + headers.join(',') + '\n' + rows.map(e => e.join(',')).join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', 'sliding_window_simulation_results.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
