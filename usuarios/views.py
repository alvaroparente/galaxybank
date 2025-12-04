from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from decimal import Decimal
from datetime import date, datetime, timedelta
from .models import Cliente, Gerente, Transacao
from .forms import RegistroUsuarioForm, RegistroClienteForm, RegistroSenhaForm

User = get_user_model()

@csrf_protect
def login_view(request):
    """View para login do usuário"""
    if request.user.is_authenticated:
        return redirect_user_by_type(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo(a), {user.first_name}!')
                return redirect_user_by_type(user)
            else:
                messages.error(request, 'Credenciais inválidas. Tente novamente.')
        else:
            messages.error(request, 'Por favor, preencha todos os campos.')
    
    return render(request, 'usuarios/login.html')

def logout_view(request):
    """View para logout do usuário"""
    logout(request)
    messages.info(request, 'Você foi desconectado com sucesso.')
    return redirect('usuarios:login')

def redirect_user_by_type(user):
    """Redireciona o usuário baseado no seu tipo"""
    if user.tipo_usuario == 'cliente':
        return redirect('usuarios:dashboard_cliente')
    elif user.tipo_usuario == 'gerente':
        return redirect('usuarios:dashboard_gerente')
    else:
        return redirect('usuarios:login')

@login_required
def dashboard_cliente(request):
    """Dashboard do cliente"""
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        
        # Buscar últimas transações
        ultimas_transacoes = cliente.transacoes_origem.order_by('-data_transacao')[:5]
        
        # Estatísticas do mês atual
        inicio_mes = date.today().replace(day=1)
        transacoes_mes = cliente.transacoes_origem.filter(data_transacao__gte=inicio_mes)
        
        total_gastos_mes = sum(t.valor for t in transacoes_mes if t.tipo in ['compra', 'transferencia_enviada']) or Decimal('0.00')
        total_recebido_mes = sum(t.valor for t in transacoes_mes if t.tipo in ['deposito', 'transferencia_recebida']) or Decimal('0.00')
        
        context = {
            'cliente': cliente,
            'usuario': request.user,
            'ultimas_transacoes': ultimas_transacoes,
            'total_gastos_mes': total_gastos_mes,
            'total_recebido_mes': total_recebido_mes,
        }
        return render(request, 'usuarios/dashboard_cliente.html', context)
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:login')

@login_required
def dashboard_gerente(request):
    """Dashboard do gerente"""
    try:
        gerente = Gerente.objects.get(usuario=request.user)
        
        # Estatísticas dinâmicas
        total_clientes = Cliente.objects.count()
        total_credito_aprovado = sum(c.limite_credito for c in Cliente.objects.filter(limite_credito_aprovado=True))
        
        # Crescimento mensal
        inicio_mes = date.today().replace(day=1)
        novos_clientes_mes = Cliente.objects.filter(usuario__date_joined__gte=inicio_mes).count()
        
        # Solicitações pendentes de crédito
        from credito.models import SolicitacaoCredito
        solicitacoes_pendentes = SolicitacaoCredito.objects.filter(status='pendente').count()
        
        context = {
            'gerente': gerente,
            'usuario': request.user,
            'total_clientes': total_clientes,
            'total_credito_aprovado': total_credito_aprovado,
            'novos_clientes_mes': novos_clientes_mes,
            'solicitacoes_pendentes': solicitacoes_pendentes,
        }
        return render(request, 'usuarios/dashboard_gerente.html', context)
    except Gerente.DoesNotExist:
        messages.error(request, 'Perfil de gerente não encontrado.')
        return redirect('usuarios:login')

def home_redirect(request):
    """Redireciona para o dashboard apropriado ou login"""
    if request.user.is_authenticated:
        return redirect_user_by_type(request.user)
    return redirect('usuarios:login')

# ===== VIEWS DE REGISTRO =====

@csrf_protect
def registro_etapa1(request):
    """Primeira etapa do registro: dados básicos do usuário"""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            # Salvar dados na sessão
            request.session['registro_etapa1'] = form.cleaned_data
            return redirect('usuarios:registro_etapa2')
    else:
        # Preencher com dados da sessão se existirem
        initial_data = request.session.get('registro_etapa1', {})
        form = RegistroUsuarioForm(initial=initial_data)
    
    context = {
        'form': form,
        'etapa_atual': 1,
        'total_etapas': 3,
        'titulo': 'Dados Pessoais',
        'subtitulo': 'Vamos começar com suas informações básicas'
    }
    return render(request, 'usuarios/registro_etapa1.html', context)

@csrf_protect
def registro_etapa2(request):
    """Segunda etapa do registro: dados específicos do cliente"""
    # Verificar se etapa 1 foi concluída
    if 'registro_etapa1' not in request.session:
        messages.warning(request, 'Complete a primeira etapa do cadastro.')
        return redirect('usuarios:registro_etapa1')
    
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            # Salvar dados na sessão
            request.session['registro_etapa2'] = form.cleaned_data
            return redirect('usuarios:registro_etapa3')
    else:
        # Preencher com dados da sessão se existirem
        initial_data = request.session.get('registro_etapa2', {})
        form = RegistroClienteForm(initial=initial_data)
    
    context = {
        'form': form,
        'etapa_atual': 2,
        'total_etapas': 3,
        'titulo': 'Dados do Cliente',
        'subtitulo': 'Agora precisamos de algumas informações específicas'
    }
    return render(request, 'usuarios/registro_etapa2.html', context)

@csrf_protect
def registro_etapa3(request):
    """Terceira etapa do registro: criação de username e senha"""
    # Verificar se etapas anteriores foram concluídas
    if 'registro_etapa1' not in request.session or 'registro_etapa2' not in request.session:
        messages.warning(request, 'Complete as etapas anteriores do cadastro.')
        return redirect('usuarios:registro_etapa1')
    
    if request.method == 'POST':
        form = RegistroSenhaForm(request.POST)
        if form.is_valid():
            try:
                # Recuperar dados das sessões
                dados_etapa1 = request.session['registro_etapa1']
                dados_etapa2 = request.session['registro_etapa2']
                dados_etapa3 = form.cleaned_data
                
                # Criar usuário
                user = User.objects.create_user(
                    username=dados_etapa3['username'],
                    email=dados_etapa1['email'],
                    password=dados_etapa3['password1'],
                    first_name=dados_etapa1['first_name'],
                    last_name=dados_etapa1['last_name'],
                    telefone=dados_etapa1['telefone'],
                    tipo_usuario='cliente'
                )
                
                # Criar perfil de cliente
                Cliente.objects.create(
                    usuario=user,
                    cpf=dados_etapa2['cpf'],
                    score_pontos=100  # Pontos iniciais
                )
                
                # Limpar sessão
                del request.session['registro_etapa1']
                del request.session['registro_etapa2']
                
                # Fazer login automático
                user = authenticate(
                    request, 
                    username=dados_etapa3['username'], 
                    password=dados_etapa3['password1']
                )
                if user:
                    login(request, user)
                    messages.success(request, f'Bem-vindo ao Galaxy Bank, {user.first_name}! Sua conta foi criada com sucesso.')
                    return redirect('usuarios:dashboard_cliente')
                else:
                    messages.success(request, 'Conta criada com sucesso! Faça login para acessar sua conta.')
                    return redirect('usuarios:login')
                    
            except Exception as e:
                messages.error(request, f'Erro ao criar conta: {str(e)}')
    else:
        form = RegistroSenhaForm()
    
    context = {
        'form': form,
        'etapa_atual': 3,
        'total_etapas': 3,
        'titulo': 'Acesso à Conta',
        'subtitulo': 'Por último, escolha suas credenciais de acesso'
    }
    return render(request, 'usuarios/registro_etapa3.html', context)

def registro_cancelar(request):
    """Cancelar registro e limpar sessão"""
    # Limpar dados do registro da sessão
    keys_to_remove = ['registro_etapa1', 'registro_etapa2', 'registro_etapa3']
    for key in keys_to_remove:
        if key in request.session:
            del request.session[key]
    
    messages.info(request, 'Cadastro cancelado.')
    return redirect('usuarios:login')

# ===== VIEWS DE PERFIL =====

@login_required
def perfil_view(request):
    """View para exibir o perfil do usuário"""
    try:
        if request.user.tipo_usuario == 'cliente':
            cliente = Cliente.objects.get(usuario=request.user)
            context = {
                'usuario': request.user,
                'perfil_especifico': cliente,
                'tipo_usuario': 'cliente',
            }
        elif request.user.tipo_usuario == 'gerente':
            gerente = Gerente.objects.get(usuario=request.user)
            context = {
                'usuario': request.user,
                'perfil_especifico': gerente,
                'tipo_usuario': 'gerente',
            }
        else:
            messages.error(request, 'Tipo de usuário não reconhecido.')
            return redirect('usuarios:login')
            
        return render(request, 'usuarios/perfil.html', context)
    except (Cliente.DoesNotExist, Gerente.DoesNotExist):
        messages.error(request, 'Perfil não encontrado.')
        return redirect('usuarios:login')

@login_required
@csrf_protect
def perfil_editar(request):
    """View para editar o perfil do usuário"""
    from .forms import PerfilUsuarioForm, PerfilClienteForm, PerfilGerenteForm
    
    try:
        if request.user.tipo_usuario == 'cliente':
            cliente = Cliente.objects.get(usuario=request.user)
            perfil_especifico = cliente
            PerfilEspecificoForm = PerfilClienteForm
        elif request.user.tipo_usuario == 'gerente':
            gerente = Gerente.objects.get(usuario=request.user)
            perfil_especifico = gerente
            PerfilEspecificoForm = PerfilGerenteForm
        else:
            messages.error(request, 'Tipo de usuário não reconhecido.')
            return redirect('usuarios:login')
    except (Cliente.DoesNotExist, Gerente.DoesNotExist):
        messages.error(request, 'Perfil não encontrado.')
        return redirect('usuarios:login')
    
    if request.method == 'POST':
        form_usuario = PerfilUsuarioForm(request.POST, instance=request.user)
        form_especifico = PerfilEspecificoForm(request.POST, instance=perfil_especifico)
        
        if form_usuario.is_valid() and form_especifico.is_valid():
            form_usuario.save()
            form_especifico.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('usuarios:perfil')
    else:
        form_usuario = PerfilUsuarioForm(instance=request.user)
        form_especifico = PerfilEspecificoForm(instance=perfil_especifico)
    
    context = {
        'form_usuario': form_usuario,
        'form_especifico': form_especifico,
        'usuario': request.user,
        'perfil_especifico': perfil_especifico,
        'tipo_usuario': request.user.tipo_usuario,
    }
    
    return render(request, 'usuarios/perfil_editar.html', context)

# ===== VIEWS DE TRANSFERÊNCIA E DEPÓSITO =====

@login_required
@csrf_protect
def transferencia(request):
    """View para realizar transferências entre contas"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem realizar transferências.')
        return redirect('usuarios:dashboard_cliente')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:login')
    
    if request.method == 'POST':
        destinatario_cpf = request.POST.get('destinatario_cpf', '').strip()
        valor_str = request.POST.get('valor', '').replace(',', '.').strip()
        descricao = request.POST.get('descricao', '').strip()
        
        if not all([destinatario_cpf, valor_str]):
            messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
            return render(request, 'usuarios/transferencia.html', {'cliente': cliente})
        
        try:
            valor = Decimal(valor_str)
            if valor <= 0:
                raise ValueError("Valor deve ser positivo")
        except (ValueError, TypeError):
            messages.error(request, 'Valor inválido. Use formato: 123.45')
            return render(request, 'usuarios/transferencia.html', {'cliente': cliente})
        
        if valor > cliente.saldo:
            messages.error(request, 'Saldo insuficiente para realizar a transferência.')
            return render(request, 'usuarios/transferencia.html', {'cliente': cliente})
        
        try:
            destinatario = Cliente.objects.get(cpf=destinatario_cpf)
            if destinatario == cliente:
                messages.error(request, 'Não é possível transferir para sua própria conta.')
                return render(request, 'usuarios/transferencia.html', {'cliente': cliente})
        except Cliente.DoesNotExist:
            messages.error(request, 'Destinatário não encontrado. Verifique o CPF.')
            return render(request, 'usuarios/transferencia.html', {'cliente': cliente})
        
        # Realizar transferência
        with transaction.atomic():
            # Debitar do remetente
            cliente.saldo -= valor
            cliente.save()
            
            # Creditar ao destinatário
            destinatario.saldo += valor
            destinatario.save()
            
            # Registrar transações
            Transacao.objects.create(
                cliente=cliente,
                tipo='transferencia_enviada',
                valor=valor,
                descricao=f'Transferência para {destinatario.usuario.first_name} ({destinatario.cpf}) - {descricao}' if descricao else f'Transferência para {destinatario.usuario.first_name} ({destinatario.cpf})',
                destinatario=destinatario
            )
            
            Transacao.objects.create(
                cliente=destinatario,
                tipo='transferencia_recebida',
                valor=valor,
                descricao=f'Transferência de {cliente.usuario.first_name} ({cliente.cpf}) - {descricao}' if descricao else f'Transferência de {cliente.usuario.first_name} ({cliente.cpf})',
                origem=cliente
            )
        
        messages.success(request, f'Transferência de R$ {valor:.2f} realizada com sucesso para {destinatario.usuario.first_name}!')
        return redirect('usuarios:dashboard_cliente')
    
    context = {
        'cliente': cliente,
    }
    return render(request, 'usuarios/transferencia.html', context)

@login_required
@csrf_protect
def deposito(request):
    """View para realizar depósitos na conta"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem realizar depósitos.')
        return redirect('usuarios:dashboard_cliente')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:login')
    
    if request.method == 'POST':
        valor_str = request.POST.get('valor', '').replace(',', '.').strip()
        descricao = request.POST.get('descricao', '').strip()
        
        if not valor_str:
            messages.error(request, 'O valor do depósito é obrigatório.')
            return render(request, 'usuarios/deposito.html', {'cliente': cliente})
        
        try:
            valor = Decimal(valor_str)
            if valor <= 0:
                raise ValueError("Valor deve ser positivo")
            if valor > Decimal('10000.00'):
                messages.error(request, 'O valor máximo para depósito é R$ 10.000,00.')
                return render(request, 'usuarios/deposito.html', {'cliente': cliente})
        except (ValueError, TypeError):
            messages.error(request, 'Valor inválido. Use formato: 123.45')
            return render(request, 'usuarios/deposito.html', {'cliente': cliente})
        
        # Realizar depósito
        with transaction.atomic():
            cliente.saldo += valor
            cliente.save()
            
            # Registrar transação
            Transacao.objects.create(
                cliente=cliente,
                tipo='deposito',
                valor=valor,
                descricao=f'Depósito - {descricao}' if descricao else 'Depósito'
            )
        
        messages.success(request, f'Depósito de R$ {valor:.2f} realizado com sucesso!')
        return redirect('usuarios:dashboard_cliente')
    
    context = {
        'cliente': cliente,
    }
    return render(request, 'usuarios/deposito.html', context)

@login_required
def extrato(request):
    """View para visualizar o extrato de transações"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem visualizar o extrato.')
        return redirect('usuarios:dashboard_cliente')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:login')
    
    # Filtros
    periodo = request.GET.get('periodo', '30')  # últimos 30 dias por padrão
    tipo_filtro = request.GET.get('tipo', 'todas')
    
    # Calcular data inicial
    if periodo == '7':
        data_inicial = date.today() - timedelta(days=7)
    elif periodo == '30':
        data_inicial = date.today() - timedelta(days=30)
    elif periodo == '90':
        data_inicial = date.today() - timedelta(days=90)
    else:
        data_inicial = date.today() - timedelta(days=30)
    
    # Buscar transações
    transacoes = cliente.transacoes_origem.filter(data_transacao__gte=data_inicial)
    
    if tipo_filtro != 'todas':
        transacoes = transacoes.filter(tipo=tipo_filtro)
    
    transacoes = transacoes.order_by('-data_transacao')
    
    # Estatísticas do período
    total_entrada = sum(t.valor for t in transacoes if t.tipo in ['deposito', 'transferencia_recebida'])
    total_saida = sum(t.valor for t in transacoes if t.tipo in ['transferencia_enviada', 'compra'])
    
    context = {
        'cliente': cliente,
        'transacoes': transacoes,
        'periodo_selecionado': periodo,
        'tipo_selecionado': tipo_filtro,
        'total_entrada': total_entrada,
        'total_saida': total_saida,
        'saldo_periodo': total_entrada - total_saida,
    }
    return render(request, 'usuarios/extrato.html', context)
