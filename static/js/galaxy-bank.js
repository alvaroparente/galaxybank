// Galaxy Bank JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initializeTooltips();
    initializeAnimations();
    initializeSidebar();
    initializeNotifications();
    loadSoundPreference();
    
    console.log('Galaxy Bank system initialized successfully');
});

// Inicializar tooltips do Bootstrap
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Animações de entrada para elementos
function initializeAnimations() {
    const animateElements = document.querySelectorAll('.stats-card, .card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fadein');
            }
        });
    });

    animateElements.forEach(el => {
        observer.observe(el);
    });
}

// Controle da sidebar em dispositivos móveis
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
        
        // Fechar sidebar ao clicar fora
        document.addEventListener('click', function(e) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        });
    }
}

// Sistema de notificações
function initializeNotifications() {
    // Criar container de notificações se não existir
    if (!document.querySelector('.galaxy-notifications-container')) {
        const container = document.createElement('div');
        container.className = 'galaxy-notifications-container';
        document.body.appendChild(container);
    }
    
    // Processar mensagens Django
    processDjangoMessages();
}

// Processar mensagens Django e convertê-las para notificações personalizadas
function processDjangoMessages() {
    const djangoMessages = document.querySelectorAll('.django-messages .alert');
    djangoMessages.forEach(alert => {
        let type = 'info';
        if (alert.classList.contains('alert-success')) type = 'success';
        else if (alert.classList.contains('alert-danger')) type = 'error';
        else if (alert.classList.contains('alert-warning')) type = 'warning';
        
        const message = alert.textContent.trim();
        showNotification(message, type);
        
        // Remover alert original
        alert.remove();
    });
    
    // Remover container de mensagens Django se vazio
    const messagesContainer = document.querySelector('.django-messages');
    if (messagesContainer && messagesContainer.children.length === 0) {
        messagesContainer.remove();
    }
}

// Função principal para mostrar notificações
function showNotification(message, type = 'info', duration = 5000, options = {}) {
    const container = document.querySelector('.galaxy-notifications-container');
    if (!container) return;
    
    // Configurações por tipo
    const config = {
        success: {
            icon: 'bi-check-circle-fill',
            title: options.title || 'Sucesso!',
            sound: 'success'
        },
        error: {
            icon: 'bi-x-circle-fill',
            title: options.title || 'Erro!',
            sound: 'error'
        },
        warning: {
            icon: 'bi-exclamation-triangle-fill',
            title: options.title || 'Atenção!',
            sound: 'warning'
        },
        info: {
            icon: 'bi-info-circle-fill',
            title: options.title || 'Informação',
            sound: 'info'
        }
    };
    
    const currentConfig = config[type] || config.info;
    
    // Verificar se já existe notificação similar
    const existingNotifications = container.querySelectorAll('.galaxy-notification');
    let similarCount = 0;
    existingNotifications.forEach(notif => {
        const msg = notif.querySelector('.galaxy-notification-message');
        if (msg && msg.textContent === message) {
            similarCount++;
        }
    });
    
    // Criar elemento de notificação
    const notification = document.createElement('div');
    notification.className = `galaxy-notification ${type} ${options.important ? 'important' : ''}`;
    
    // Badge de contador se houver notificações similares
    const badgeHtml = similarCount > 0 ? `<span class="galaxy-notification-badge">${similarCount + 1}</span>` : '';
    
    notification.innerHTML = `
        ${badgeHtml}
        <div class="galaxy-notification-icon">
            <i class="bi ${currentConfig.icon}"></i>
        </div>
        <div class="galaxy-notification-content">
            <div class="galaxy-notification-title">${currentConfig.title}</div>
            <div class="galaxy-notification-message">${message}</div>
        </div>
        <button class="galaxy-notification-close" aria-label="Fechar">
            <i class="bi bi-x"></i>
        </button>
        <div class="galaxy-notification-progress"></div>
    `;
    
    // Adicionar ao container
    container.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Botão de fechar
    const closeBtn = notification.querySelector('.galaxy-notification-close');
    closeBtn.addEventListener('click', () => removeNotification(notification));
    
    // Auto-remover após duração
    if (duration > 0) {
        setTimeout(() => removeNotification(notification), duration);
    }
    
    // Tocar som (opcional)
    if (options.playSound !== false) {
        playNotificationSound(type);
    }
    
    // Vibrar no mobile (se suportado)
    if (navigator.vibrate && options.vibrate !== false) {
        const vibrationPattern = {
            success: [50, 50, 50],
            error: [100, 50, 100],
            warning: [50, 100, 50],
            info: [50]
        };
        navigator.vibrate(vibrationPattern[type] || [50]);
    }
    
    return notification;
}

// Remover notificação com animação
function removeNotification(notification) {
    notification.classList.add('hide');
    notification.classList.remove('show');
    setTimeout(() => {
        if (notification.parentElement) {
            notification.parentElement.removeChild(notification);
        }
    }, 400);
}

// Tocar som de notificação (opcional)
function playNotificationSound(type) {
    // Criar contexto de áudio se não existir
    if (!window.GalaxyBankAudio) {
        window.GalaxyBankAudio = {
            enabled: true,
            context: null
        };
    }
    
    if (!window.GalaxyBankAudio.enabled) return;
    
    // Sons sintéticos usando Web Audio API
    try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!window.GalaxyBankAudio.context) {
            window.GalaxyBankAudio.context = new AudioContext();
        }
        
        const ctx = window.GalaxyBankAudio.context;
        const oscillator = ctx.createOscillator();
        const gainNode = ctx.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);
        
        // Configurações de som por tipo
        const soundConfig = {
            success: { freq: [523.25, 659.25], duration: 0.15 },
            error: { freq: [329.63, 261.63], duration: 0.2 },
            warning: { freq: [440], duration: 0.15 },
            info: { freq: [523.25], duration: 0.1 }
        };
        
        const config = soundConfig[type] || soundConfig.info;
        
        // Tocar sequência de notas
        config.freq.forEach((freq, index) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            
            osc.connect(gain);
            gain.connect(ctx.destination);
            
            osc.frequency.value = freq;
            osc.type = 'sine';
            
            gain.gain.setValueAtTime(0.1, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + config.duration);
            
            const startTime = ctx.currentTime + (index * config.duration);
            osc.start(startTime);
            osc.stop(startTime + config.duration);
        });
    } catch (e) {
        // Navegador não suporta Web Audio API
        console.log('Audio not supported');
    }
}

// Habilitar/desabilitar sons
function toggleNotificationSounds(enabled) {
    if (window.GalaxyBankAudio) {
        window.GalaxyBankAudio.enabled = enabled;
        localStorage.setItem('galaxybank_sounds', enabled ? 'true' : 'false');
    }
}

// Carregar preferência de sons
function loadSoundPreference() {
    const preference = localStorage.getItem('galaxybank_sounds');
    if (preference !== null) {
        toggleNotificationSounds(preference === 'true');
    }
}

// Atalhos para tipos específicos
function showSuccessNotification(message, duration = 5000, options = {}) {
    return showNotification(message, 'success', duration, options);
}

function showErrorNotification(message, duration = 5000, options = {}) {
    return showNotification(message, 'error', duration, options);
}

function showWarningNotification(message, duration = 5000, options = {}) {
    return showNotification(message, 'warning', duration, options);
}

function showInfoNotification(message, duration = 5000, options = {}) {
    return showNotification(message, 'info', duration, options);
}

// Notificação com loading/spinner
function showLoadingNotification(message, title = 'Processando...') {
    const notification = showNotification(
        `<span class="galaxy-notification-spinner"></span>${message}`,
        'info',
        0,
        { title: title, playSound: false, vibrate: false }
    );
    return {
        notification,
        close: () => removeNotification(notification),
        success: (msg) => {
            removeNotification(notification);
            showSuccessNotification(msg);
        },
        error: (msg) => {
            removeNotification(notification);
            showErrorNotification(msg);
        }
    };
}

// Notificação de confirmação com ações
function showConfirmNotification(message, onConfirm, onCancel, options = {}) {
    const notification = showNotification(message, 'warning', 0, {
        title: options.title || 'Confirmação',
        playSound: false
    });
    
    // Adicionar botões de ação
    const content = notification.querySelector('.galaxy-notification-content');
    const actions = document.createElement('div');
    actions.className = 'galaxy-notification-actions mt-2 d-flex gap-2';
    actions.innerHTML = `
        <button class="btn btn-sm btn-success confirm-btn px-3">
            <i class="bi bi-check-lg me-1"></i> ${options.confirmText || 'Confirmar'}
        </button>
        <button class="btn btn-sm btn-secondary cancel-btn px-3">
            <i class="bi bi-x-lg me-1"></i> ${options.cancelText || 'Cancelar'}
        </button>
    `;
    content.appendChild(actions);
    
    // Remover a barra de progresso para confirmações
    const progress = notification.querySelector('.galaxy-notification-progress');
    if (progress) progress.remove();
    
    // Event listeners
    actions.querySelector('.confirm-btn').addEventListener('click', () => {
        removeNotification(notification);
        if (onConfirm) onConfirm();
    });
    
    actions.querySelector('.cancel-btn').addEventListener('click', () => {
        removeNotification(notification);
        if (onCancel) onCancel();
    });
    
    return notification;
}

// Notificação com progresso customizado
function showProgressNotification(message, title = 'Carregando...') {
    const notification = showNotification(message, 'info', 0, { 
        title: title,
        playSound: false 
    });
    
    // Remover barra de progresso padrão
    const defaultProgress = notification.querySelector('.galaxy-notification-progress');
    if (defaultProgress) defaultProgress.remove();
    
    // Adicionar barra de progresso customizada
    const content = notification.querySelector('.galaxy-notification-content');
    const progressBar = document.createElement('div');
    progressBar.className = 'mt-2';
    progressBar.innerHTML = `
        <div class="progress" style="height: 8px; border-radius: 4px;">
            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                 role="progressbar" 
                 style="width: 0%; background: linear-gradient(90deg, #0dcaf0, #0d6efd);">
            </div>
        </div>
    `;
    content.appendChild(progressBar);
    
    const bar = progressBar.querySelector('.progress-bar');
    
    return {
        notification,
        setProgress: (percent) => {
            bar.style.width = `${Math.min(100, Math.max(0, percent))}%`;
            if (percent >= 100) {
                bar.classList.remove('progress-bar-animated');
            }
        },
        complete: (msg) => {
            bar.style.width = '100%';
            bar.classList.remove('progress-bar-animated');
            setTimeout(() => {
                removeNotification(notification);
                showSuccessNotification(msg || 'Concluído!');
            }, 500);
        },
        error: (msg) => {
            removeNotification(notification);
            showErrorNotification(msg || 'Erro ao processar');
        }
    };
}

// Função para formatar valores monetários
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Função para formatar CPF
function formatCPF(cpf) {
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

// Função para validar CPF
function validateCPF(cpf) {
    cpf = cpf.replace(/[^\d]+/g, '');
    
    if (cpf.length !== 11 || !!cpf.match(/(\d)\1{10}/)) {
        return false;
    }
    
    const digits = cpf.split('').map(el => +el);
    const rest = (count) => (digits.slice(0, count-12)
        .reduce((soma, el, index) => (soma + el * (count-index)), 0)*10) % 11 % 10;
    
    return rest(10) === digits[9] && rest(11) === digits[10];
}

// Função para mostrar loading
function showLoading(buttonElement) {
    if (buttonElement) {
        const originalText = buttonElement.innerHTML;
        buttonElement.innerHTML = '<div class="loading-spinner me-2"></div>Carregando...';
        buttonElement.disabled = true;
        
        // Retornar função para restaurar estado
        return function() {
            buttonElement.innerHTML = originalText;
            buttonElement.disabled = false;
        };
    }
}

// Função para confirmar ações
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Função para copiar texto para clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copiado para a área de transferência!', 'success');
    }).catch(() => {
        showNotification('Erro ao copiar texto', 'error');
    });
}

// Função para mostrar notificações toast
function showNotification(message, type = 'info') {
    // Criar elemento toast
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Container para toasts
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Adicionar toast
    const toastElement = document.createElement('div');
    toastElement.innerHTML = toastHtml;
    toastContainer.appendChild(toastElement.firstElementChild);
    
    // Mostrar toast
    const toast = new bootstrap.Toast(toastContainer.lastElementChild);
    toast.show();
    
    // Remover após esconder
    toastContainer.lastElementChild.addEventListener('hidden.bs.toast', () => {
        toastContainer.removeChild(toastContainer.lastElementChild);
    });
}

// Função para atualizar dados em tempo real
function refreshDashboardData() {
    // Simular atualização de dados
    const elements = document.querySelectorAll('[data-auto-refresh]');
    elements.forEach(element => {
        element.classList.add('animate-pulse');
        setTimeout(() => {
            element.classList.remove('animate-pulse');
        }, 1000);
    });
}

// Auto-refresh a cada 30 segundos
setInterval(refreshDashboardData, 30000);

// Função para validar formulários
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        }
    });
    
    return isValid;
}

// Event listeners para formulários
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (!validateForm(form)) {
        e.preventDefault();
        showNotification('Por favor, preencha todos os campos obrigatórios', 'error');
    }
});

// Função para logout com confirmação
function logout() {
    confirmAction('Tem certeza que deseja sair?', function() {
        window.location.href = '/logout/';
    });
}

// Atalhos de teclado
document.addEventListener('keydown', function(e) {
    // Ctrl+L para logout
    if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        logout();
    }
    
    // ESC para fechar modals/sidebar
    if (e.key === 'Escape') {
        const sidebar = document.querySelector('.sidebar.show');
        if (sidebar) {
            sidebar.classList.remove('show');
        }
    }
});

// Função para tema escuro/claro (futuro)
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// Carregar tema salvo
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-theme');
}

// Exportar funções globais
window.GalaxyBank = {
    formatCurrency,
    formatCPF,
    validateCPF,
    showLoading,
    confirmAction,
    copyToClipboard,
    showNotification,
    validateForm,
    logout,
    toggleTheme
};