from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from .models import SolicitacaoCredito, HistoricoCredito
from usuarios.models import Cliente, Gerente
from .forms import SolicitacaoCreditoForm
from decimal import Decimal

@login_required
def solicitar_credito(request):
    """Cliente solicita limite de crédito"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem solicitar crédito.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        
        # Verificar se já tem solicitação pendente
        solicitacao_pendente = SolicitacaoCredito.objects.filter(
            cliente=cliente, 
            status='pendente'
        ).first()
        
        if solicitacao_pendente:
            messages.warning(request, 'Você já possui uma solicitação pendente de análise.')
            return redirect('credito:minhas_solicitacoes')
        
        if request.method == 'POST':
            form = SolicitacaoCreditoForm(request.POST)
            if form.is_valid():
                solicitacao = form.save(commit=False)
                solicitacao.cliente = cliente
                solicitacao.save()
                
                messages.success(request, 'Solicitação de crédito enviada com sucesso! Aguarde a análise do gerente.')
                return redirect('credito:minhas_solicitacoes')
        else:
            form = SolicitacaoCreditoForm()
        
        context = {
            'form': form,
            'cliente': cliente,
        }
        
        return render(request, 'credito/solicitar.html', context)
        
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:home_redirect')

@login_required
def minhas_solicitacoes(request):
    """Lista solicitações de crédito do cliente"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem ver solicitações.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        solicitacoes = cliente.solicitacoes_credito.all()
        
        # Paginação
        paginator = Paginator(solicitacoes, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'cliente': cliente,
        }
        
        return render(request, 'credito/minhas_solicitacoes.html', context)
        
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:home_redirect')

@login_required
def historico_credito(request):
    """Histórico de uso do crédito do cliente"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem ver histórico.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        historico = cliente.historico_credito.all()
        
        # Paginação
        paginator = Paginator(historico, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'cliente': cliente,
        }
        
        return render(request, 'credito/historico.html', context)
        
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:home_redirect')

# ===== VIEWS DO GERENTE =====

@login_required
def avaliar_solicitacoes(request):
    """Gerente avalia solicitações de crédito"""
    if request.user.tipo_usuario != 'gerente':
        messages.error(request, 'Apenas gerentes podem avaliar solicitações.')
        return redirect('usuarios:home_redirect')
    
    try:
        gerente = Gerente.objects.get(usuario=request.user)
        
        # Filtros
        status_filter = request.GET.get('status', '')
        ordenar = request.GET.get('ordenar', '')
        
        # Buscar solicitações
        if status_filter == 'pendente':
            solicitacoes = SolicitacaoCredito.objects.filter(status='pendente')
        else:
            solicitacoes = SolicitacaoCredito.objects.all()
        
        # Ordenação
        if ordenar == 'valor_desc':
            solicitacoes = solicitacoes.order_by('-valor_solicitado')
        elif ordenar == 'valor_asc':
            solicitacoes = solicitacoes.order_by('valor_solicitado')
        elif ordenar == 'data_desc':
            solicitacoes = solicitacoes.order_by('-data_solicitacao')
        else:
            solicitacoes = solicitacoes.order_by('data_solicitacao')
        
        # Adicionar análise de risco para cada solicitação
        for solicitacao in solicitacoes:
            if solicitacao.renda_mensal and solicitacao.renda_mensal > 0:
                percentual = (float(solicitacao.valor_solicitado) / float(solicitacao.renda_mensal)) * 100
                solicitacao.percentual_renda = round(percentual, 1)
                if percentual <= 30:
                    solicitacao.nivel_risco = 'baixo'
                elif percentual <= 60:
                    solicitacao.nivel_risco = 'medio'
                else:
                    solicitacao.nivel_risco = 'alto'
            else:
                solicitacao.percentual_renda = 0
                solicitacao.nivel_risco = 'indeterminado'
        
        # Estatísticas
        pendentes_count = SolicitacaoCredito.objects.filter(status='pendente').count()
        hoje = timezone.now().date()
        aprovadas_count = SolicitacaoCredito.objects.filter(
            status='aprovada', 
            data_avaliacao__date=hoje
        ).count()
        rejeitadas_count = SolicitacaoCredito.objects.filter(
            status='reprovada', 
            data_avaliacao__date=hoje
        ).count()
        total_valor = sum(s.valor_solicitado for s in SolicitacaoCredito.objects.filter(status='pendente'))
        
        # Paginação
        paginator = Paginator(solicitacoes, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'solicitacoes': page_obj,
            'page_obj': page_obj,
            'gerente': gerente,
            'pendentes_count': pendentes_count,
            'aprovadas_count': aprovadas_count,
            'rejeitadas_count': rejeitadas_count,
            'total_valor': total_valor,
        }
        
        return render(request, 'credito/avaliar_solicitacoes.html', context)
        
    except Gerente.DoesNotExist:
        messages.error(request, 'Perfil de gerente não encontrado.')
        return redirect('usuarios:home_redirect')

@login_required
def detalhes_solicitacao(request, solicitacao_id):
    """Detalhes de uma solicitação de crédito para avaliação"""
    if request.user.tipo_usuario != 'gerente':
        messages.error(request, 'Apenas gerentes podem ver detalhes.')
        return redirect('usuarios:home_redirect')
    
    try:
        gerente = Gerente.objects.get(usuario=request.user)
        solicitacao = get_object_or_404(SolicitacaoCredito, id=solicitacao_id)
        
        context = {
            'solicitacao': solicitacao,
            'gerente': gerente,
        }
        
        return render(request, 'credito/detalhes_solicitacao.html', context)
        
    except Gerente.DoesNotExist:
        messages.error(request, 'Perfil de gerente não encontrado.')
        return redirect('usuarios:home_redirect')

@login_required
@csrf_protect
def processar_solicitacao(request, solicitacao_id):
    """Gerente aprova ou reprova solicitação"""
    if request.method != 'POST':
        return redirect('credito:avaliar_solicitacoes')
    
    if request.user.tipo_usuario != 'gerente':
        messages.error(request, 'Apenas gerentes podem processar solicitações.')
        return redirect('usuarios:home_redirect')
    
    try:
        gerente = Gerente.objects.get(usuario=request.user)
        solicitacao = get_object_or_404(SolicitacaoCredito, id=solicitacao_id, status='pendente')
        
        acao = request.POST.get('acao')
        observacoes = request.POST.get('observacoes', '')
        valor_aprovado = request.POST.get('valor_aprovado', '0')
        
        # Debug logging
        print(f"DEBUG: acao={acao}, valor_aprovado={valor_aprovado}, observacoes={observacoes}")
        
        with transaction.atomic():
            if acao == 'aprovar':
                print(f"DEBUG: Entering approval block")
                try:
                    # Se não foi fornecido valor, usar o valor solicitado
                    if not valor_aprovado or valor_aprovado == '0':
                        valor_aprovado = solicitacao.valor_solicitado
                    else:
                        # Handle Brazilian decimal format (comma as decimal separator)
                        valor_aprovado = valor_aprovado.replace(',', '.')
                        valor_aprovado = Decimal(valor_aprovado)
                    
                    if valor_aprovado <= 0:
                        raise ValueError("Valor deve ser maior que zero")
                    
                    # Atualizar solicitação
                    solicitacao.status = 'aprovada'
                    solicitacao.gerente_responsavel = gerente
                    solicitacao.data_avaliacao = timezone.now()
                    solicitacao.observacoes_gerente = observacoes
                    solicitacao.valor_aprovado = valor_aprovado
                    solicitacao.save()
                    
                    # Atualizar limite do cliente
                    cliente = solicitacao.cliente
                    cliente.limite_credito = valor_aprovado
                    cliente.limite_credito_aprovado = True
                    cliente.save()
                    
                    # Registrar no histórico
                    saldo_anterior = cliente.limite_credito if cliente.limite_credito_aprovado else Decimal('0')
                    HistoricoCredito.objects.create(
                        cliente=cliente,
                        tipo_operacao='ajuste',
                        valor=valor_aprovado,
                        saldo_anterior=saldo_anterior,
                        saldo_posterior=valor_aprovado,
                        descricao=f'Limite aprovado pelo gerente {gerente.usuario.first_name}'
                    )
                    
                    messages.success(request, f'Solicitação aprovada com limite de R$ {valor_aprovado}!')
                    print(f"DEBUG: Successfully approved credit request for {valor_aprovado}")
                    
                except (ValueError, TypeError) as e:
                    print(f"DEBUG: Error converting valor_aprovado: {e}")
                    messages.error(request, f'Valor aprovado inválido: {str(e)}')
                    return redirect('credito:detalhes_solicitacao', solicitacao_id=solicitacao_id)
                
            elif acao == 'rejeitar':
                # Atualizar solicitação
                solicitacao.status = 'reprovada'
                solicitacao.gerente_responsavel = gerente
                solicitacao.data_avaliacao = timezone.now()
                solicitacao.observacoes_gerente = observacoes
                solicitacao.save()
                
                messages.success(request, 'Solicitação reprovada.')
            
            else:
                messages.error(request, 'Ação inválida.')
                return redirect('credito:detalhes_solicitacao', solicitacao_id=solicitacao_id)
        
        return redirect('credito:avaliar_solicitacoes')
        
    except Gerente.DoesNotExist:
        messages.error(request, 'Perfil de gerente não encontrado.')
        return redirect('usuarios:home_redirect')
    except Exception as e:
        messages.error(request, 'Erro ao processar solicitação.')
        return redirect('credito:avaliar_solicitacoes')

@login_required
def solicitacoes_avaliadas(request):
    """Lista solicitações já avaliadas pelo gerente"""
    if request.user.tipo_usuario != 'gerente':
        messages.error(request, 'Apenas gerentes podem ver avaliações.')
        return redirect('usuarios:home_redirect')
    
    try:
        gerente = Gerente.objects.get(usuario=request.user)
        
        # Buscar solicitações avaliadas por este gerente
        solicitacoes = SolicitacaoCredito.objects.filter(
            gerente_responsavel=gerente
        ).exclude(status='pendente').order_by('-data_avaliacao')
        
        # Paginação
        paginator = Paginator(solicitacoes, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'gerente': gerente,
        }
        
        return render(request, 'credito/solicitacoes_avaliadas.html', context)
        
    except Gerente.DoesNotExist:
        messages.error(request, 'Perfil de gerente não encontrado.')
        return redirect('usuarios:home_redirect')
