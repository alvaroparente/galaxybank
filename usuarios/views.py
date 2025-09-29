from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from .models import Cliente, Gerente

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
    return redirect('login')

def redirect_user_by_type(user):
    """Redireciona o usuário baseado no seu tipo"""
    if user.tipo_usuario == 'cliente':
        return redirect('dashboard_cliente')
    elif user.tipo_usuario == 'gerente':
        return redirect('dashboard_gerente')
    else:
        return redirect('login')

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
        return redirect('login')

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
        return redirect('login')

def home_redirect(request):
    """Redireciona para o dashboard apropriado ou login"""
    if request.user.is_authenticated:
        return redirect_user_by_type(request.user)
    return redirect('login')
