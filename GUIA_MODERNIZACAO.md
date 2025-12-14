# 🚀 GUIA RÁPIDO: Como Modernizar os Templates Restantes

## 📖 Template Base para Copiar e Adaptar

### 1. Estrutura Básica
```html
{% extends 'usuarios/base.html' %}

{% block title %}Título - Galaxy Bank{% endblock %}

{% block content %}
<div class="row g-0">
    <!-- Sidebar -->
    <div class="col-md-3 col-lg-2 sidebar">
        <h6>NAVEGAÇÃO</h6>
        <ul class="nav flex-column">
            <li class="nav-item">
                <a class="nav-link {% if active == 'dashboard' %}active{% endif %}" href="{% url 'usuarios:dashboard_cliente' %}">
                    <i class="bi bi-speedometer2"></i> Dashboard
                </a>
            </li>
            <!-- Adicionar mais links -->
        </ul>
    </div>

    <!-- Main Content -->
    <div class="col-md-9 col-lg-10 main-content">
        <!-- Header -->
        <div class="dashboard-header animate-fadein mb-4">
            <div>
                <h1><i class="bi bi-icon" style="color: var(--galaxy-primary);"></i> Título</h1>
                <p class="text-muted mb-0">Descrição da página</p>
            </div>
            <div class="text-end">
                <!-- Botões de ação -->
            </div>
        </div>

        <!-- Conteúdo aqui -->
    </div>
</div>
{% endblock %}
```

---

## 📊 Cards de Estatísticas (Stats Cards)

### Template:
```html
<div class="row g-4 mb-4">
    <div class="col-md-6 col-lg-3 animate-fadein" style="animation-delay: 0.1s;">
        <div class="stats-card">
            <div class="stats-icon" style="background: var(--gradient-primary);">
                <i class="bi bi-wallet2"></i>
            </div>
            <div class="stats-value">R$ 1.500,00</div>
            <div class="stats-label">Saldo Disponível</div>
        </div>
    </div>
    <!-- Repetir para cada stat -->
</div>
```

### Variações de Cores:
- `var(--gradient-primary)` - Roxo
- `var(--gradient-secondary)` - Azul
- `var(--gradient-success)` - Verde
- `var(--gradient-warning)` - Amarelo/Laranja
- `var(--gradient-error)` - Vermelho

---

## 📝 Formulários Modernos

### Template:
```html
<div class="card form-card animate-fadein">
    <div class="card-header">
        <h5 class="mb-0"><i class="bi bi-pencil"></i> Formulário</h5>
    </div>
    <div class="card-body">
        <form method="post">
            {% csrf_token %}
            
            <div class="mb-4">
                <label class="form-label">
                    <i class="bi bi-person"></i> Campo
                </label>
                <input type="text" class="form-control" placeholder="Digite...">
                <small class="form-text text-muted">Dica útil</small>
            </div>

            <div class="text-end">
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-check-circle"></i> Salvar
                </button>
            </div>
        </form>
    </div>
</div>

<style>
.form-card {
    max-width: 600px;
    margin: 0 auto;
}
</style>
```

---

## 📋 Lista de Items

### Template:
```html
<div class="card transaction-card animate-fadein">
    <div class="card-header">
        <h5 class="mb-0"><i class="bi bi-list"></i> Lista</h5>
    </div>
    <div class="card-body p-0">
        <div class="transaction-list">
            {% for item in items %}
            <div class="transaction-item">
                <div class="d-flex align-items-center">
                    <div class="transaction-icon transaction-icon-success">
                        <i class="bi bi-check"></i>
                    </div>
                    <div class="transaction-details">
                        <div class="transaction-title">{{ item.titulo }}</div>
                        <div class="transaction-date">{{ item.data }}</div>
                    </div>
                </div>
                <div class="transaction-amount">
                    R$ {{ item.valor }}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
```

---

## 📊 Gráficos

### Linha (Evolução):
```html
<div class="card chart-card">
    <div class="card-header">
        <h5 class="mb-0"><i class="bi bi-graph-up"></i> Evolução</h5>
    </div>
    <div class="card-body">
        <div class="chart-container" style="height: 300px;">
            <canvas id="lineChart"></canvas>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const labels = ['Jan', 'Fev', 'Mar', 'Abr'];
    const data = [1000, 1500, 1200, 1800];
    GalaxyCharts.createLineChart('lineChart', labels, data);
});
</script>
```

### Pizza (Distribuição):
```html
<div class="card chart-card">
    <div class="card-header">
        <h5 class="mb-0"><i class="bi bi-pie-chart"></i> Distribuição</h5>
    </div>
    <div class="card-body">
        <div class="chart-container" style="height: 300px;">
            <canvas id="pieChart"></canvas>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const labels = ['Categoria A', 'Categoria B', 'Categoria C'];
    const data = [30, 50, 20];
    GalaxyCharts.createPieChart('pieChart', labels, data);
});
</script>
```

### Donut (Progresso):
```html
<div class="card chart-card">
    <div class="card-header">
        <h5 class="mb-0"><i class="bi bi-arrow-clockwise"></i> Progresso</h5>
    </div>
    <div class="card-body">
        <div class="chart-container" style="height: 250px;">
            <canvas id="donutChart"></canvas>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const percentual = 75;
    GalaxyCharts.createDoughnutChart('donutChart', 
        ['Completo', 'Restante'], 
        [percentual, 100 - percentual],
        { centerText: percentual + '%', cutout: '75%' }
    );
});
</script>
```

### Barras (Comparação):
```html
<div class="card chart-card">
    <div class="card-header">
        <h5 class="mb-0"><i class="bi bi-bar-chart"></i> Comparação</h5>
    </div>
    <div class="card-body">
        <div class="chart-container" style="height: 300px;">
            <canvas id="barChart"></canvas>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const labels = ['Jan', 'Fev', 'Mar'];
    const entradas = [1000, 1500, 1200];
    const saidas = [800, 900, 1000];
    GalaxyCharts.createBarChart('barChart', labels, entradas, saidas);
});
</script>
```

---

## 🎨 Barra de Progresso Moderna

```html
<div class="progress-modern mb-2" style="height: 32px;">
    <div class="progress-bar-modern" 
         style="width: 75%; background: var(--gradient-success);">
        <span>75%</span>
    </div>
</div>

<style>
.progress-modern {
    background: var(--galaxy-border);
    border-radius: var(--radius-full);
    overflow: hidden;
}

.progress-bar-modern {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: white;
    font-weight: 700;
    font-size: 14px;
    transition: width 0.6s ease;
}
</style>
```

---

## 📅 Timeline Vertical

```html
<div class="timeline">
    {% for evento in eventos %}
    <div class="timeline-item">
        <div class="timeline-marker timeline-marker-success"></div>
        <div class="timeline-content">
            <div class="timeline-header">
                <strong>{{ evento.titulo }}</strong>
                <span class="timeline-date">{{ evento.data }}</span>
            </div>
            <div class="timeline-body">
                {{ evento.descricao }}
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<style>
.timeline {
    position: relative;
    padding-left: 40px;
}

.timeline-item {
    position: relative;
    padding-bottom: 24px;
}

.timeline-marker {
    position: absolute;
    left: -40px;
    top: 0;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border: 3px solid var(--galaxy-lighter);
}

.timeline-marker-success { background: var(--galaxy-success); }
.timeline-marker-warning { background: var(--galaxy-warning); }
.timeline-marker-danger { background: var(--galaxy-error); }

.timeline-item::before {
    content: '';
    position: absolute;
    left: -32px;
    top: 16px;
    width: 2px;
    height: calc(100% - 8px);
    background: var(--galaxy-border);
}

.timeline-item:last-child::before {
    display: none;
}

.timeline-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}

.timeline-date {
    font-size: 13px;
    color: var(--galaxy-text-secondary);
}
</style>
```

---

## 🎯 Ações Rápidas

```html
<div class="card quick-actions-card mb-4">
    <div class="card-header">
        <h5 class="mb-0"><i class="bi bi-lightning-fill"></i> Ações Rápidas</h5>
    </div>
    <div class="card-body">
        <div class="row g-3">
            <div class="col-6 col-md-4 col-lg-2">
                <a href="#" class="quick-action-btn">
                    <div class="quick-action-icon" style="background: var(--gradient-primary);">
                        <i class="bi bi-plus"></i>
                    </div>
                    <span>Adicionar</span>
                </a>
            </div>
            <!-- Repetir para cada ação -->
        </div>
    </div>
</div>

<style>
.quick-action-btn {
    text-decoration: none;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 16px;
    border-radius: var(--radius-md);
    transition: all 0.3s ease;
    color: var(--galaxy-text);
}

.quick-action-btn:hover {
    transform: translateY(-8px);
}

.quick-action-icon {
    width: 56px;
    height: 56px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    box-shadow: var(--shadow-colored);
}

.quick-action-btn:hover .quick-action-icon {
    transform: scale(1.1);
}
</style>
```

---

## ❌ Empty State

```html
<div class="empty-state">
    <div class="empty-state-icon">
        <i class="bi bi-inbox"></i>
    </div>
    <h5 class="empty-state-title">Nenhum item encontrado</h5>
    <p class="empty-state-text">
        Você ainda não possui itens cadastrados.
    </p>
    <div class="empty-state-actions">
        <a href="#" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Adicionar Item
        </a>
    </div>
</div>

<style>
.empty-state {
    padding: 64px 32px;
    text-align: center;
}

.empty-state-icon {
    font-size: 64px;
    color: var(--galaxy-border);
    margin-bottom: 24px;
}

.empty-state-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
}

.empty-state-text {
    color: var(--galaxy-text-secondary);
    margin-bottom: 24px;
}
</style>
```

---

## 🎨 Badges Modernos

```html
<!-- Success -->
<span class="badge" style="background: var(--gradient-success); font-size: 14px; padding: 8px 16px;">
    <i class="bi bi-check-circle"></i> Aprovado
</span>

<!-- Warning -->
<span class="badge" style="background: var(--gradient-warning); font-size: 14px; padding: 8px 16px;">
    <i class="bi bi-clock"></i> Pendente
</span>

<!-- Error -->
<span class="badge" style="background: var(--gradient-error); font-size: 14px; padding: 8px 16px;">
    <i class="bi bi-x-circle"></i> Rejeitado
</span>

<!-- Info -->
<span class="badge" style="background: var(--gradient-secondary); font-size: 14px; padding: 8px 16px;">
    <i class="bi bi-info-circle"></i> Informação
</span>
```

---

## 📱 Tabela Responsiva

```html
<div class="card">
    <div class="card-header">
        <h5 class="mb-0"><i class="bi bi-table"></i> Tabela</h5>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-modern">
                <thead>
                    <tr>
                        <th>Coluna 1</th>
                        <th>Coluna 2</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr>
                        <td>{{ item.campo1 }}</td>
                        <td>{{ item.campo2 }}</td>
                        <td>
                            <a href="#" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-eye"></i>
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<style>
.table-modern thead th {
    background: var(--galaxy-light);
    font-weight: 700;
    text-transform: uppercase;
    font-size: 12px;
    color: var(--galaxy-text-secondary);
    padding: 16px;
    border: none;
}

.table-modern tbody td {
    padding: 16px;
    vertical-align: middle;
    border: none;
}

.table-modern tbody tr {
    background: var(--galaxy-lighter);
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
}

.table-modern tbody tr:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}
</style>
```

---

## ✅ CHECKLIST para Cada Template

- [ ] Sidebar com navegação moderna
- [ ] Header com título e ícone
- [ ] Cards de estatísticas (se aplicável)
- [ ] Animações com delays escalonados
- [ ] Cores usando variáveis CSS
- [ ] Ícones Bootstrap apropriados
- [ ] Responsivo (col-md, col-lg)
- [ ] Empty state (se lista vazia)
- [ ] Botões com ícones
- [ ] Hover effects
- [ ] Gráficos (se dados numéricos)
- [ ] Espaçamento consistente (g-4, mb-4)
- [ ] Typography hierárquica

---

## 🔥 Dicas Rápidas

1. **Sempre use variáveis CSS**: `var(--galaxy-primary)` ao invés de cores diretas
2. **Animações**: Adicione `animate-fadein` e `animation-delay` progressivo
3. **Ícones**: Um ícone apropriado faz toda diferença
4. **Gradientes**: Use os gradientes pré-definidos para consistência
5. **Hover**: Sempre adicione efeito hover em elementos clicáveis
6. **Responsivo**: Teste em mobile, tablet e desktop
7. **Empty States**: Nunca deixe uma lista vazia sem mensagem
8. **Loading**: Considere estados de carregamento
9. **Feedback**: Sempre dê feedback visual para ações
10. **Consistência**: Siga os padrões dos templates já modernizados

---

## 📚 Referências

- **Templates Completos**: Ver `dashboard_cliente.html`, `extrato.html`, `minhas_faturas.html`, `detalhes_fatura.html`
- **CSS**: `static/css/galaxy-bank.css`
- **JS Gráficos**: `static/js/galaxy-charts.js`
- **Documentação**: `MODERNIZACAO_TEMPLATES.md` e `RESUMO_MODERNIZACAO.md`

---

**Boa sorte na modernização dos demais templates! 🚀**
