from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Fatura, ConfiguracaoFatura, PagamentoFatura, criar_fatura_mensal
from usuarios.models import Cliente
from decimal import Decimal
from datetime import date

@login_required
def minhas_faturas(request):
    """Lista faturas do cliente"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem ver faturas.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        faturas = cliente.faturas.all()
        
        # Atualizar status de faturas vencidas
        for fatura in faturas:
            if fatura.esta_vencida and fatura.status == 'fechada':
                fatura.calcular_juros_mora()
        
        # Paginação
        paginator = Paginator(faturas, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'cliente': cliente,
        }
        
        return render(request, 'faturas/minhas_faturas.html', context)
        
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:home_redirect')

@login_required
def detalhes_fatura(request, fatura_id):
    """Detalhes de uma fatura específica"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem ver faturas.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        fatura = get_object_or_404(Fatura, id=fatura_id, cliente=cliente)
        
        # Atualizar juros se vencida
        if fatura.esta_vencida:
            fatura.calcular_juros_mora()
        
        itens = fatura.itens.all()
        pagamentos = fatura.pagamentos.all()
        
        context = {
            'fatura': fatura,
            'itens': itens,
            'pagamentos': pagamentos,
            'cliente': cliente,
        }
        
        return render(request, 'faturas/detalhes_fatura.html', context)
        
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:home_redirect')

@login_required
@csrf_protect
def pagar_fatura(request, fatura_id):
    """Pagar fatura com saldo"""
    if request.method != 'POST':
        return redirect('faturas:detalhes_fatura', fatura_id=fatura_id)
    
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem pagar faturas.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        fatura = get_object_or_404(Fatura, id=fatura_id, cliente=cliente)
        
        if fatura.status == 'paga':
            messages.warning(request, 'Esta fatura já está paga.')
            return redirect('faturas:detalhes_fatura', fatura_id=fatura_id)
        
        # Calcular valor total (incluindo juros se houver)
        if fatura.esta_vencida:
            fatura.calcular_juros_mora()
        
        valor_total = fatura.valor_total + fatura.juros_mora - fatura.valor_pago
        
        if cliente.saldo < valor_total:
            messages.error(request, 'Saldo insuficiente para pagar a fatura.')
            return redirect('faturas:detalhes_fatura', fatura_id=fatura_id)
        
        with transaction.atomic():
            # Debitar do saldo
            cliente.saldo -= valor_total
            cliente.save()
            
            # Registrar pagamento
            pagamento = PagamentoFatura.objects.create(
                fatura=fatura,
                valor_pago=valor_total,
                forma_pagamento='saldo',
                observacoes='Pagamento via saldo'
            )
            
            # Atualizar fatura
            fatura.valor_pago += valor_total
            fatura.status = 'paga'
            fatura.data_pagamento = timezone.now()
            fatura.save()
            
            # Restaurar limite de crédito se aplicável
            if fatura.valor_total > 0:  # Fatura tinha compras no crédito
                # Buscar todas as compras da fatura para restaurar crédito
                for item in fatura.itens.all():
                    if item.compra.forma_pagamento == 'credito':
                        valor_item = item.valor_parcela
                        cliente.limite_credito += valor_item
                
                cliente.save()
        
        messages.success(request, f'Fatura paga com sucesso! Valor: R$ {valor_total:.2f}')
        return redirect('faturas:minhas_faturas')
        
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:home_redirect')
    except Exception as e:
        messages.error(request, 'Erro ao processar pagamento.')
        return redirect('faturas:detalhes_fatura', fatura_id=fatura_id)

@login_required
def configurar_vencimento(request):
    """Configurar dia de vencimento das faturas"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem configurar vencimento.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        config, created = ConfiguracaoFatura.objects.get_or_create(
            cliente=cliente,
            defaults={'dia_vencimento': 10}
        )
        
        if request.method == 'POST':
            novo_dia = int(request.POST.get('dia_vencimento', 10))
            
            if 1 <= novo_dia <= 28:
                config.dia_vencimento = novo_dia
                config.save()
                messages.success(request, f'Dia de vencimento alterado para {novo_dia}.')
                return redirect('faturas:minhas_faturas')
            else:
                messages.error(request, 'Dia deve estar entre 1 e 28.')
        
        context = {
            'config': config,
            'cliente': cliente,
        }
        
        return render(request, 'faturas/configurar_vencimento.html', context)
        
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:home_redirect')

@login_required
def fatura_atual(request):
    """Fatura do mês atual (aberta)"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem ver faturas.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        
        # Buscar ou criar fatura do mês atual
        mes_atual = date.today().replace(day=1)
        fatura = Fatura.objects.filter(cliente=cliente, mes_referencia=mes_atual).first()
        
        if not fatura:
            fatura = criar_fatura_mensal(cliente, mes_atual)
        
        if fatura:
            itens = fatura.itens.all()
            
            context = {
                'fatura': fatura,
                'itens': itens,
                'cliente': cliente,
                'eh_fatura_atual': True,
            }
            
            return render(request, 'faturas/fatura_atual.html', context)
        else:
            messages.info(request, 'Nenhuma fatura encontrada para o mês atual.')
            return redirect('faturas:minhas_faturas')
        
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:home_redirect')
