from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from .models import Cliente, Gerente
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
        context = {
            'cliente': cliente,
            'usuario': request.user,
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
        context = {
            'gerente': gerente,
            'usuario': request.user,
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
