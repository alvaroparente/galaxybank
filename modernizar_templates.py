"""
Script para modernizar todos os templates HTML do Galaxy Bank
Design inspirado em apps modernos como Nubank, Revolut, N26
"""

import os
import re
from pathlib import Path

# Diretório base
BASE_DIR = Path(r"c:\Users\victo\Documents\galaxybank")

# Componentes reutilizáveis
SIDEBAR_CLIENTE_MODERNO = '''    <div class="col-md-3 col-lg-2 sidebar">
        <div class="p-3">
            <h6>MENU</h6>
            <ul class="nav flex-column">
                <li class="nav-item">
                    <a class="nav-link {active_dashboard}" href="{% url 'usuarios:dashboard_cliente' %}">
                        <i class="bi bi-speedometer2"></i> Dashboard
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {active_transferencia}" href="{% url 'usuarios:transferencia' %}">
                        <i class="bi bi-arrow-left-right"></i> Transferência
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {active_deposito}" href="{% url 'usuarios:deposito' %}">
                        <i class="bi bi-wallet-fill"></i> Depósito
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {active_extrato}" href="{% url 'usuarios:extrato' %}">
                        <i class="bi bi-list-check"></i> Extrato
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {active_loja}" href="{% url 'loja:home' %}">
                        <i class="bi bi-shop"></i> Loja
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {active_credito}" href="{% url 'credito:solicitar' %}">
                        <i class="bi bi-credit-card"></i> Crédito
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link {active_faturas}" href="{% url 'faturas:minhas_faturas' %}">
                        <i class="bi bi-receipt"></i> Faturas
                    </a>
                </li>
            </ul>
        </div>
    </div>'''

def modernizar_sidebar(content, active_page=''):
    """Substitui sidebar antiga por moderna"""
    # Padrão para encontrar sidebar
    pattern = r'<div class="col-md-3.*?sidebar.*?>.*?</div>\s*</div>'
    
    # Preparar sidebar com página ativa
    sidebar = SIDEBAR_CLIENTE_MODERNO.format(
        active_dashboard='active' if active_page == 'dashboard' else '',
        active_transferencia='active' if active_page == 'transferencia' else '',
        active_deposito='active' if active_page == 'deposito' else '',
        active_extrato='active' if active_page == 'extrato' else '',
        active_loja='active' if active_page == 'loja' else '',
        active_credito='active' if active_page == 'credito' else '',
        active_faturas='active' if active_page == 'faturas' else '',
    )
    
    return re.sub(pattern, sidebar, content, flags=re.DOTALL)

def modernizar_cards(content):
    """Moderniza cards"""
    # Substituir classes de cards antigos
    content = content.replace('class="card shadow-sm"', 'class="card"')
    content = content.replace('class="card border-0 shadow-sm"', 'class="card stats-card"')
    return content

def modernizar_botoes(content):
    """Moderniza botões"""
    content = content.replace('btn btn-primary', 'btn btn-primary')
    return content

def processar_template(filepath, active_page=''):
    """Processa um template individual"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Aplicar modernizações
        content = modernizar_sidebar(content, active_page)
        content = modernizar_cards(content)
        content = modernizar_botoes(content)
        
        # Salvar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Modernizado: {filepath.name}")
        return True
    except Exception as e:
        print(f"❌ Erro em {filepath.name}: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando modernização dos templates Galaxy Bank\n")
    
    # Mapear templates e suas páginas ativas
    templates = {
        'usuarios/templates/usuarios/transferencia.html': 'transferencia',
        'usuarios/templates/usuarios/deposito.html': 'deposito',
        'usuarios/templates/usuarios/perfil.html': 'perfil',
        'usuarios/templates/usuarios/perfil_editar.html': 'perfil',
    }
    
    sucesso = 0
    falha = 0
    
    for template_path, active in templates.items():
        filepath = BASE_DIR / template_path
        if filepath.exists():
            if processar_template(filepath, active):
                sucesso += 1
            else:
                falha += 1
        else:
            print(f"⚠️  Não encontrado: {template_path}")
    
    print(f"\n✅ Modernizados: {sucesso}")
    print(f"❌ Falhas: {falha}")

if __name__ == '__main__':
    main()
