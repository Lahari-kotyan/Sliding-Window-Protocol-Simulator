/**
 * Chart.js Integration for Web Protocol Comparison Graphs
 */

let comparisonChartInstance = null;
let sensitivityChartInstance = null;

function renderComparisonCharts(metricsDict) {
  const protocols = Object.keys(metricsDict);
  const throughputs = protocols.map(p => metricsDict[p].throughputFps);
  const efficiencies = protocols.map(p => metricsDict[p].efficiencyPct);
  const retransmissions = protocols.map(p => metricsDict[p].retransmissions);
  const totalTimes = protocols.map(p => metricsDict[p].totalTimeMs);

  const ctxComp = document.getElementById('comparisonChart').getContext('2d');
  
  if (comparisonChartInstance) {
    comparisonChartInstance.destroy();
  }

  comparisonChartInstance = new Chart(ctxComp, {
    type: 'bar',
    data: {
      labels: protocols,
      datasets: [
        {
          label: 'Throughput (fps)',
          data: throughputs,
          backgroundColor: 'rgba(59, 130, 246, 0.75)',
          borderColor: '#3b82f6',
          borderWidth: 1
        },
        {
          label: 'Efficiency (%)',
          data: efficiencies,
          backgroundColor: 'rgba(16, 185, 129, 0.75)',
          borderColor: '#10b981',
          borderWidth: 1
        },
        {
          label: 'Retransmissions',
          data: retransmissions,
          backgroundColor: 'rgba(239, 68, 68, 0.75)',
          borderColor: '#ef4444',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8' } },
        title: { display: true, text: 'Protocol Comparison Metrics', color: '#f8fafc', font: { size: 14 } }
      },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
      }
    }
  });
}

function renderLossSensitivityChart(params) {
  const lossRates = [0, 10, 20, 30, 40, 50];
  const ctxSens = document.getElementById('sensitivityChart').getContext('2d');

  const protoFactories = [
    { name: 'One-Bit SW', color: '#ef4444', factory: (n, w, t) => new OneBitProtocol(n, t) },
    { name: 'Go-Back-N', color: '#f59e0b', factory: (n, w, t) => new GoBackNProtocol(n, w, t) },
    { name: 'Selective Repeat', color: '#10b981', factory: (n, w, t) => new SelectiveRepeatProtocol(n, w, t) }
  ];

  const datasets = protoFactories.map(pConfig => {
    const dataPoints = lossRates.map(lossPct => {
      const proto = pConfig.factory(params.numFrames, params.winSize, params.timeout);
      const net = new NetworkChannel(params.transDelay, params.ackDelay, lossPct, params.ackLoss, params.seed);
      const sim = new Simulator(proto, net);
      const m = sim.run();
      return m.throughputFps;
    });

    return {
      label: pConfig.name,
      data: dataPoints,
      borderColor: pConfig.color,
      backgroundColor: pConfig.color,
      tension: 0.3,
      fill: false
    };
  });

  if (sensitivityChartInstance) {
    sensitivityChartInstance.destroy();
  }

  sensitivityChartInstance = new Chart(ctxSens, {
    type: 'line',
    data: {
      labels: lossRates.map(l => `${l}%`),
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8' } },
        title: { display: true, text: 'Throughput (fps) vs Packet Loss %', color: '#f8fafc', font: { size: 14 } }
      },
      scales: {
        x: { title: { display: true, text: 'Packet Loss %', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
        y: { title: { display: true, text: 'Throughput (fps)', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
      }
    }
  });
}
