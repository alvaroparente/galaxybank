// Galaxy Bank JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initializeTooltips();
    initializeAnimations();
    initializeSidebar();
    initializeNotifications();
    
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
    // Auto-hide alerts após 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-persistent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
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