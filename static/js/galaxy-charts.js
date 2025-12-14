// ================================================
// GALAXY BANK - MODERN CHARTS SYSTEM
// Sistema de gráficos modernos usando Chart.js
// ================================================

// Configuração global do Chart.js
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", "Roboto", sans-serif';
Chart.defaults.font.size = 13;
Chart.defaults.color = '#636E72';
Chart.defaults.borderColor = '#E8ECEF';
Chart.defaults.plugins.legend.display = true;
Chart.defaults.plugins.legend.position = 'bottom';
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(26, 29, 41, 0.95)';
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.titleColor = '#FFFFFF';
Chart.defaults.plugins.tooltip.bodyColor = '#F5F7FA';

// Paleta de cores moderna
const modernColors = {
    primary: 'rgb(91, 79, 233)',
    secondary: 'rgb(0, 212, 255)',
    success: 'rgb(0, 230, 118)',
    warning: 'rgb(255, 184, 0)',
    danger: 'rgb(255, 82, 82)',
    accent: 'rgb(255, 107, 157)',
    
    // Variações com transparência
    primaryAlpha: 'rgba(91, 79, 233, 0.15)',
    secondaryAlpha: 'rgba(0, 212, 255, 0.15)',
    successAlpha: 'rgba(0, 230, 118, 0.15)',
    warningAlpha: 'rgba(255, 184, 0, 0.15)',
    dangerAlpha: 'rgba(255, 82, 82, 0.15)',
    accentAlpha: 'rgba(255, 107, 157, 0.15)',
    
    // Gradientes
    primaryGradient: ['rgb(102, 126, 234)', 'rgb(118, 75, 162)'],
    secondaryGradient: ['rgb(0, 212, 255)', 'rgb(91, 79, 233)'],
    successGradient: ['rgb(0, 230, 118)', 'rgb(0, 191, 165)'],
};

// ================================================
// GRÁFICO DE LINHA - Extrato/Transações
// ================================================
function createLineChart(canvasId, labels, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas ${canvasId} não encontrado`);
        return null;
    }

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(91, 79, 233, 0.2)');
    gradient.addColorStop(1, 'rgba(91, 79, 233, 0)');

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: options.label || 'Saldo',
                data: data,
                borderColor: modernColors.primary,
                backgroundColor: gradient,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: modernColors.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index',
            },
            plugins: {
                legend: {
                    display: options.showLegend !== false,
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: { weight: '600' }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            label += 'R$ ' + context.parsed.y.toFixed(2);
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false,
                    },
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toFixed(0);
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false,
                    }
                }
            }
        }
    });
}

// ================================================
// GRÁFICO DE BARRAS - Entradas vs Saídas
// ================================================
function createBarChart(canvasId, labels, entriesData, exitsData, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas ${canvasId} não encontrado`);
        return null;
    }

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Entradas',
                    data: entriesData,
                    backgroundColor: modernColors.successAlpha,
                    borderColor: modernColors.success,
                    borderWidth: 2,
                    borderRadius: 8,
                },
                {
                    label: 'Saídas',
                    data: exitsData,
                    backgroundColor: modernColors.dangerAlpha,
                    borderColor: modernColors.danger,
                    borderWidth: 2,
                    borderRadius: 8,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index',
            },
            plugins: {
                legend: {
                    display: options.showLegend !== false,
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: { weight: '600' }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            label += 'R$ ' + context.parsed.y.toFixed(2);
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false,
                    },
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toFixed(0);
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false,
                    }
                }
            }
        }
    });
}

// ================================================
// GRÁFICO DE PIZZA/DONUT - Categorias de Gastos
// ================================================
function createDoughnutChart(canvasId, labels, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas ${canvasId} não encontrado`);
        return null;
    }

    const colors = [
        modernColors.primary,
        modernColors.secondary,
        modernColors.success,
        modernColors.warning,
        modernColors.danger,
        modernColors.accent,
    ];

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 3,
                borderColor: '#fff',
                hoverBorderWidth: 4,
                hoverBorderColor: '#fff',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    display: options.showLegend !== false,
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { weight: '600' },
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                return data.labels.map((label, i) => {
                                    const value = data.datasets[0].data[i];
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return {
                                        text: `${label}: ${percentage}%`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        hidden: false,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) label += ': ';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            label += 'R$ ' + value.toFixed(2) + ' (' + percentage + '%)';
                            return label;
                        }
                    }
                }
            }
        }
    });
}

// ================================================
// GRÁFICO DE ÁREA - Fatura ao longo do tempo
// ================================================
function createAreaChart(canvasId, labels, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas ${canvasId} não encontrado`);
        return null;
    }

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(255, 184, 0, 0.3)');
    gradient.addColorStop(1, 'rgba(255, 184, 0, 0)');

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: options.label || 'Valor',
                data: data,
                borderColor: modernColors.warning,
                backgroundColor: gradient,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: modernColors.warning,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index',
            },
            plugins: {
                legend: {
                    display: options.showLegend !== false,
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: { weight: '600' }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            label += 'R$ ' + context.parsed.y.toFixed(2);
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false,
                    },
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toFixed(0);
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false,
                    }
                }
            }
        }
    });
}

// ================================================
// GRÁFICO MISTO - Saldo e Transações
// ================================================
function createMixedChart(canvasId, labels, lineData, barData, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas ${canvasId} não encontrado`);
        return null;
    }

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(91, 79, 233, 0.2)');
    gradient.addColorStop(1, 'rgba(91, 79, 233, 0)');

    return new Chart(ctx, {
        data: {
            labels: labels,
            datasets: [
                {
                    type: 'line',
                    label: 'Saldo',
                    data: lineData,
                    borderColor: modernColors.primary,
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y',
                },
                {
                    type: 'bar',
                    label: 'Transações',
                    data: barData,
                    backgroundColor: modernColors.secondaryAlpha,
                    borderColor: modernColors.secondary,
                    borderWidth: 2,
                    borderRadius: 8,
                    yAxisID: 'y1',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: options.showLegend !== false,
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: { weight: '600' }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false,
                    },
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toFixed(0);
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false,
                    },
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false,
                    }
                }
            }
        }
    });
}

// ================================================
// FUNÇÕES UTILITÁRIAS
// ================================================

// Formatar moeda brasileira
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Gerar cores aleatórias para gráficos dinâmicos
function generateColors(count) {
    const colors = [];
    const baseColors = Object.values(modernColors).filter(c => !c.includes('Alpha') && !Array.isArray(c));
    
    for (let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
    }
    
    return colors;
}

// Animação de contadores
function animateValue(elementId, start, end, duration) {
    const obj = document.getElementById(elementId);
    if (!obj) return;
    
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        obj.textContent = formatCurrency(current);
    }, 16);
}

// Atualizar gráfico com novos dados
function updateChart(chart, newLabels, newData) {
    chart.data.labels = newLabels;
    chart.data.datasets[0].data = newData;
    chart.update('active');
}

// Exportar para uso global
window.GalaxyCharts = {
    createLineChart,
    createBarChart,
    createDoughnutChart,
    createAreaChart,
    createMixedChart,
    formatCurrency,
    generateColors,
    animateValue,
    updateChart,
    colors: modernColors
};

console.log('Galaxy Charts System loaded successfully');
