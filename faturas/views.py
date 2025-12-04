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
        print(f"DEBUG: Cliente encontrado: {cliente}")
        
        # Debug - verificar faturas existentes
        todas_faturas = cliente.faturas.all()
        print(f"DEBUG: Total de faturas do cliente: {todas_faturas.count()}")
        for fatura in todas_faturas:
            print(f"DEBUG: Fatura ID {fatura.id}, Status: {fatura.status}, Mês: {fatura.mes_referencia}")
        
        # Verificar se o cliente tem pelo menos uma fatura (criar fatura atual se não tiver)
        if not todas_faturas.exists():
            from .models import criar_fatura_mensal
            from datetime import date
            mes_atual = date.today().replace(day=1)
            print(f"DEBUG: Criando fatura para mês: {mes_atual}")
            try:
                fatura_atual = criar_fatura_mensal(cliente, mes_atual)
                if fatura_atual:
                    messages.info(request, 'Sua primeira fatura foi criada para o mês atual.')
                    print(f"DEBUG: Fatura criada com ID: {fatura_atual.id}")
                else:
                    print("DEBUG: Fatura não foi criada (já existe)")
            except Exception as e:
                print(f"Erro ao criar fatura inicial: {e}")
                messages.error(request, f'Erro ao criar fatura: {e}')
        
        # Recarregar faturas após possível criação
        todas_faturas = cliente.faturas.all()
        
        # Filtro por status se fornecido
        status_filter = request.GET.get('status', '')
        
        if status_filter:
            faturas = todas_faturas.filter(status=status_filter)
            print(f"DEBUG: Filtrado por status '{status_filter}': {faturas.count()} faturas")
        else:
            faturas = todas_faturas
            print(f"DEBUG: Todas as faturas: {faturas.count()}")
        
        # Atualizar status de faturas vencidas
        for fatura in faturas:
            if hasattr(fatura, 'esta_vencida') and fatura.esta_vencida and fatura.status == 'fechada':
                if hasattr(fatura, 'calcular_juros_mora'):
                    fatura.calcular_juros_mora()
        
        # Calcular estatísticas
        total_pendente = sum(f.valor_total - f.valor_pago for f in todas_faturas if f.status in ['fechada', 'vencida'])
        total_vencido = sum(f.valor_total - f.valor_pago for f in todas_faturas if hasattr(f, 'esta_vencida') and f.esta_vencida and f.status != 'paga')
        total_pago = sum(f.valor_pago for f in todas_faturas)
        faturas_count = todas_faturas.count()
        
        print(f"DEBUG: Estatísticas - Pendente: {total_pendente}, Vencido: {total_vencido}, Pago: {total_pago}, Count: {faturas_count}")
        
        # Paginação
        paginator = Paginator(faturas, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        print(f"DEBUG: Página {page_number}, Objetos na página: {len(page_obj)}")
        
        context = {
            'faturas': page_obj,
            'page_obj': page_obj,
            'cliente': cliente,
            'total_pendente': total_pendente,
            'total_vencido': total_vencido,
            'total_pago': total_pago,
            'faturas_count': faturas_count,
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
def configurar_vencimento(request, fatura_id):
    """Configurar vencimentos de parcelas de uma fatura específica"""
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem configurar vencimento.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        fatura = get_object_or_404(Fatura, id=fatura_id, cliente=cliente)
        
        if request.method == 'POST':
            novo_dia = int(request.POST.get('dia_vencimento', 10))
            
            if 1 <= novo_dia <= 28:
                with transaction.atomic():
                    # Atualizar parcelas pendentes para o novo dia
                    from datetime import date, timedelta
                    hoje = timezone.now().date()
                    
                    parcelas_pendentes = fatura.pagamentos.filter(pago=False, data_vencimento__gte=hoje)
                    for parcela in parcelas_pendentes:
                        # Calcular nova data mantendo mês e ano, mas mudando o dia
                        data_original = parcela.data_vencimento
                        try:
                            nova_data = data_original.replace(day=novo_dia)
                        except ValueError:
                            # Se o dia não existir no mês (ex: 31 em fevereiro), usar o último dia do mês
                            import calendar
                            ultimo_dia = calendar.monthrange(data_original.year, data_original.month)[1]
                            novo_dia_ajustado = min(novo_dia, ultimo_dia)
                            nova_data = data_original.replace(day=novo_dia_ajustado)
                        
                        parcela.data_vencimento = nova_data
                        parcela.save()
                
                messages.success(request, f'Vencimentos das parcelas pendentes ajustados para o dia {novo_dia}.')
                return redirect('faturas:detalhes_fatura', fatura_id=fatura.id)
            else:
                messages.error(request, 'Dia deve estar entre 1 e 28.')
        
        context = {
            'fatura': fatura,
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

@login_required
@csrf_protect
def fechar_fatura(request, fatura_id):
    """Fechar uma fatura aberta"""
    if request.method != 'POST':
        return redirect('faturas:fatura_atual')
    
    if request.user.tipo_usuario != 'cliente':
        messages.error(request, 'Apenas clientes podem fechar faturas.')
        return redirect('usuarios:home_redirect')
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        fatura = get_object_or_404(Fatura, id=fatura_id, cliente=cliente, status='aberta')
        
        data_vencimento_str = request.POST.get('data_vencimento')
        
        if not data_vencimento_str:
            messages.error(request, 'Data de vencimento é obrigatória.')
            return redirect('faturas:fatura_atual')
        
        try:
            from datetime import datetime
            data_vencimento = datetime.strptime(data_vencimento_str, '%Y-%m-%d').date()
            
            if data_vencimento <= fatura.data_emissao:
                messages.error(request, 'Data de vencimento deve ser posterior à data de emissão.')
                return redirect('faturas:fatura_atual')
            
            with transaction.atomic():
                fatura.status = 'fechada'
                fatura.data_fechamento = timezone.now()
                fatura.data_vencimento = data_vencimento
                fatura.save()
                
                messages.success(request, f'Fatura fechada com sucesso! Vencimento: {data_vencimento.strftime("%d/%m/%Y")}')
            
            return redirect('faturas:detalhes_fatura', fatura_id=fatura.id)
            
        except ValueError:
            messages.error(request, 'Data de vencimento inválida.')
            return redirect('faturas:fatura_atual')
        
    except Cliente.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('usuarios:home_redirect')
    except Exception as e:
        messages.error(request, 'Erro ao fechar a fatura.')
        return redirect('faturas:fatura_atual')

@login_required
@csrf_protect
def pagar_fatura_completa(request, fatura_id):
    """Pagar uma fatura completamente usando o saldo"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    if request.user.tipo_usuario != 'cliente':
        return JsonResponse({'success': False, 'message': 'Apenas clientes podem pagar faturas'})
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        fatura = get_object_or_404(Fatura, id=fatura_id, cliente=cliente)
        
        if fatura.status == 'paga':
            return JsonResponse({'success': False, 'message': 'Fatura já está paga'})
        
        if cliente.saldo < fatura.saldo_devedor:
            return JsonResponse({'success': False, 'message': 'Saldo insuficiente'})
        
        with transaction.atomic():
            valor_pagamento = fatura.saldo_devedor
            
            # Debitar do saldo do cliente
            cliente.saldo -= valor_pagamento
            cliente.save()
            
            # Atualizar fatura
            fatura.valor_pago += valor_pagamento
            if fatura.saldo_devedor <= Decimal('0'):
                fatura.status = 'paga'
            fatura.save()
            
            # Marcar parcelas como pagas
            parcelas_pendentes = fatura.pagamentos.filter(pago=False)
            for parcela in parcelas_pendentes:
                parcela.pago = True
                parcela.data_pagamento = timezone.now()
                parcela.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Fatura paga com sucesso! Valor: R$ {valor_pagamento}'
        })
        
    except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Cliente não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Erro ao processar pagamento'})

@login_required
@csrf_protect
def pagar_parcela(request, pagamento_id):
    """Pagar uma parcela específica usando o saldo"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    if request.user.tipo_usuario != 'cliente':
        return JsonResponse({'success': False, 'message': 'Apenas clientes podem pagar parcelas'})
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        pagamento = get_object_or_404(PagamentoFatura, id=pagamento_id, fatura__cliente=cliente)
        
        if pagamento.pago:
            return JsonResponse({'success': False, 'message': 'Parcela já está paga'})
        
        if cliente.saldo < pagamento.valor_parcela:
            return JsonResponse({'success': False, 'message': 'Saldo insuficiente'})
        
        with transaction.atomic():
            # Debitar do saldo do cliente
            cliente.saldo -= pagamento.valor_parcela
            cliente.save()
            
            # Marcar parcela como paga
            pagamento.pago = True
            pagamento.data_pagamento = timezone.now()
            pagamento.save()
            
            # Atualizar fatura
            fatura = pagamento.fatura
            fatura.valor_pago += pagamento.valor_parcela
            if fatura.saldo_devedor <= Decimal('0'):
                fatura.status = 'paga'
            fatura.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Parcela paga com sucesso! Valor: R$ {pagamento.valor_parcela}'
        })
        
    except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Cliente não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Erro ao processar pagamento'})
