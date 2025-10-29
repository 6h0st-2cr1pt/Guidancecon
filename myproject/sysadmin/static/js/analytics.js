// Analytics Dashboard Chart Initialization

// Theme colors matching the CHMSU design
const chartColors = {
  darkGreen: '#1a4d3a',
  accentYellow: '#F0DF10',
  orange: '#ff6b35',
  lightGray: '#BAD8B6',
  mediumGray: '#6c757d',
  white: '#ffffff',
  success: '#28a745',
  danger: '#dc3545',
  warning: '#ffc107',
  info: '#17a2b8'
};

// Chart.js default configuration
Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
Chart.defaults.color = '#1a252f';

// Status Pie Chart
const statusCtx = document.getElementById('statusChart');
if (statusCtx && analyticsData.status.labels.length > 0) {
  new Chart(statusCtx, {
    type: 'doughnut',
    data: {
      labels: analyticsData.status.labels,
      datasets: [{
        data: analyticsData.status.data,
        backgroundColor: [
          chartColors.warning,
          chartColors.success,
          chartColors.danger,
          chartColors.mediumGray
        ],
        borderWidth: 2,
        borderColor: chartColors.white
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 15,
            font: {
              size: 12,
              weight: '500'
            }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.parsed || 0;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((value / total) * 100).toFixed(1);
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}

// Monthly Trend Line Chart
const trendCtx = document.getElementById('trendChart');
if (trendCtx && analyticsData.monthly.labels.length > 0) {
  new Chart(trendCtx, {
    type: 'line',
    data: {
      labels: analyticsData.monthly.labels,
      datasets: [{
        label: 'Appointments',
        data: analyticsData.monthly.data,
        borderColor: chartColors.darkGreen,
        backgroundColor: 'rgba(26, 77, 58, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: chartColors.accentYellow,
        pointBorderColor: chartColors.darkGreen,
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: chartColors.darkGreen,
          padding: 12,
          titleFont: {
            size: 14,
            weight: 'bold'
          },
          bodyFont: {
            size: 13
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  });
}

// Counselor Bar Chart
const counselorCtx = document.getElementById('counselorChart');
if (counselorCtx && analyticsData.counselor.labels.length > 0) {
  new Chart(counselorCtx, {
    type: 'bar',
    data: {
      labels: analyticsData.counselor.labels,
      datasets: [{
        label: 'Appointments',
        data: analyticsData.counselor.data,
        backgroundColor: chartColors.darkGreen,
        borderColor: chartColors.darkGreen,
        borderWidth: 1,
        borderRadius: 6,
        hoverBackgroundColor: chartColors.orange
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      indexAxis: 'y',
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: chartColors.darkGreen,
          padding: 12
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            precision: 0
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y: {
          grid: {
            display: false
          },
          ticks: {
            font: {
              size: 11
            }
          }
        }
      }
    }
  });
}

// Time Slot Bar Chart
const timeslotCtx = document.getElementById('timeslotChart');
if (timeslotCtx && analyticsData.timeslot.labels.length > 0) {
  new Chart(timeslotCtx, {
    type: 'bar',
    data: {
      labels: analyticsData.timeslot.labels,
      datasets: [{
        label: 'Bookings',
        data: analyticsData.timeslot.data,
        backgroundColor: chartColors.accentYellow,
        borderColor: chartColors.darkGreen,
        borderWidth: 1,
        borderRadius: 6,
        hoverBackgroundColor: chartColors.orange
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: chartColors.darkGreen,
          padding: 12
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            font: {
              size: 10
            }
          }
        }
      }
    }
  });
}

// Program Bar Chart
const programCtx = document.getElementById('programChart');
if (programCtx && analyticsData.program.labels.length > 0) {
  new Chart(programCtx, {
    type: 'bar',
    data: {
      labels: analyticsData.program.labels,
      datasets: [{
        label: 'Appointments',
        data: analyticsData.program.data,
        backgroundColor: chartColors.orange,
        borderColor: chartColors.orange,
        borderWidth: 1,
        borderRadius: 6,
        hoverBackgroundColor: chartColors.darkGreen
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: chartColors.darkGreen,
          padding: 12
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            font: {
              size: 10
            },
            callback: function(value, index, ticks) {
              const label = this.getLabelForValue(value);
              return label.length > 15 ? label.substr(0, 15) + '...' : label;
            }
          }
        }
      }
    }
  });
}

